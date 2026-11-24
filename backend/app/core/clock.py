from datetime import datetime, timedelta, timezone

CENTER_TZ = timezone(timedelta(hours=7))

# Quy ước thời gian của hệ thống:
# - Dữ liệu nghiệp vụ trong DB (lịch học, kỳ thi, hạn nộp) là GIỜ VIỆT NAM, cột DateTime KHÔNG có múi giờ.
#   Mọi nơi lấy "bây giờ" để so sánh với các cột đó phải gọi center_local_now(), không gọi datetime.now().
# - JWT dùng UTC có múi giờ (thư viện jose yêu cầu), tách biệt hoàn toàn với dữ liệu nghiệp vụ.
# - Gửi ra ngoài (API) bằng to_center_iso(): chuỗi ISO có offset +07:00. Không gửi chuỗi không có múi giờ,
#   vì trình duyệt sẽ hiểu theo giờ máy của học sinh.
# - Giao diện thi không tin đồng hồ máy học sinh: tính độ lệch = server_now - Date.now() lúc nhận phản hồi.


def center_local_now() -> datetime:
    """Return the center's Vietnam wall time without a UTC offset."""
    return datetime.now(CENTER_TZ).replace(tzinfo=None)


def to_center_iso(value: datetime) -> str:
    """Giờ Việt Nam không múi giờ trong DB -> ISO 8601 có offset, ví dụ 2026-11-24T08:00:00+07:00."""
    if value.tzinfo is not None:
        raise ValueError("Dữ liệu nghiệp vụ phải là giờ Việt Nam không kèm múi giờ")
    return value.replace(tzinfo=CENTER_TZ).isoformat()
