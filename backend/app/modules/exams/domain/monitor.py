"""Phân loại trạng thái từng em cho màn theo dõi của giáo viên. Hàm thuần.

Máy chủ chỉ biết lần cuối nhận tín hiệu của em (last_seen_at), nên "mất kết nối" không phân biệt được giữa mạng
chập chờn, mất điện hay tắt máy. Số liệu rời màn hình, thoát toàn màn hình, offline do trình duyệt báo: chỉ để cô
cân nhắc, không bao giờ tự trừ điểm hay khóa bài.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timedelta
from typing import Any

# Quá khoảng này không có tín hiệu thì coi là mất kết nối. Nhịp lưu là 10–20 giây nên 60 giây là ba nhịp.
ONLINE_WINDOW_SECONDS = 60

NOT_STARTED = "not_started"
IN_PROGRESS = "in_progress"
DISCONNECTED = "disconnected"
SUBMITTED = "submitted"
AUTO_SUBMITTED = "auto_submitted"

# Loại sự kiện trình duyệt được phép gửi. Danh sách đóng để bảng sự kiện không bị nhét dữ liệu tùy ý.
ALLOWED_EVENT_TYPES = frozenset(
    {
        "visibility_hidden", "visibility_visible", "blur", "focus", "fullscreen_exit", "fullscreen_enter",
        "offline", "online", "pagehide", "copy", "paste", "contextmenu",
    }
)
MAX_EVENTS_PER_REQUEST = 50
MAX_EVENTS_PER_ATTEMPT = 2000
MAX_EVENT_PAYLOAD_BYTES = 1024


def classify(*, status: str | None, last_seen_at: datetime | None, now: datetime) -> str:
    if status is None:
        return NOT_STARTED
    if status in (SUBMITTED, AUTO_SUBMITTED):
        return status
    if last_seen_at is None or now - last_seen_at > timedelta(seconds=ONLINE_WINDOW_SECONDS):
        return DISCONNECTED
    return IN_PROGRESS


def answered_count(answers: Mapping[str, Any] | None) -> int:
    """Số câu đã trả lời. Câu đúng/sai tính là đã trả lời khi có ít nhất một ý được chọn."""
    if not answers:
        return 0
    total = 0
    for value in answers.values():
        if isinstance(value, str):
            total += bool(value.strip())
        elif isinstance(value, Mapping):
            total += any(v is not None for v in value.values())
        else:
            total += value is not None
    return total
