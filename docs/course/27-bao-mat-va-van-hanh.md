# P4 — Phiên đăng nhập, bảo vệ dữ liệu và vận hành qua sự cố

Đầu ra: threat model theo chức năng, một kế hoạch phiên có thể test và một buổi
diễn tập phát hiện/phục hồi. Học sau auth, debug, triển khai và đo tải.

## 1. Phân biệt fixture học với tài khoản người dùng

Workbench dùng JWT tạo bởi CLI để học scope, không có mật khẩu/login thật.
Không đưa CLI cấp token tùy user ra Internet. Trước dùng người thật, nối login
đã kiểm hash/active/rate limit và chốt chính sách phiên theo nhu cầu.

Viết bảng tài sản → tác nhân → điểm vào → điều cấm → test. Điểm vào có cả list,
detail, write, file, export, socket và job nền. Không chỉ bảo vệ trang route.

| Tài sản | Tình huống tấn công/lỗi | Bằng chứng bắt buộc |
|---|---|---|
| Bài nộp | Đổi assignment/student id | Chủ bài lấy từ actor, scope server, DB không đổi |
| Điểm chưa công bố | Gọi API trực tiếp hoặc xem cache | JSON không có điểm riêng, cache đúng user |
| Tài khoản | Đoán mật khẩu/reset token | Giới hạn thử, thông báo phù hợp, không log secret |
| File | Sửa storage key/URL, upload quá lớn | Private storage, quyền tải, limit trước hết RAM |
| Quản trị | Tự gửi role/admin trong JSON | Input allowlist, capability check, audit |

## 2. Thiết kế phiên bằng vòng đời cụ thể

Chọn storage/token/cookie theo kiến trúc, ghi lý do và nguy cơ. HttpOnly cookie
giảm khả năng JavaScript đọc credential nhưng cần xử lý CSRF/credential policy;
localStorage có thể bị script XSS đọc. Không có một lựa chọn thay mọi kiểm soát.

Một thiết kế tham khảo để tự triển khai: access token ngắn hạn, refresh token
opaque ngẫu nhiên, server lưu hash refresh cùng session_id/user/expiry/revoked,
rotation qua transaction. Không lưu refresh plain trong DB; không log token.
TTL cụ thể phải chốt; thời gian ngắn không thay cơ chế thu hồi/quyền hiện tại.

```text
Login hợp lệ → tạo session + refresh hash → cấp access/refresh
Refresh hợp lệ → khóa/atomic claim token cũ → thay bằng token mới → commit
Logout phiên → revoke session, client xóa credential
Reset password/khóa user → xử lý các phiên theo policy đã chốt
```

JWT signature hợp lệ chưa nói session còn được dùng. Nếu cần thu hồi ngay,
server cần kiểm trạng thái/session version theo policy thay vì chỉ chờ exp.
Lab hiện kiểm active/role từ DB mỗi request, chưa có refresh/session store.

## 3. Test các race của refresh và reset

Hai tab cùng refresh không được tạo hai chuỗi phiên không kiểm soát. Chốt
policy token single-use, phát hiện reuse, cách tab phối hợp và trường hợp response
mất sau rotation. Không tự retry refresh cũ vô hạn rồi khóa nhầm mọi người.

Password reset: token ngẫu nhiên một lần/hết hạn, hash lưu server, response
request không lộ user tồn tại, giới hạn theo tài khoản/IP phù hợp. Consume token
và thay password trong một transaction; xử lý các phiên cũ theo policy.

| Test | Kết quả phải chốt trước implementation |
|---|---|
| Refresh hai request cùng token | Một lần tiêu thụ; request còn lại theo policy rõ |
| Reuse token đã rotate | Không cấp phiên mới ngoài hợp đồng |
| Logout rồi dùng access cũ | Bị chặn ngay hoặc còn đến exp theo policy đã ghi |
| Reset token sai/hết hạn/đã dùng | Không thay password; không lộ dữ liệu |
| User khóa giữa phiên | Request tiếp theo bị chặn, job/socket xét lại quyền |

Đây là hợp đồng và bài triển khai, chưa có implementation refresh/reset hoàn
chỉnh trong lab. Nộp code cùng test cạnh tranh trước khi đánh dấu hoàn thành.

## 4. Giới hạn tài nguyên và upload

Nginx lab giới hạn body 32k và rate theo IP; API giới hạn title/answer/page_size.
Limit theo IP có thể gộp cả trường chung NAT; khi scale phải xét trusted proxy,
actor/endpoint và state chung. Không tin X-Forwarded-For từ client không tin cậy.

