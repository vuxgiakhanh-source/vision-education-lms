# Điểm dừng và nhật ký học/code

## Đọc đầu tiên khi mở dự án

- **Hiện tại:** đã có khung auth và dashboard responsive; dashboard vẫn dùng mock.
- **Việc đang chọn:** L00.2 — kể lại luồng đăng nhập từ frontend đến database và quay về.
- **Mở ở đâu:** [CODE_GUIDE mục luồng đăng nhập](CODE_GUIDE.md#5-đọc-một-luồng-hoàn-chỉnh-đăng-nhập).
- **Khi nào xong:** tự vẽ và giải thích được luồng mà không nhìn tài liệu;
  chạy thử nếu môi trường backend sẵn sàng và ghi kết quả thật.
- **Sau đó:** L00.3 — đọc lại đổi mật khẩu.
- **Chưa rõ:** thời gian học mỗi ngày và mức tự làm của từng mảng; chưa đặt lịch tuần.

Đây là điểm bắt đầu đề xuất. Khi chọn việc khác, thay nội dung khối này để nó
luôn chỉ đúng một việc tiếp theo.

## Quy trình mỗi buổi

**Mở buổi:** đọc điểm dừng → xem `git status --short` → chọn một mã việc →
nói rõ đầu vào, đầu ra và cách kiểm tra trước khi sửa.

**Trong buổi:** học phần nhỏ cần dùng → thực hành → giải thích lại → kiểm tra.
Nếu nhờ AI, yêu cầu chỉ ra luồng và lý do thay đổi; tự xem diff trước khi nhận là đã hiểu.

**Cuối buổi:** ghi kết quả theo mẫu → cập nhật điểm dừng → đánh dấu checklist
khi có bằng chứng → tạo commit mô tả đúng phần đã làm nếu muốn lưu mốc.
Không đưa cả thay đổi không liên quan vào cùng một commit.

## Mẫu ghi nhanh — sao chép cho mỗi buổi

```text
Ngày:
Mã việc:
Mục tiêu của buổi:

Mình đã đọc/sửa file nào? Vì sao?
-

Luồng xử lý mình hiểu được (viết bằng lời của mình):
-

Đã kiểm tra gì? Kết quả thật?
- Lệnh/tình huống:
- Kết quả:
- Chưa kiểm tra:

Quyết định nghiệp vụ (nếu có): ai chốt, nội dung, còn đề xuất hay đã duyệt?
-

Điều còn chưa hiểu/lỗi có thể tái hiện:
-

Việc đầu tiên lần sau (ghi cụ thể file và thao tác):
-

Commit nếu có:
```

## Nhật ký 17/10/2026 — lập lại bản đồ dự án

- Đã đọc cấu trúc source, luồng login/change-password/me, model users và nơi lấy dữ liệu dashboard.
- Đã viết README, CODE_GUIDE, LEARNING_ROADMAP và nhật ký này để có điểm quay lại.
- Dashboard responsive đã được áp dụng ở các buổi trước; phần nghiệp vụ vẫn dùng mock.
- Ở các buổi trước, frontend build/lint đã qua và đã đo 20 mốc chiều rộng dashboard.
- Trong lần lập tài liệu này chưa chạy lại đăng nhập/database, chưa chạy migration,
  seed hoặc thay đổi hành vi ứng dụng.
- Chưa đánh dấu bài học nào là người dùng đã hiểu; các checklist vẫn để mở.
- Việc tiếp theo đề xuất: L00.2 trong LEARNING_ROADMAP.
