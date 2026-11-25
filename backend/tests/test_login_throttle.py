from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.core import clock
from app.core.enums.user_role import UserRole
from app.database.database import get_session_factory
from app.main import app
from app.models.user import User
from app.modules.auth.login import service as login_service
from app.modules.auth.login.exceptions import (
    TooManyLoginAttemptsException,
    UserNotFoundException,
    WrongPasswordException,
)
from app.modules.auth.login.repository import LoginRepository
from app.modules.auth.login.schemas import LoginRequest
from app.modules.auth.login.service import COOLDOWN, MAX_FAILED_ATTEMPTS, LoginService

PHONE = "0911111111"
T0 = datetime(2026, 11, 24, 8, 0, 0)


@pytest.fixture
def env(sqlite_engine, monkeypatch):
    """Người dùng thật trong SQLite, bcrypt thay bằng so sánh chuỗi để test nhanh, đồng hồ do test điều khiển."""
    with Session(sqlite_engine) as db:
        db.add(User(
            id=1, full_name="Throttle", phone_number=PHONE, hashed_password="good",
            role=UserRole.STUDENT, must_change_password=False, updated_at=datetime(2020, 1, 1),
        ))
        db.commit()

    calls = []
    monkeypatch.setattr(login_service, "verify_password", lambda password, hashed: calls.append(password) or password == hashed)
    clock_state = {"now": T0}
    monkeypatch.setattr(clock, "center_local_now", lambda: clock_state["now"])

    factory = sessionmaker(bind=sqlite_engine)
    service = LoginService(LoginRepository(factory))

    class Env:
        pass

    e = Env()
    e.service, e.calls, e.clock, e.engine, e.factory = service, calls, clock_state, sqlite_engine, factory
    e.attempt = lambda password, phone=PHONE: service.login(LoginRequest(phone_number=phone, password=password))

    def row():
        with Session(sqlite_engine) as db:
            return db.execute(select(User.failed_login_count, User.last_failed_login_at, User.updated_at)).one()

    e.row = row
    yield e
    app.dependency_overrides.clear()


def fail_attempt(env):
    with pytest.raises(WrongPasswordException) as wrong:
        env.attempt("wrong")
    # Qua HTTP, router ghi việc này SAU khi đã trả lời (xem test cuối file).
    env.service.record_failed_login(wrong.value.user_id)


def fail_times(env, count):
    for _ in range(count):
        fail_attempt(env)


def test_account_is_throttled_after_ten_failures_and_bcrypt_is_skipped(env):
    fail_times(env, MAX_FAILED_ATTEMPTS)
    bcrypt_calls = len(env.calls)
    with pytest.raises(TooManyLoginAttemptsException) as blocked:
        env.attempt("good")  # kể cả mật khẩu đúng cũng bị chặn trong thời gian chờ
    assert 1 <= blocked.value.retry_after_seconds <= COOLDOWN.total_seconds()
    assert len(env.calls) == bcrypt_calls


def test_nine_failures_do_not_block(env):
    fail_times(env, MAX_FAILED_ATTEMPTS - 1)
    assert env.attempt("good").access_token


def test_login_returns_role_for_direct_dashboard_navigation(env):
    app.dependency_overrides[get_session_factory] = lambda: env.factory
    with TestClient(app) as client:
        response = client.post("/login", json={"phone_number": PHONE, "password": "good"})
    assert response.status_code == 200
    assert response.json()["role"] == "student"


def test_correct_password_after_cooldown_works_and_resets_the_counter(env):
    fail_times(env, MAX_FAILED_ATTEMPTS)
    env.clock["now"] = T0 + COOLDOWN + timedelta(seconds=1)
    assert env.attempt("good").access_token
    assert env.row().failed_login_count == 0
    assert env.row().last_failed_login_at is None


def test_wrong_password_after_cooldown_blocks_again_at_once(env):
    fail_times(env, MAX_FAILED_ATTEMPTS)
    env.clock["now"] = T0 + COOLDOWN + timedelta(seconds=1)
    fail_attempt(env)
    with pytest.raises(TooManyLoginAttemptsException):
        env.attempt("good")


def test_failures_older_than_the_window_start_counting_again(env):
    fail_times(env, MAX_FAILED_ATTEMPTS - 1)
    env.clock["now"] = T0 + timedelta(minutes=11)
    fail_times(env, 1)
    assert env.row().failed_login_count == 1


def test_failed_login_does_not_change_updated_at(env):
    fail_times(env, 2)
    assert env.row().updated_at == datetime(2020, 1, 1)
    assert env.row().failed_login_count == 2


def test_unknown_phone_is_never_throttled(env):
    for _ in range(MAX_FAILED_ATTEMPTS + 3):
        with pytest.raises(UserNotFoundException):
            env.attempt("whatever", phone="0922222222")


def test_http_returns_429_with_retry_after(env):
    app.dependency_overrides[get_session_factory] = lambda: env.factory
    client = TestClient(app)
    body = {"phone_number": PHONE, "password": "wrong"}
    for _ in range(MAX_FAILED_ATTEMPTS):
        assert client.post("/login", json=body).status_code == 401
    response = client.post("/login", json=body)
    assert response.status_code == 429
    assert 1 <= int(response.headers["Retry-After"]) <= 60
    assert "thử lại sau" in response.json()["detail"]


def test_service_does_not_write_inline_so_timing_matches_an_unknown_phone(env):
    """Lần ghi MySQL mất ~240 ms. Nếu nằm trong đường trả lời, sai mật khẩu chậm hơn số lạ và lộ ai có tài khoản."""
    with pytest.raises(WrongPasswordException):
        env.attempt("wrong")
    assert env.row().failed_login_count == 0


def test_http_records_the_failure_after_responding(env):
    app.dependency_overrides[get_session_factory] = lambda: env.factory
    client = TestClient(app)
    assert client.post("/login", json={"phone_number": PHONE, "password": "wrong"}).status_code == 401
    assert env.row().failed_login_count == 1
