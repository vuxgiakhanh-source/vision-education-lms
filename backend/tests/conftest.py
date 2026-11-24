"""Cấu hình dùng chung cho mọi test.

Thứ tự quan trọng: file này chạy TRƯỚC khi test import `app`, nên phải chuẩn bị biến
môi trường ở đây thì `app.core.config` mới đọc đúng.
"""

import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[1]

# 1. Máy dev: đọc backend/.env. Biến đã có sẵn trong môi trường (CI) không bị ghi đè.
load_dotenv(BACKEND_DIR / ".env")

# 2. CI hoặc máy chưa có .env: giá trị tối thiểu để import được `app`. Không bao giờ ghi đè biến thật.
for name, value in {
    "MYSQL_USER": "lms_test_user",
    "MYSQL_PASSWORD": "lms_test_password",
    "MYSQL_DATABASE": "lms_test",
    "SECRET_KEY": "test-only-secret-key-with-at-least-32-characters",
    "ACCESS_TOKEN_EXPIRE_MINUTES": "30",
    "ALLOWED_ORIGINS": "http://localhost:3000",
}.items():
    os.environ.setdefault(name, value)

# 3. DB riêng cho test MySQL: đặt LMS_TEST_MYSQL_DATABASE để test không đụng vào DB dev.
if os.getenv("LMS_TEST_MYSQL_DATABASE"):
    os.environ["MYSQL_DATABASE"] = os.environ["LMS_TEST_MYSQL_DATABASE"]

# 4. Chốt chặn: test MySQL ghi và xóa dữ liệu, chỉ được chạy trên DB có chữ "test" trong tên.
if os.getenv("SCHEDULE_MYSQL_TESTS") == "1" and "test" not in os.environ["MYSQL_DATABASE"].lower():
    raise pytest.UsageError(
        f"SCHEDULE_MYSQL_TESTS=1 đang trỏ vào DB {os.environ['MYSQL_DATABASE']!r}. "
        "Đặt LMS_TEST_MYSQL_DATABASE=<tên DB có chữ test> và chạy alembic upgrade head trên DB đó."
    )


@pytest.fixture
def sqlite_engine():
    """SQLite trong bộ nhớ với đủ bảng của mọi model. Dùng cho test mới thay vì chép lại fixture."""
    from sqlalchemy import create_engine
    from sqlalchemy.pool import StaticPool

    import app.models  # noqa: F401
    from app.core.base import Base

    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    try:
        yield engine
    finally:
        engine.dispose()
