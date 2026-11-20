from bcrypt import gensalt, hashpw, checkpw
from jose import jwt
from datetime import timedelta, datetime, timezone
from .config import settings


ALGORITHM = "HS256"
MAX_PASSWORD_BYTES = 72
MIN_NEW_PASSWORD_CHARACTERS = 8


class InvalidPasswordError(ValueError):
    pass


def _encode_password(password: str) -> bytes:
    try:
        encoded = password.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise InvalidPasswordError("Mật khẩu chứa ký tự không hợp lệ.") from exc
    if len(encoded) > MAX_PASSWORD_BYTES:
        raise InvalidPasswordError(f"Mật khẩu không được vượt quá {MAX_PASSWORD_BYTES} byte UTF-8.")
    return encoded


def validate_password_length(password: str) -> None:
    _encode_password(password)


def validate_new_password_length(password: str) -> None:
    validate_password_length(password)
    if len(password) < MIN_NEW_PASSWORD_CHARACTERS:
        raise InvalidPasswordError(f"Mật khẩu mới phải có ít nhất {MIN_NEW_PASSWORD_CHARACTERS} ký tự.")


def hash_password(password: str) -> str:
    return hashpw(_encode_password(password), gensalt()).decode("utf-8")

def verify_password(password: str, hashed_password: str) -> bool:
    return checkpw(_encode_password(password), hashed_password.encode("utf-8"))

#3  Tạo token truy cập
def create_access_token(payload: dict, expires_delta: timedelta):
    copy_payload = payload.copy()
    copy_payload["exp"] = datetime.now(timezone.utc) + expires_delta
    SECRET_KEY = settings.secret_key
    access_token = jwt.encode(copy_payload, SECRET_KEY, ALGORITHM)
    return access_token
#4 Giải mã token truy cập
def decode_access_token(access_token: str) -> dict:
    SECRET_KEY = settings.secret_key
    payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload

