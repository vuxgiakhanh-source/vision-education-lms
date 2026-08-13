from bcrypt import gensalt, hashpw, checkpw
from jose import jwt
from datetime import timedelta, datetime, timezone
from .config import settings


ALGORITHM = "HS256"
#1 Mã hóa password để lưu vào db
def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8") # change from string to bytes
    hashed_bytes = hashpw(password_bytes, gensalt()) # create hashed bytes
    hashed_string = hashed_bytes.decode("utf-8") # decode from bytes to string
    return hashed_string

#2 Xác thực xem password có đúng khi đăng nhập ko
def verify_password(password: str, hashed_password: str) -> bool:
    return checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))

#3  Tạo token truy cập
def create_access_token(payload: dict, expires_delta: timedelta):
    copy_payload = payload.copy()
    copy_payload["exp"] = datetime.now(timezone.utc) + expires_delta
    SECRET_KEY = settings.secret_key
    access_token = jwt.encode(copy_payload, SECRET_KEY, ALGORITHM)
    return access_token


