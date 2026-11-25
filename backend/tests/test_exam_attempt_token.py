"""Token riêng cho lượt thi: phạm vi, hạn theo deadline, không lẫn với token đăng nhập."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from jose import JWTError, jwt

from app.core.clock import center_local_now
from app.core.config import settings
from app.core.security import ALGORITHM, create_access_token, decode_access_token
from app.modules.exams.attempts.token import (
    TOKEN_BUFFER,
    issue_attempt_token,
    token_expiry,
    verify_attempt_token,
)
from app.modules.exams.domain.errors import NotAllowedToEnter


def test_roundtrip_returns_attempt_and_student():
    token = issue_attempt_token(attempt_id=42, student_id=7, deadline_at=center_local_now() + timedelta(minutes=30))
    claims = verify_attempt_token(token)
    assert (claims.attempt_id, claims.student_id) == (42, 7)


def test_expiry_is_deadline_plus_buffer_converted_from_vietnam_time_to_utc():
    deadline = datetime(2030, 1, 1, 9, 30)  # giờ Việt Nam
    # 09:30 +07:00 = 02:30 UTC; cộng đệm 60 phút = 03:30 UTC
    assert token_expiry(deadline) == datetime(2030, 1, 1, 3, 30, tzinfo=timezone.utc)
    assert TOKEN_BUFFER == timedelta(minutes=60)


def test_token_survives_refresh_after_the_deadline_within_buffer():
    """Em F5 hoặc mở lại tab sau khi hết giờ vẫn xem được biên nhận, không bị đá ra trang đăng nhập."""
    token = issue_attempt_token(attempt_id=1, student_id=1, deadline_at=center_local_now() - timedelta(minutes=59))
    assert verify_attempt_token(token).attempt_id == 1


def test_token_expires_after_the_buffer():
    token = issue_attempt_token(attempt_id=1, student_id=1, deadline_at=center_local_now() - timedelta(minutes=61))
    with pytest.raises(NotAllowedToEnter):
        verify_attempt_token(token)


def test_login_token_cannot_be_used_as_attempt_token():
    login = create_access_token({"sub": "7"}, timedelta(minutes=30))
    with pytest.raises(NotAllowedToEnter):
        verify_attempt_token(login)


def test_attempt_token_cannot_be_used_as_login_token():
    token = issue_attempt_token(attempt_id=1, student_id=7, deadline_at=center_local_now() + timedelta(minutes=30))
    with pytest.raises(JWTError):
        decode_access_token(token)


@pytest.mark.parametrize("bad", ["", "abc", "a.b.c", "Bearer xyz"])
def test_garbage_is_rejected(bad):
    with pytest.raises(NotAllowedToEnter):
        verify_attempt_token(bad)


def test_tampered_token_is_rejected():
    token = issue_attempt_token(attempt_id=1, student_id=7, deadline_at=center_local_now() + timedelta(minutes=30))
    head, body, sig = token.split(".")
    forged = ".".join([head, body, sig[:-2] + ("AA" if not sig.endswith("AA") else "BB")])
    with pytest.raises(NotAllowedToEnter):
        verify_attempt_token(forged)


def test_token_signed_with_another_secret_is_rejected():
    claims = {"sub": "7", "aid": 1, "scope": "exam_attempt", "exp": datetime.now(timezone.utc) + timedelta(hours=1)}
    forged = jwt.encode(claims, "x" * 40, ALGORITHM)
    assert settings.secret_key != "x" * 40
    with pytest.raises(NotAllowedToEnter):
        verify_attempt_token(forged)


def test_token_missing_required_claims_is_rejected():
    claims = {"scope": "exam_attempt", "exp": datetime.now(timezone.utc) + timedelta(hours=1)}
    with pytest.raises(NotAllowedToEnter):
        verify_attempt_token(jwt.encode(claims, settings.secret_key, ALGORITHM))


def test_token_with_wrong_scope_is_rejected():
    claims = {"sub": "7", "aid": 1, "scope": "password_reset", "exp": datetime.now(timezone.utc) + timedelta(hours=1)}
    with pytest.raises(NotAllowedToEnter):
        verify_attempt_token(jwt.encode(claims, settings.secret_key, ALGORITHM))