Upload thực tế cần giới hạn ở proxy và application, streaming, quota, allowlist
loại nội dung, private storage, filename safe, quyền download và cleanup. Kiểm
magic/content theo loại được nhận, scan nếu threat model cần; không thực thi file.
Nội dung HTML/rich text phải có policy sanitize và render an toàn.

Khi thêm upload, nâng body limit cho đúng route sau review, không tăng toàn bộ
API vô hạn. Log lỗi cleanup thành job có thể xử lý; DB rollback không xóa object
đã ghi storage. Signed URL cần TTL/scope và cơ chế quyền phù hợp.

## 5. Observability bắt đầu từ một sự cố có thể lần ra

Mở [server.py](workshop/lms_lab/server.py): middleware tạo request_id, ghi route
pattern/status/elapsed và trả header cho client. Không ghi JSON body, token,
password, query string hoặc bài làm để tiện debug. Log và audit nghiệp vụ là
hai loại dữ liệu có mục đích/retention khác nhau.

```text
User báo lỗi + thời điểm/mã request
 → tìm API log → xem status/latency
 → đối chiếu DB/connection/lock và release
 → giả thuyết nhỏ → kiểm tra → giảm tác động → sửa → regression test
```

Metrics cần: rate/error/duration theo route, CPU/RAM, pool wait/timeout,
connections/locks/slow queries, job backlog/age/fail và storage. Dùng label
route pattern; user_id/request_id không làm label metrics vì cardinality lớn.
Exporter/dashboard/alert là bài thêm ở môi trường vận hành, chưa được tích hợp
trong template. Log timing không thay được toàn bộ metrics/tracing.

## 6. Alert cần dẫn đến hành động

Ví dụ bài tập: tỉ lệ lỗi ngoài dự kiến vượt ngưỡng đã chốt trong cửa sổ đủ mẫu,
p95 tăng kéo dài, DB hết connection, job lâu không xử lý, backup quá hạn.
Đặt ngưỡng dựa baseline/SLO, người nhận và runbook; một request lỗi đơn lẻ
không mặc nhiên cần đánh thức người vận hành.

Một alert phải trả lời: ảnh hưởng ai, bắt đầu khi nào, link dashboard/log nào,
ai xử lý, bước giảm tác động và khi nào escalates. Kiểm alert bằng lỗi chủ đích
trong staging và xác nhận hết cảnh báo sau khôi phục.

## 7. RPO/RTO biến backup thành yêu cầu

RPO: tối đa mất bao nhiêu dữ liệu theo thời gian. RTO: cần phục hồi dịch vụ
trong bao lâu. Ví dụ bài tập đề xuất RPO 24 giờ/RTO 60 phút phải được ghi là
mục tiêu, không phải đã đạt. Thi cử/nộp bài có thể cần yêu cầu nghiêm hơn.

Tần suất backup, binlog/point-in-time recovery, nơi lưu độc lập và cách phục hồi
phải phù hợp mục tiêu. Backup mỗi ngày không đáp ứng mặc nhiên RPO vài phút.
Đo restore DB mới, đối chiếu dữ liệu/file và smoke app. Giữ bằng chứng ngày đo,
dataset size và thời gian; diễn tập lại khi schema/storage thay đổi lớn.

## 8. Runbook một trang cho DB không truy cập được

1. Ghi thời điểm, release/schema và ảnh hưởng; tạm ngừng phát hành khác.
2. Kiểm /health so /ready, API log/pool wait, DB process/storage/network.
3. Phân biệt password/config sai, hết disk, connection cạn và query bị khóa.
4. Chọn giảm tải/tạm dừng tác vụ nền/rollback config phù hợp, tránh restart
   hàng loạt làm mất dấu vết và tăng kết nối đột biến.
5. Sau hồi phục, chạy smoke lưu/nộp/xem điểm bằng dữ liệu thử.
6. Ghi nguyên nhân, dữ liệu có thể ảnh hưởng, action owner và regression test.

## 9. Bài tập và điều kiện qua

**Điền:** threat model cho một endpoint download và một job export.
**Trắng:** triển khai một luồng reset/refresh có transaction theo policy đã
chốt, test sai/hết hạn/nhận lặp/cạnh tranh. **Sửa lỗi:** điểm chưa công bố lọt
qua cache hoặc export dù API chính đã ẩn; test phải bao phủ đường bị bỏ sót.

Qua khi mày tái hiện được một lỗi staging, tìm request/log, bảo vệ dữ liệu khi
sửa và phục hồi theo RPO/RTO đã đo. Không tự nhận hệ thống bảo mật chỉ vì dùng JWT.

Nguồn: [OWASP session management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html),
[OWASP forgot password](https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html),
[OWASP file upload](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html).
