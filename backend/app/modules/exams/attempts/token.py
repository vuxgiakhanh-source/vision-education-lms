"""Token riêng cho một lượt thi.

Vì sao không dùng token đăng nhập: token đăng nhập hết hạn theo giờ đăng nhập (180 phút), còn ca thi có hạn riêng.
Token lượt thi gắn với MỘT lượt và hết hạn ở deadline_at + khoảng đệm, nên em F5, mạng lag hay mở lại tab giữa
giờ vẫn vào lại được mà không phải đăng nhập, và token không dùng được cho việc nào khác.

- Phạm vi "exam_attempt": token đăng nhập không dùng được ở đây, và ngược lại (decode_access_token từ chối
  token có `scope`).
- Hạn: deadline_at + TOKEN_BUFFER. Đủ dài để nộp bài và xem biên nhận sau hạn, nhưng không mãi mãi.
- sendBeacon không đặt được header Authorization nên API sự kiện nhận token trong thân yêu cầu; hàm xác thực
  dùng chung cho cả hai đường.
- Token chỉ chứng minh "em này đang dự lượt này". Quyền ghi vẫn do write_epoch quyết định.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from jose import JWTError

from app.core.clock import CENTER_TZ
from app.core.security import create_scoped_token, decode_scoped_token
from app.modules.exams.domain.errors import NotAllowedToEnter

SCOPE = "exam_attempt"
TOKEN_BUFFER = timedelta(minutes=60)


@dataclass(frozen=True)
class AttemptClaims:
    attempt_id: int
    student_id: int


def token_expiry(deadline_at: datetime) -> datetime:
    """deadline_at là giờ Việt Nam không múi giờ trong DB; JWT cần thời điểm tuyệt đối có múi giờ."""
    return deadline_at.replace(tzinfo=CENTER_TZ).astimezone(timezone.utc) + TOKEN_BUFFER


def issue_attempt_token(*, attempt_id: int, student_id: int, deadline_at: datetime) -> str:
    return create_scoped_token(
        {"sub": str(student_id), "aid": attempt_id}, SCOPE, token_expiry(deadline_at)
    )


def verify_attempt_token(token: str) -> AttemptClaims:
    """Trả (lượt, học sinh) từ token. Mọi lỗi (hỏng, hết hạn, sai phạm vi) đều là NotAllowedToEnter."""
    try:
        payload = decode_scoped_token(token, SCOPE)
        return AttemptClaims(attempt_id=int(payload["aid"]), student_id=int(payload["sub"]))
    except (JWTError, KeyError, ValueError, TypeError) as exc:
        raise NotAllowedToEnter("Phiên làm bài không hợp lệ hoặc đã hết hạn.") from exc
