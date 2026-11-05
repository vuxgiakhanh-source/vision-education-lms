# 12 — Kiểm thử, Git và đưa hệ thống ra dùng thử

## Bài 12.1 — Chọn đúng thứ cần kiểm tra

| Loại | Kiểm tra gì? | Ví dụ |
|---|---|---|
| Unit | Quy tắc độc lập dependency ngoài | Đúng deadline, điểm 0, retry không đổi timestamp |
| Integration | Các phần thực sự phối hợp | Unique MySQL, transaction rollback, route/auth/DB |
| Luồng người dùng | Người dùng hoàn thành công việc | Cô giao → học sinh nộp → cô chấm → xem điểm |
| Giao diện | Layout, trạng thái, bàn phím | Mobile, dữ liệu dài, zoom, loading/error |

Test đúng đường chạy vui chưa đủ. Ưu tiên quyền truy cập, chấm điểm, lưu bài,
deadline và migration vì sai ở đó có tác động thực tế. Không viết hàng loạt test
chỉ kiểm tra className hoặc lặp lại y nguyên câu if của implementation.

## Bài 12.2 — Arrange, Act, Assert

Tạo dữ liệu → thực hiện một hành động → kiểm tra kết quả quan sát được.
Ví dụ nộp hai lần cùng nội dung phải cùng id và giữ thời gian cũ; kiểm tra trạng
thái lưu, không chỉ kiểm tra service đã gọi hàm nào đó.

Kho ví dụ dùng unittest của Python, không cần cài pytest. Chạy từ gốc repo:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s docs/course/examples -p "test_domain.py" -v
```

Nếu chọn pytest sau này, hiểu assertion/fixture/parametrize và test DB trước
khi thêm plugin. Hiện repo chưa khai báo pytest như phụ thuộc test.

## Bài 12.3 — Dữ liệu test và sự độc lập

Mỗi test có fixture đủ nhỏ để hiểu, không phụ thuộc thứ tự chạy hay user seed
từ buổi trước. Dùng giờ cố định để kiểm deadline; server thật vẫn lấy giờ server.
Test integration dùng database riêng và migration đúng; rollback/reset dữ liệu
theo cơ chế test đã thiết kế. Không trỏ test vào database lớp đang học thật.

SQLite/memory fake giúp test một số logic nhưng không chứng minh behavior MySQL,
locking, collation hay transaction tương đương. Hai request đồng thời là một
bài integration riêng; chỉ gọi hàm hai lần tuần tự chưa phải test concurrency.

## Bài 12.4 — Git như nhật ký có thể review

Trước sửa: status và diff. Khi cần nhánh riêng, tên mặc định theo môi trường
làm việc này là `codex/<ten-viec>`, có thể theo quy ước khác nếu người dùng yêu cầu.
Tách việc liên quan, đặt commit mô tả hành vi. Trước khi commit: xem đúng file,
kiểm tra không có bí mật/dữ liệu riêng, ghi validation thực sự đã chạy.

Ví dụ mô tả thay đổi:

```text
Vấn đề: gửi lại request nộp bài tạo bản trùng sau khi mất mạng.
Thay đổi: trả bản đã có khi cùng nội dung, giữ timestamp ban đầu.
Kiểm tra: cùng nội dung, nội dung khác, retry sau hạn, unique DB khi cạnh tranh.
Giới hạn: chưa hỗ trợ sửa bài đã nộp; đó là nghiệp vụ riêng.
```

Đọc được diff và giải thích từng thay đổi là kỹ năng bắt buộc khi dùng AI.
Không đánh dấu đã test DB chỉ vì unit test fake chạy qua.

## Bài 12.5 — CI và kiểm tra hiện tại

Ở `frontend`, repo đã có `npm run build` và `npm run lint`. Đây không phải test
nghiệp vụ. Khi đã có test, CI nên cài phụ thuộc có thể tái lập, chạy kiểm tra kiểu,
lint, unit và integration cần thiết trên môi trường riêng.

Backend requirements hiện không pin tất cả phiên bản; học cách quản lý/phân tách
phụ thuộc runtime/dev và tái lập môi trường trước khi phát hành. Dùng lockfile
frontend hiện có; tránh chỉnh tay version để làm thông báo lỗi biến mất.

CI chạy kiểm tra; CD là quy trình phát hành. Không cần tự động triển khai mọi
lần push ngay khi chưa có môi trường thử và cách quay lại.

## Bài 12.6 — Cấu hình, triển khai và quan sát

- Dev, test, staging, production phải phân biệt cấu hình và dữ liệu.
- Không commit `.env` thật; frontend biến môi trường được bundle có thể đọc
  được ở client, nên không đặt secret server ở `VITE_*`.
- Build frontend rồi phục vụ file phù hợp; backend chạy bằng tiến trình server
  có quản lý; cấu hình HTTPS, origin và reverse proxy theo môi trường đã chọn.
- Log hành động và lỗi với ngữ cảnh vừa đủ/mã request; không log token/password.
- Chạy migration có kế hoạch, backup trước thay đổi ảnh hưởng dữ liệu.
- File upload cần nơi lưu bền vững, quyền tải và backup; không dựa vào ổ tạm của process.
- Tách lỗi mạng/cấu hình/DB/logic bằng log và trạng thái health phù hợp.

Docker Compose hiện chỉ có MySQL. Nó chưa chứng minh frontend/backend đã có
image production, backup hoặc cơ chế vận hành hoàn chỉnh.

## Bài 12.7 — Backup phải phục hồi thử

Một file backup tồn tại chưa đủ. Trên môi trường thử, phục hồi vào database mới,
kiểm tra tài khoản/lớp/bài nộp/file liên quan và ghi thời gian/các bước. Khi schema
đổi, rollback code không tự rollback dữ liệu an toàn; tránh coi downgrade là
lệnh cứu mọi tình huống. Chốt mức chấp nhận mất dữ liệu và thời gian phục hồi
với người vận hành trước khi dùng thật.

## Bài tự viết và buổi dùng thử

- **Q1:** bộ unit test theo hợp đồng chương 10, gồm dữ liệu không đổi khi bị từ chối.
- **Q2:** integration cho FK/UNIQUE/rollback và request đồng thời.
- **Q3:** hai tài khoản thực hiện luồng xuyên hệ thống, có refresh và lỗi mạng.
- **Q4:** README đủ để người khác chạy, không cần bạn đọc mật khẩu cấu hình cho họ.
- **Q5:** phát hành staging, diễn tập lỗi bản mới và phục hồi dữ liệu thử.
- **Q6:** một nhóm dùng thử; mỗi lỗi có bước tái hiện, mức ảnh hưởng và bằng chứng sửa.

Qua chương khi tự chứng minh bản phát hành làm được việc gì, chưa làm được gì
và cách phát hiện/phục hồi khi có lỗi. Không hứa một stack sẽ tự tạo chất lượng.

Tham khảo: [pytest](https://docs.pytest.org/en/stable/getting-started.html),
[Python unittest](https://docs.python.org/3/library/unittest.html).
