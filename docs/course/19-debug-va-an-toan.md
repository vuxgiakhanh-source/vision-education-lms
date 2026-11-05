# Debug, bảo mật và chất lượng qua sự cố thật

## 1. Quy trình debug có thể lặp lại

Ghi mong đợi → tái hiện nhỏ nhất → quan sát → một giả thuyết → một phép thử →
sửa nguyên nhân → kiểm tra lại lỗi cũ và đường đúng. Không đổi năm thứ cùng lúc.
Stack trace, HTTP status và SQL error là dữ liệu, không phải chỉ dẫn “cài lại hết”.

## 2. Bảy sự cố để tự điều tra

| Dấu hiệu | Phép thử đầu | Kết luận chỉ được rút ra sau thử |
|---|---|---|
| Nút không làm gì | Console + breakpoint handler + Network | Event/validation/API ở đâu dừng? |
| 422 khi gửi tên lớp | Payload so với schema | Sai tên field, kiểu, trim hay giới hạn? |
| Reload mất lớp vừa tạo | Xem response, DB, commit, request GET | UI local đã bị nhầm với lưu bền? |
| Đổi lớp thấy dữ liệu lớp cũ | Network thứ tự response, dependency | Race/cleanup hay API trả sai scope? |
| Điểm0 hiện “chưa chấm” | Giá trị response và biểu thức render | <code>&#124;&#124;</code>/truthiness đã gộp 0 với null? |
| Thỉnh thoảng trùng bài nộp | Hai request đồng thời + UNIQUE | Check-then-insert không đủ atomic? |
| Dữ liệu dài làm vỡ card | Computed/min-width/Grid/content | Min-content, width cố định hay từ dài? |

Với mỗi lỗi, nộp báo cáo: bước tái hiện, tài khoản/phạm vi giả lập, bằng chứng
đã làm sạch secret, nguyên nhân, diff và test giữ lỗi không quay lại.

## 3. Debugger và log dùng khác nhau

Breakpoint giúp dừng một lần chạy để xem stack và biến. Log giữ dấu vết qua
nhiều request/process. Log nên có request_id, hành động, resource_id phù hợp,
status và elapsed time. Không ghi toàn bộ request login, Authorization, hash
mật khẩu hoặc bài làm riêng tư vào log chỉ để tiện debug.

Repo có Loguru, nhưng import logger chưa tạo chiến lược quan sát. Trong repo
học, thêm log trước/sau service một lần, gây lỗi có chủ đích và tìm đúng trace.
Khi trả lỗi500, client nhận thông báo phù hợp/mã tra cứu; stacktrace ở server.

## 4. Threat model nhỏ trước checklist lớn

Tài sản: tài khoản, bài nộp, điểm, file, quyền cô/admin. Tác nhân: người chưa
đăng nhập, học sinh lớp khác, tài khoản bị khóa, cô không phụ trách. Điểm vào:
API list/detail/update/download/export/WebSocket; không chỉ trang giao diện.

| Nguy cơ | Cách học và kiểm |
|---|---|
| Đọc chéo bài bằng đổi id | Server kiểm quan hệ actor–resource; test cả list/detail/file |
| SQL injection | Truy vấn parameterized/ORM; không ghép input vào SQL string |
| XSS | Render text theo cơ chế framework; sanitize HTML khi có nhu cầu rich text |
| CSRF với cookie auth | Xét credential gửi tự động, SameSite/origin/token theo kiến trúc |
| JWT sai/hết hạn | Xác minh signature/algorithm/expiry; kiểm user active và quyền |
| Credential stuffing | Giới hạn thử, giám sát, thông báo phù hợp; không tự khóa hàng loạt tùy tiện |
| Upload nguy hiểm | Size/type/content policy, storage_key server, quyền tải và cleanup |
| Lộ secret | Không đưa server secret vào VITE_* hoặc git/log/ảnh |
| Cạn tài nguyên | Pagination, giới hạn body/file/rate và thời gian tác vụ |
| Đổi quyền nhầm | Ma trận quyền, backend check, audit, test thu hồi quyền |

XSS và CSRF khác cơ chế; localStorage và cookie có tradeoff. Repo hiện giữ token
trong localStorage. Đó là hiện trạng cần hiểu, không phải kết luận tự động an
toàn nhất. Không tự chuyển kiến trúc auth chỉ bằng một mẹo trong sách.

## 5. Bcrypt và JWT: giải thích bằng dữ liệu

Hash mật khẩu là phép một chiều có salt/cost; verify dùng password nhập với
hash đã lưu. Không “giải mã” hash để lấy password cũ. Giới hạn độ dài theo byte
của bcrypt cần được chốt/test với thư viện đang dùng, kể cả Unicode; không cắt
thầm password. Reset là cấp quyền thay password qua luồng xác minh riêng.

JWT signed thông thường không mã hóa payload: đọc được claim không có nghĩa
sửa được signature. Đừng đặt secret/bài làm vào payload. `exp` hết hạn được
server kiểm; đồng hồ client không cấp quyền. Đổi vai trò/khóa user cần xét thông
tin hiện tại và chính sách thu hồi phiên, không tin mãi role cũ trong token.

## 6. Test nào chứng minh điều gì?

Unit với fake: quy tắc và không sửa dữ liệu khi từ chối. Integration với DB:
mapping, constraints, transaction, query. In-process ASGI: request/schema/
dependency/route/response phối hợp; không chứng minh TCP/reverse proxy. Luồng
trình duyệt: người dùng hoàn thành việc, refresh và đổi tài khoản. Load test:
cần workload và môi trường rõ; một con số RPS đơn lẻ không nói hệ thống tốt.

SQLite hữu ích để kiểm nhanh nhưng không thay MySQL cho collation, locking,
timezone, driver, migration và concurrency. Chương xưởng ghi rõ mức đã test.

## 7. Tình huống phá để luyện

1. Bỏ điều kiện lớp ở endpoint detail: viết test phải bắt được đọc chéo.
2. Đưa commit vào repository đầu tiên của nghiệp vụ hai bước: gây lỗi ở bước 2.
3. Dùng index làm key ở danh sách có reorder: quan sát state của từng hàng.
4. Ném exception trước response, kiểm log không chứa token và DB không đổi.
5. Tạo bài nộp trùng song song trong DB học; giữ UNIQUE và hợp đồng lỗi.

Không sửa sản phẩm thật để thực hiện thí nghiệm phá. Dùng repository học và
fixture giả. Tự kể: tài sản nào được bảo vệ, kiểm ở đâu và bằng chứng nào đủ.

Tài liệu chính: [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/),
[OWASP API Security](https://owasp.org/www-project-api-security/),
[FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/).
