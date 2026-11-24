from bcrypt import gensalt, hashpw, checkpw
from jose import JWTError, jwt
from datetime import timedelta, datetime, timezone
from .config import settings


ALGORITHM = "HS256"
MAX_PASSWORD_BYTES = 72
MIN_NEW_PASSWORD_CHARACTERS = 8

# Hash bcrypt cùng cost với mật khẩu thật, dùng để tốn thời gian như nhau khi số điện thoại không tồn tại.
DUMMY_PASSWORD_HASH = "$2b$12$9/Bt/jmO9ZOBGrK7pY1uquiWXBWx38F3MbdMNzFedbWHO1ZF2i.bS"


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
    # Token có phạm vi (ví dụ lượt thi) cũng mang "id" nhưng chỉ dùng cho đúng một việc.
    # Từ chối ở đây để nó không bao giờ làm token đăng nhập chung.
    if "scope" in payload:
        raise JWTError("Token có phạm vi riêng, không dùng làm token đăng nhập")
    return payload


def create_scoped_token(payload: dict, scope: str, expires_at: datetime) -> str:
    """Token chỉ dùng cho một việc, hạn do người gọi quyết định (thời điểm tuyệt đối, có múi giờ).

    Dùng cho lượt thi: hạn = deadline_at + ân hạn, không phụ thuộc giờ học sinh đăng nhập.
    """
    if expires_at.tzinfo is None:
        raise ValueError("expires_at phải có múi giờ, nếu không hạn token sẽ lệch theo máy chủ")
    claims = {**payload, "scope": scope, "exp": expires_at}
    return jwt.encode(claims, settings.secret_key, ALGORITHM)


def decode_scoped_token(token: str, scope: str) -> dict:
    payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
    if payload.get("scope") != scope:
        raise JWTError("Token không đúng phạm vi")
    return payload

