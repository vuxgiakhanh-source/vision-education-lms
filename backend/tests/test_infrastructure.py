"""Kiểm tra hạ tầng chung: cấu hình, health, pool, phiên DB, log."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from app.core import config as config_module
from app.core.base import Base
from app.core.config import ConfigurationError, Settings
from app.database.database import DbSession, engine, get_db, get_session_factory
from app.main import app


@pytest.fixture
def client():
    yield TestClient(app)
    app.dependency_overrides.clear()


def use_engine(db_engine):
    factory = sessionmaker(bind=db_engine)
    app.dependency_overrides[get_session_factory] = lambda: factory


def test_liveness_does_not_need_the_database(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readiness_ok_when_database_answers(client, sqlite_engine):
    use_engine(sqlite_engine)
    assert client.get("/health/ready").json() == {"status": "ready"}


def test_readiness_503_when_database_is_down(client):
    broken = create_engine("sqlite:////nonexistent-dir/none.db")
    use_engine(broken)
    response = client.get("/health/ready")
    assert response.status_code == 503
    assert "sqlite" not in response.text.lower()  # không lộ chi tiết lỗi ra ngoài


def test_all_models_are_registered_on_base_metadata():
    """Lỗi từng gặp: model mới không được import nên Alembic không thấy bảng."""
    import app.models  # noqa: F401

    tables = set(Base.metadata.tables)
    assert {"users", "students", "classes", "class_enrollments", "class_sessions",
            "session_attendances", "sessions_transfers"} <= tables


def test_models_package_imports_every_module_in_the_folder():
    from pathlib import Path

    import app.models as models_package

    folder = Path(models_package.__file__).parent
    modules = {p.stem for p in folder.glob("*.py") if p.stem != "__init__"}
    imported = {name for name in modules if hasattr(models_package, name)}
    assert modules == imported, f"Thêm vào app/models/__init__.py: {sorted(modules - imported)}"


def test_database_session_closes_before_the_response_is_sent(client, sqlite_engine):
    """DbSession dùng scope='function': session đóng trước byte cuối của phản hồi."""
    use_engine(sqlite_engine)
    events = []
    factory = sessionmaker(bind=sqlite_engine)

    class RecordingSession:
        def __enter__(self):
            self.inner = factory()
            events.append("open")
            return self.inner

        def __exit__(self, *exc):
            self.inner.close()
            events.append("closed")

    app.dependency_overrides[get_session_factory] = lambda: (lambda: RecordingSession())

    @app.get("/_test/session-order")
    def endpoint(db: DbSession):
        events.append("endpoint")
        return {"ok": True}

    class Spy:
        def __init__(self, inner):
            self.inner = inner

        async def __call__(self, scope, receive, send):
            async def spy_send(message):
                if message["type"] == "http.response.body" and not message.get("more_body"):
                    events.append("last-byte-sent")
                await send(message)

            await self.inner(scope, receive, spy_send)

    try:
        assert TestClient(Spy(app)).get("/_test/session-order").status_code == 200
    finally:
        app.router.routes[:] = [r for r in app.router.routes if getattr(r, "path", "") != "/_test/session-order"]
    assert events == ["open", "endpoint", "closed", "last-byte-sent"]


def test_engine_pool_is_configured_explicitly():
    pool = engine.pool
    assert pool.size() == config_module.settings.db_pool_size
    assert pool._max_overflow == config_module.settings.db_max_overflow
    assert pool._timeout == config_module.settings.db_pool_timeout


def test_database_url_escapes_special_characters_in_password(monkeypatch):
    monkeypatch.setenv("MYSQL_PASSWORD", "p@ss:w/rd%1")
    url = create_engine(Settings().database_url).url
    assert url.password == "p@ss:w/rd%1"


def test_default_database_host_is_ipv4_loopback(monkeypatch):
    """Windows: "localhost" thử ::1 trước và mỗi kết nối chờ thêm ~2 giây (đã đo)."""
    monkeypatch.delenv("MYSQL_HOST", raising=False)
    assert Settings().mysql_host == "127.0.0.1"


@pytest.mark.parametrize(
    "name, value, message",
    [
        ("SECRET_KEY", "short", "ít nhất 32"),
        ("SECRET_KEY", "", "Thiếu biến môi trường SECRET_KEY"),
        ("ACCESS_TOKEN_EXPIRE_MINUTES", "abc", "phải là số nguyên"),
        ("ACCESS_TOKEN_EXPIRE_MINUTES", "0", "từ 1 trở lên"),
        ("MYSQL_PASSWORD", "", "Thiếu biến môi trường MYSQL_PASSWORD"),
    ],
)
def test_bad_configuration_fails_with_a_clear_message(monkeypatch, name, value, message):
    monkeypatch.setenv(name, value)
    with pytest.raises(ConfigurationError, match=message):
        Settings()


def test_allowed_origins_are_trimmed(monkeypatch):
    monkeypatch.setenv("ALLOWED_ORIGINS", " http://a.test , http://b.test ,, ")
    assert Settings().allowed_origins == ["http://a.test", "http://b.test"]


def test_docs_are_hidden_in_production(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    assert Settings().is_production is True
    monkeypatch.setenv("ENVIRONMENT", "development")
    assert Settings().is_production is False


def test_login_runs_bcrypt_even_for_an_unknown_phone(monkeypatch):
    """Số điện thoại không tồn tại phải tốn thời gian như sai mật khẩu, không thì đo được ai có tài khoản."""
    from app.core.security import DUMMY_PASSWORD_HASH
    from app.modules.auth.login import service as login_service
    from app.modules.auth.login.exceptions import UserNotFoundException
    from app.modules.auth.login.schemas import LoginRequest

    calls = []
    monkeypatch.setattr(login_service, "verify_password", lambda password, hashed: calls.append(hashed) or False)

    class EmptyRepository:
        def find_user_by_phone_number(self, phone_number):
            return None

    with pytest.raises(UserNotFoundException):
        login_service.LoginService(EmptyRepository()).login(
            LoginRequest(phone_number="0900000000", password="abcdefgh")
        )
    assert calls == [DUMMY_PASSWORD_HASH]


def test_dummy_hash_has_the_same_cost_as_real_hashes():
    from app.core.security import DUMMY_PASSWORD_HASH, hash_password

    assert DUMMY_PASSWORD_HASH.split("$")[2] == hash_password("abcdefgh").split("$")[2]


def test_user_updated_at_changes_on_update(sqlite_engine):
    from datetime import datetime

    from sqlalchemy.orm import Session

    from app.core.enums.user_role import UserRole
    from app.models.user import User

    with Session(sqlite_engine) as db:
        user = User(full_name="A", phone_number="0900000001", hashed_password="x", role=UserRole.STUDENT)
        db.add(user)
        db.commit()
        user.updated_at = datetime(2020, 1, 1)
        db.commit()
        user.full_name = "B"
        db.commit()
        db.refresh(user)
        assert user.updated_at.year >= 2026


def test_returning_an_orm_object_is_safe_with_db_session(client, sqlite_engine):
    """Đã đo: serialize xảy ra trước khi phiên đóng, nên trả ORM sau commit vẫn ổn (không DetachedInstanceError)."""
    from pydantic import BaseModel, ConfigDict

    from app.core.enums.user_role import UserRole
    from app.models.user import User

    class UserOut(BaseModel):
        model_config = ConfigDict(from_attributes=True)
        id: int
        full_name: str

    use_engine(sqlite_engine)

    @app.post("/_test/orm", response_model=UserOut)
    def create(db: DbSession):
        user = User(full_name="Orm", phone_number="0900000002", hashed_password="x", role=UserRole.STUDENT)
        db.add(user)
        db.commit()  # commit làm mọi thuộc tính hết hạn, serialize phải đọc lại được
        return user

    try:
        response = client.post("/_test/orm")
    finally:
        app.router.routes[:] = [r for r in app.router.routes if getattr(r, "path", "") != "/_test/orm"]
    assert response.status_code == 200
    assert response.json()["full_name"] == "Orm"


# ---- token có phạm vi và quy ước thời gian -------------------------------------------------

def _utc(**delta):
    from datetime import datetime, timedelta, timezone

    return datetime.now(timezone.utc) + timedelta(**delta)


def test_scoped_token_round_trip_and_wrong_scope_is_rejected():
    from jose import JWTError

    from app.core.security import create_scoped_token, decode_scoped_token

    token = create_scoped_token({"id": 7, "attempt_id": 99}, "attempt", _utc(minutes=90))
    assert decode_scoped_token(token, "attempt")["attempt_id"] == 99
    with pytest.raises(JWTError):
        decode_scoped_token(token, "other")


def test_expired_scoped_token_is_rejected():
    from jose import JWTError

    from app.core.security import create_scoped_token, decode_scoped_token

    with pytest.raises(JWTError):
        decode_scoped_token(create_scoped_token({"id": 1}, "attempt", _utc(seconds=-5)), "attempt")


def test_scoped_token_requires_a_timezone_aware_expiry():
    from datetime import datetime

    from app.core.security import create_scoped_token

    with pytest.raises(ValueError):
        create_scoped_token({"id": 1}, "attempt", datetime(2030, 1, 1))


def test_scoped_token_is_never_accepted_as_a_login_token(client, sqlite_engine):
    """Token lượt thi có "id" như token đăng nhập: nếu get_current_user_id nhận nó thì lộ cả hệ thống."""
    from jose import JWTError

    from app.core.security import create_access_token, create_scoped_token, decode_access_token

    scoped = create_scoped_token({"id": 1}, "attempt", _utc(minutes=90))
    with pytest.raises(JWTError):
        decode_access_token(scoped)
    from datetime import timedelta

    assert decode_access_token(create_access_token({"id": 1}, timedelta(minutes=5)))["id"] == 1

    use_engine(sqlite_engine)
    assert client.get("/me", headers={"Authorization": f"Bearer {scoped}"}).status_code == 401


def test_login_token_cannot_be_used_as_a_scoped_token():
    from datetime import timedelta

    from jose import JWTError

    from app.core.security import create_access_token, decode_scoped_token

    with pytest.raises(JWTError):
        decode_scoped_token(create_access_token({"id": 1}, timedelta(minutes=5)), "attempt")


def test_center_time_is_sent_with_an_explicit_offset():
    from datetime import datetime, timezone

    from app.core.clock import to_center_iso

    iso = to_center_iso(datetime(2026, 11, 24, 8, 0))
    assert iso == "2026-11-24T08:00:00+07:00"
    assert datetime.fromisoformat(iso).astimezone(timezone.utc) == datetime(2026, 11, 24, 1, 0, tzinfo=timezone.utc)


def test_center_iso_rejects_values_that_already_have_a_timezone():
    from datetime import datetime, timezone

    from app.core.clock import to_center_iso

    with pytest.raises(ValueError):
        to_center_iso(datetime(2026, 11, 24, 8, 0, tzinfo=timezone.utc))


# ---- middleware bắt lỗi chưa xử lý ----------------------------------------------------------

def test_unhandled_error_becomes_500_json_with_cors_headers_and_is_logged(client):
    from app.core.logger import logger

    @app.get("/_test/boom")
    def boom():
        raise RuntimeError("secret internal detail")

    messages = []
    sink = logger.add(messages.append, level="ERROR", diagnose=False)
    try:
        response = TestClient(app, raise_server_exceptions=False).get(
            "/_test/boom", headers={"Origin": "http://localhost:3000"}
        )
    finally:
        logger.remove(sink)
        app.router.routes[:] = [r for r in app.router.routes if getattr(r, "path", "") != "/_test/boom"]
    assert response.status_code == 500
    assert response.json() == {"detail": "Đã xảy ra lỗi máy chủ."}
    assert "secret internal detail" not in response.text  # không lộ chi tiết lỗi cho client
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"
    assert any("RuntimeError" in str(m) and "/_test/boom" in str(m) for m in messages)


def test_http_exceptions_are_not_turned_into_500(client):
    assert client.get("/no-such-route").status_code == 404


# ----- quá tải tạm thời trả 503 kèm Retry-After, không phải 500 -----
def _app_with_failing_session(exc):
    def broken_factory():
        raise exc

    app.dependency_overrides[get_session_factory] = lambda: broken_factory
    return TestClient(app, raise_server_exceptions=False)


def test_exhausted_connection_pool_returns_503_with_retry_after():
    from sqlalchemy.exc import TimeoutError as PoolTimeout

    c = _app_with_failing_session(PoolTimeout("QueuePool limit of size 10 overflow 5 reached"))
    try:
        response = c.get("/health/ready")
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 503
    assert response.headers["retry-after"] == "2"
    assert "thử lại" in response.json()["detail"]


@pytest.mark.parametrize("code", [1040, 2003, 2006, 2013])
def test_transient_mysql_errors_return_503(code):
    from sqlalchemy.exc import OperationalError

    c = _app_with_failing_session(OperationalError("SELECT 1", {}, Exception(code, "mysql")))
    try:
        response = c.get("/health/ready")
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 503
    assert response.headers["retry-after"] == "2"


def test_other_database_errors_stay_500_so_real_bugs_are_not_hidden():
    from sqlalchemy.exc import OperationalError

    c = _app_with_failing_session(OperationalError("SELECT 1", {}, Exception(1054, "Unknown column")))
    try:
        response = c.get("/health/ready")
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 500
    assert "retry-after" not in response.headers
