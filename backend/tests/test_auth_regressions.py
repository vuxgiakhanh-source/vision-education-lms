import asyncio
from contextlib import contextmanager
from datetime import timedelta
import os
from secrets import randbelow
from threading import Event

import anyio
import httpx
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete, event
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from app.core.enums.user_role import UserRole
from app.core.logger import logger
from app.core.security import create_access_token, hash_password
from app.database.database import engine as local_engine, get_session_factory
from app.main import app
from app.models.student import Student
from app.models.user import User
from app.modules.auth.login import service as login_service
from app.modules.auth.login.router import MAX_CONCURRENT_LOGINS, get_login_limiter, login_router
from app.modules.auth.login.service import get_auth_service


PHONE = "0900000000"
LEGACY_PASSWORD = "old123"


@pytest.fixture
def auth_api(monkeypatch, sqlite_engine):
    engine = sqlite_engine
    with Session(engine) as db:
        db.add(User(
            id=1, full_name="Auth fixture", phone_number=PHONE, role=UserRole.STUDENT,
            hashed_password=hash_password(LEGACY_PASSWORD), must_change_password=True,
        ))
        db.commit()

    session_factory = sessionmaker(bind=engine)
    monkeypatch.setitem(app.dependency_overrides, get_session_factory, lambda: session_factory)
    token = create_access_token({"id": 1}, timedelta(minutes=5))
    with TestClient(app) as client:
        yield client, {"Authorization": f"Bearer {token}"}, engine


def test_phone_is_a_database_constraint(auth_api):
    _, _, engine = auth_api
    with Session(engine) as db:
        db.add(User(
            full_name="Duplicate fixture", phone_number=PHONE, role=UserRole.STUDENT,
            hashed_password="unused",
        ))
        with pytest.raises(IntegrityError):
            db.commit()


@pytest.mark.parametrize("role", [UserRole.TEACHER, UserRole.ADMIN, UserRole.TEACHING_ASSISTANT])
def test_student_schedule_requires_student_role_even_with_profile(auth_api, role):
    client, headers, engine = auth_api
    with Session(engine) as db:
        user = db.get(User, 1)
        user.role = role
        user.must_change_password = False
        db.add(Student(user_id=user.id, grade=12))
        db.commit()

    requests = (
        ("GET", "/schedule/weekly?week_start=2026-11-23", None),
        ("GET", "/schedule/upcoming", None),
        ("GET", "/schedule/temporary-transfers/options", None),
        ("GET", "/schedule/temporary-transfers/pending", None),
        ("GET", "/schedule/permanent-transfers/options", None),
        ("PUT", "/schedule/temporary-transfers/1", {
            "expected_enrollment_id": 1,
            "expected_current_session_id": 1,
            "target_session_id": 2,
            "expected_target_starts_at": "2026-11-23T14:00:00",
            "expected_target_ends_at": "2026-11-23T17:00:00",
        }),
        ("POST", "/schedule/permanent-transfers", {
            "target_class_id": 2,
            "expected_current_enrollment_id": 1,
            "expected_first_session": None,
        }),
        ("PUT", "/schedule/temporary-transfers/1/reconfirm", {
            "target_session_id": 2,
            "expected_target_starts_at": "2026-11-23T14:00:00",
            "expected_target_ends_at": "2026-11-23T17:00:00",
        }),
    )
    for method, path, body in requests:
        response = client.request(method, path, headers=headers, json=body)
        assert response.status_code == 403, f"{method} {path}: {response.text}"
        assert response.json()["detail"] == "Chỉ học sinh mới có quyền truy cập"


@pytest.mark.parametrize("password", ["a" * 73, "é" * 37])
def test_password_over_72_bytes_returns_400_for_both_apis(auth_api, password):
    client, headers, _ = auth_api
    for phone in (PHONE, "0900000001"):
        result = client.post("/login", json={"phone_number": phone, "password": password})
        assert result.status_code == 400
        assert "72 byte" in result.json()["detail"]
    change = client.put("/change-password", headers=headers, json={"new_password": password})
    assert change.status_code == 400
    assert "72 byte" in change.json()["detail"]


def test_existing_short_password_and_new_password_bounds(auth_api):
    client, headers, _ = auth_api
    assert client.post("/login", json={"phone_number": PHONE, "password": LEGACY_PASSWORD}).status_code == 200
    same = client.put("/change-password", headers=headers, json={"new_password": LEGACY_PASSWORD})
    assert same.status_code == 400
    assert same.json()["detail"] == "Mật khẩu mới trùng với mật khẩu cũ"
    short = client.put("/change-password", headers=headers, json={"new_password": "a" * 7})
    assert short.status_code == 400 and "8 ký tự" in short.json()["detail"]

    password = "é" * 36
    assert len(password.encode("utf-8")) == 72
    assert client.put("/change-password", headers=headers, json={"new_password": password}).status_code == 200
    assert client.post("/login", json={"phone_number": PHONE, "password": password}).status_code == 200


