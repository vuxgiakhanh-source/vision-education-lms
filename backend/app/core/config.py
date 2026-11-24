import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.engine import URL

# Đọc backend/.env theo vị trí file này, không phụ thuộc thư mục đang chạy lệnh.
# Biến đã có sẵn trong môi trường (CI, VPS) được giữ nguyên, .env không ghi đè.
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

MIN_SECRET_KEY_LENGTH = 32


class ConfigurationError(RuntimeError):
    pass


def _required(name: str) -> str:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        raise ConfigurationError(f"Thiếu biến môi trường {name}. Xem backend/.env.example.")
    return value


def _integer(name: str, default: int | None = None, *, minimum: int = 1) -> int:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        if default is None:
            raise ConfigurationError(f"Thiếu biến môi trường {name}. Xem backend/.env.example.")
        return default
    try:
        value = int(raw)
    except ValueError:
        raise ConfigurationError(f"{name} phải là số nguyên, nhận được {raw!r}.") from None
    if value < minimum:
        raise ConfigurationError(f"{name} phải từ {minimum} trở lên, nhận được {value}.")
    return value


class Settings:
    def __init__(self):
        self.environment = os.getenv("ENVIRONMENT", "development").strip().lower()

        self.mysql_user = _required("MYSQL_USER")
        self.mysql_password = _required("MYSQL_PASSWORD")
        self.mysql_database = _required("MYSQL_DATABASE")
        # 127.0.0.1 chứ không phải "localhost": trên Windows "localhost" thử IPv6 (::1) trước, Docker chỉ nghe IPv4,
        # nên MỖI kết nối mới chờ ~2 giây (đo: 2100 ms so với 20-40 ms). Pool tạo kết nối liên tục khi tải cao.
        self.mysql_host = os.getenv("MYSQL_HOST", "127.0.0.1")
        self.mysql_port = _integer("MYSQL_PORT", 3306)
        # URL.create mã hóa ký tự đặc biệt (@ : / %) trong mật khẩu,
        # còn nối chuỗi thô sẽ làm hỏng URL.
        self.database_url = URL.create(
            "mysql+pymysql",
            username=self.mysql_user,
            password=self.mysql_password,
            host=self.mysql_host,
            port=self.mysql_port,
            database=self.mysql_database,
        ).render_as_string(hide_password=False)

        # Mỗi tiến trình API có một pool riêng. Tổng kết nối tối đa của cả máy là
        # (pool_size + max_overflow) x số tiến trình, phải nhỏ hơn max_connections của MySQL.
        self.db_pool_size = _integer("DB_POOL_SIZE", 10)
        self.db_max_overflow = _integer("DB_MAX_OVERFLOW", 5, minimum=0)
        self.db_pool_timeout = _integer("DB_POOL_TIMEOUT", 10)
        self.db_pool_recycle = _integer("DB_POOL_RECYCLE", 1800)

        self.secret_key = _required("SECRET_KEY")
        if len(self.secret_key) < MIN_SECRET_KEY_LENGTH:
            raise ConfigurationError(f"SECRET_KEY phải có ít nhất {MIN_SECRET_KEY_LENGTH} ký tự.")
        self.access_token_expire_minutes = _integer("ACCESS_TOKEN_EXPIRE_MINUTES")
        self.allowed_origins = [
            origin.strip() for origin in _required("ALLOWED_ORIGINS").split(",") if origin.strip()
        ]

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


settings = Settings()
