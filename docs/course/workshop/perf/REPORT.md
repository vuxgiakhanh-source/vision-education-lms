# Phiếu đo tải — để trống đến khi chạy thật

Trạng thái: CHƯA ĐO. Không có số tải được công bố từ script mẫu.

| Điều kiện | Giá trị thực tế |
|---|---|
| Ngày, người đo, commit, image digest, schema revision | |
| CPU/RAM/ổ đĩa máy app và máy phát tải | |
| MySQL version, DB size, số lớp/bài/user/bài nộp | |
| API replicas/workers, pool_size/max_overflow, proxy limit | |
| Script hash, MODE/RATE/DURATION/MAX_VUS, token TTL | |
| Mục tiêu p95/p99/lỗi và nguồn yêu cầu | |

| Lần | Workload | Offered rate | Achieved rate | p95/p99 ms | Lỗi/check fail | Dropped | CPU/RAM/DB locks |
|---|---|---|---|---|---|---|---|
| Baseline | | | | | | | |
| Sau sửa một nguyên nhân | | | | | | | |
| Lặp cùng điều kiện | | | | | | | |

Sau tải ghi SQL đối chiếu: không trùng (assignment_id, student_id), timestamp
không bị retry đổi, score chưa công bố không xuất hiện. Ghi số row trước/sau.
Attach summary không chứa token, log đã làm sạch, EXPLAIN, diff và lý do thay đổi.
Phân biệt lần đầu INSERT với lần sau retry; không báo benchmark ghi mới từ retry.

Kết luận chỉ áp dụng môi trường/workload đã đo. Nếu dropped > 0 hoặc máy phát
tải nghẽn, chưa chứng minh đã phục vụ đủ offered rate. Ghi giới hạn thay vì ngoại suy.