def test_saturated_login_admission_keeps_shared_worker_available():
    test_app = FastAPI()
    test_app.include_router(login_router)
    release = Event()

    class BlockingLoginService:
        def login(self, request):
            assert release.wait(timeout=15)
            return {"access_token": "synthetic", "token_type": "bearer", "must_change_password": False}

    @test_app.get("/sync-probe")
    def sync_probe():
        return {"ok": True}

    async def get_test_service():
        return BlockingLoginService()

    test_app.dependency_overrides[get_auth_service] = get_test_service

    async def exercise():
        anyio.to_thread.current_default_thread_limiter().total_tokens = 1
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=test_app), base_url="http://test") as client:
            requests = [
                asyncio.create_task(client.post("/login", json={"phone_number": PHONE, "password": LEGACY_PASSWORD}))
                for _ in range(MAX_CONCURRENT_LOGINS + 2)
            ]
            try:
                limiter = get_login_limiter()
                with anyio.fail_after(5):
                    while limiter.statistics().tasks_waiting < 2:
                        await anyio.sleep(0.01)
                    assert limiter.borrowed_tokens == MAX_CONCURRENT_LOGINS
                    assert (await client.get("/sync-probe")).json() == {"ok": True}
            finally:
                release.set()
                responses = await asyncio.gather(*requests)
            assert all(response.status_code == 200 for response in responses)

    asyncio.run(exercise())


@pytest.mark.skipif(os.getenv("SCHEDULE_MYSQL_TESTS") != "1", reason="requires migrated local MySQL")
def test_mysql_login_returns_connection_before_bcrypt(monkeypatch):
    assert local_engine.dialect.name == "mysql"
    engine = create_engine(local_engine.url, pool_size=1, max_overflow=0)
    session_factory = sessionmaker(bind=engine)
    phone = f"09{randbelow(10**8):08d}"
    user_id = None

    try:
        password_hash = hash_password(LEGACY_PASSWORD)
        with session_factory.begin() as db:
            user = User(
                full_name="Login pool fixture", phone_number=phone, role=UserRole.STUDENT,
                hashed_password=password_hash, must_change_password=True,
            )
            db.add(user)
            db.flush()
            user_id = user.id

        actions = []
        event.listen(engine, "checkout", lambda *_: actions.append("checkout"))
        event.listen(engine, "checkin", lambda *_: actions.append("checkin"))
        verify_password = login_service.verify_password

        def verify_after_checkin(password, hashed_password):
            assert actions == ["checkout", "checkin"]
            assert engine.pool.checkedout() == 0
            actions.append("bcrypt")
            return verify_password(password, hashed_password)

        monkeypatch.setattr(login_service, "verify_password", verify_after_checkin)
        monkeypatch.setitem(app.dependency_overrides, get_session_factory, lambda: session_factory)

        with TestClient(app) as client:
            # Bất biến cần giữ: KHÔNG giữ kết nối trong lúc bcrypt chạy (đã kiểm trong verify_after_checkin).
            # Đăng nhập sai còn ghi bộ đếm giới hạn sau bcrypt: mượn rồi trả ngay, pool_size=1 không bị kẹt.
            for password, expected_status, expected_actions in (
                (LEGACY_PASSWORD, 200, ["checkout", "checkin", "bcrypt"]),
                ("incorrect-password", 401, ["checkout", "checkin", "bcrypt", "checkout", "checkin"]),
            ):
                actions.clear()
                response = client.post("/login", json={"phone_number": phone, "password": password})
                assert response.status_code == expected_status, response.text
                assert actions == expected_actions
                assert engine.pool.checkedout() == 0
                if expected_status == 200:
                    assert response.json()["must_change_password"] is True
                    assert response.json()["access_token"]
    finally:
        try:
            if user_id is not None:
                with engine.begin() as conn:
                    conn.execute(delete(User).where(User.id == user_id))
        finally:
            engine.dispose()


@contextmanager
def capture_errors(messages):
    sink = logger.add(messages.append, level="ERROR", diagnose=False)
    try:
        yield
    finally:
        logger.remove(sink)


def test_unhandled_exception_is_logged_without_its_private_message(monkeypatch):
    secret = "synthetic-private-value"

    def broken_dependency():
        raise RuntimeError(secret)

    monkeypatch.setitem(app.dependency_overrides, get_auth_service, broken_dependency)
    messages = []
    with capture_errors(messages), TestClient(app) as client:
        response = client.post("/login", json={"phone_number": PHONE, "password": secret})
    assert response.status_code == 500
    assert secret not in response.text
    assert any("RuntimeError" in message and "POST /login" in message for message in messages)
    assert all(secret not in message for message in messages)
