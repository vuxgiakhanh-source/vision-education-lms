"""Hạn nộp và ân hạn. Mọi giờ là giờ Việt Nam không múi giờ (core.clock.center_local_now)."""

from __future__ import annotations

from datetime import datetime, timedelta

DEFAULT_GRACE_SECONDS = 30


def can_enter(now: datetime, opens_at: datetime, closes_at: datetime) -> bool:
    """Vào được trong [opens_at, closes_at). Sau giờ đóng thì không bắt đầu lượt mới."""
    return opens_at <= now < closes_at


def compute_deadline(now: datetime, closes_at: datetime, duration_minutes: int) -> datetime:
    """Hạn nộp của một lượt, tính MỘT LẦN ở máy chủ lúc bắt đầu.

    Vào muộn thì không được thêm giờ: phòng 08:00–10:00, bài 90 phút, vào 08:45 thì hạn là 10:00
    (không phải 10:15). Vào đúng 08:00 thì hạn là 09:30.
    """
    return min(closes_at, now + timedelta(minutes=duration_minutes))


def is_within_grace(now: datetime, deadline_at: datetime, grace_seconds: int = DEFAULT_GRACE_SECONDS) -> bool:
    """Còn nhận bài đến deadline + ân hạn (mạng chậm lúc bấm Nộp ở giây chót)."""
    return now <= deadline_at + timedelta(seconds=grace_seconds)


def grace_floor(now: datetime, grace_seconds: int = DEFAULT_GRACE_SECONDS) -> datetime:
    """Giá trị `:now_minus_grace` dùng trong câu UPDATE lưu bài: deadline_at >= grace_floor."""
    return now - timedelta(seconds=grace_seconds)
