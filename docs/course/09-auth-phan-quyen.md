# 09 — Đăng nhập và quyền truy cập dữ liệu

## Bài 09.1 — Hai câu hỏi phải tách rõ

Xác thực: người gửi request là ai? Phân quyền: người đó được làm gì với tài
nguyên cụ thể? Token hợp lệ của học sinh A không cho A đọc bài nộp của B.

Luồng hiện có: bcrypt kiểm tra mật khẩu, JWT chứa id/role/exp, frontend lưu
access_token, Axios gắn Bearer token, dependency đọc id. `/me` kiểm tra tài khoản
còn tồn tại và active. Dashboard còn ngoài guard và dùng mock; enum vai trò
chưa phải cơ chế phân quyền hoàn chỉnh.

## Bài 09.2 — Đọc JWT đúng nghĩa

- Hash mật khẩu là cơ chế một chiều phù hợp để kiểm tra; không giải mã hash.
- JWT ký giúp xác minh tính toàn vẹn và bên ký. Payload thông thường đọc được,
  không đặt mật khẩu hoặc bí mật vào payload.
- Xác minh chữ ký, thuật toán cho phép và hết hạn; các claim khác phụ thuộc hệ thống.
- Đọc role từ localStorage hoặc decode token ở frontend không đủ để cấp quyền.
- Nếu tài khoản bị khóa/đổi quyền sau khi token cấp, policy phải quyết định
  kiểm tra trạng thái hiện tại hoặc cơ chế thu hồi; không coi claim cũ luôn là sự thật mới.

Đọc `security.py` và `dependencies.py` rồi tự chỉ ra repo đang kiểm tra gì và
chưa kiểm tra gì. Không tự thay thuật toán hoặc cách lưu token chỉ vì ví dụ khác.

## Bài 09.3 — Current user là dữ liệu đáng tin từ backend

Endpoint nộp bài nên nhận assignment_id và answer từ client, còn student_id lấy
từ người dùng đã xác thực. Không nhận user_id từ form rồi tin đó là chủ bài nộp.

Một dependency tương lai cần: xác minh token → lấy user DB → kiểm tra tồn tại,
active và chính sách bắt đổi mật khẩu → trả user cho service. Dùng response
401/403 theo hợp đồng đã chốt; không trả hashed_password.

Trong frontend, trạng thái có thể gồm đang kiểm tra phiên, chưa đăng nhập, cần
đổi mật khẩu, đã đăng nhập và lỗi tạm thời. Một lỗi mạng của `/me` không nhất
thiết là token sai; xử lý 401 khác lỗi mạng, tránh vòng redirect vô tận.

## Bài 09.4 — Quyền toàn hệ thống và quyền theo lớp

Giả định học tập, cần người dùng duyệt trước khi triển khai:

| Hành động | Quy tắc |
|---|---|
| Tạo lớp/phân công | Admin hoặc người có capability đã cấp |
| Giao bài | Giáo viên được phân công vào lớp |
| Nộp bài | Học sinh là thành viên lớp của bài |
| Xem bài nộp | Chủ bài nộp hoặc người được chấm trong lớp |
| Chấm bài | Cô hoặc trợ giảng được giao quyền, đúng lớp |
| Công bố điểm | Người có quyền công bố, không suy ra từ quyền xem |
| Thay vai trò tài khoản | Quản trị tài khoản, không cấp mặc định cho cô |

Từ chối theo mặc định khi không có quyền rõ. Không cho admin tự động làm mọi
hành vi học tập nếu yêu cầu chưa chốt. Quyền trợ giảng cần phân biệt điểm danh,
trả lời, chấm và sửa đề; một bool is_teacher không diễn đạt đủ mọi trường hợp.

## Bài 09.5 — Kiểm tra tài nguyên và phạm vi

Tư duy cho yêu cầu đọc bài nộp:

```text
Lấy user hiện tại từ auth.
Tìm bài nộp, bài tập và lớp tương ứng.
Nếu là chủ bài: kiểm tra quyền xem theo trạng thái.
Nếu là người chấm: kiểm tra quan hệ với lớp và capability.
Nếu không thuộc trường hợp được phép: từ chối.
Chỉ trả các field phù hợp, bao gồm chính sách công bố điểm/lời giải.
```

Kiểm tra tương tự cho file download, export báo cáo, endpoint danh sách và
endpoint chi tiết. Chỉ bảo vệ nút ở UI hoặc route cấp trang không ngăn HTTP
request thủ công. Lọc scope ngay ở query khi phù hợp, vẫn giữ quy tắc rõ ở service.

## Bài 09.6 — Bộ tình huống kiểm thử

Chuẩn bị dữ liệu test riêng: học sinh A/B cùng lớp, C khác lớp; cô X phụ trách,
cô Y khác lớp; trợ giảng Z có quyền giới hạn; tài khoản bị khóa; token hết hạn.

- A nộp bài của lớp mình: thành công nếu đúng quy tắc.
- A thay id để xem bài B: bị từ chối.
- C mở bài lớp khác qua URL và file đính kèm: bị từ chối.
- Y chấm bài lớp X: bị từ chối.
- Z chỉ có quyền điểm danh: không công bố điểm.
- Token lỗi/hết hạn: không thay đổi DB, frontend đưa ra trạng thái đúng.
- Tài khoản bị khóa sau login: xử lý đúng policy đã chốt.

Không dùng token thật trong tài liệu, ảnh hoặc commit. Repo hiện lưu token
localStorage; hiểu rủi ro XSS của cách này. Nếu đổi sang cookie HttpOnly, phải
thiết kế cả CSRF, SameSite và CORS liên quan, không coi đổi chỗ lưu là giải quyết mọi việc.

## Bài tự viết

- **AUTH1:** sơ đồ phiên từ login → `/me` → refresh trang → logout.
- **AUTH2:** bảng quyền cho 4 vai trò và mỗi thao tác của lớp/bài nộp.
- **AUTH3:** service kiểm tra membership, không lấy danh tính từ body.
- **AUTH4:** viết các test truy cập chéo phía trên, kiểm tra DB không đổi khi bị từ chối.
- **AUTH5:** xác định trang preview UI nào được public và trang dữ liệu thật nào phải bảo vệ.

Qua chương khi tự giải thích được mỗi quyết định cho phép/từ chối và chứng minh
bằng test. Quên mật khẩu, thu hồi phiên và giới hạn đăng nhập là bài thiết kế riêng;
chưa có code hoàn chỉnh trong giáo án để mang dùng thật.

Tham khảo: [FastAPI security](https://fastapi.tiangolo.com/tutorial/security/),
[OWASP Authorization](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html).

## Xưởng — Ma trận trước guard

| Hành động | Học sinh | Cô | Trợ giảng | Admin |
|---|---|---|---|---|
| Đọc bài nộp | Chủ bài theo policy | Lớp được phân công | Capability được cấp | Không tự suy từ tên role |
| Giao/chấm | Không | Lớp được phân công | Chỉ khi được cấp | Theo quyền nghiệp vụ đã chốt |
| Điểm danh | Phạm vi tự xem | Lớp được phân công | Nếu được giao | Theo quyền đã chốt |
| Khóa tài khoản | Không | Không mặc định | Không mặc định | Quyền quản trị phù hợp |

Đây là khung cần chốt cho sản phẩm. Role toàn hệ thống chưa đủ: xét
`actor,action,resource,context`. Current user id từ token chưa chứng minh
còn active hoặc thuộc lớp. Nested /classes/7/assignments/10 cần kiểm bài 10
thực sự thuộc lớp 7, không chỉ kiểm user thuộc lớp 7.

## Xưởng — Login, phiên và những luồng tiếp theo

Form → API login → tìm user → verifyhash → active → ký token → client giữ phiên
→ Authorization → server verify → user hiện tại → quyền tài nguyên. Mỗi bước có
lỗi riêng. Kiểm cùng scope ở list/detail/update/download/export/WebSocket.

Logout client không tự thu hồi JWT còn hạn. Refresh/revocation cần policy về
rotation,storage,expiry và concurrency. Must_change_password cần server chặn
hành động phù hợp, không chỉ điều hướng frontend. Quên mật khẩu cần identity
verification,token một lần/hết hạn,giới hạn thử,response không lộ tài khoản.
Reset admin cần quyền,audit và policy phiên; không gửi password plain qua thông báo.

**Điền:** kiểm active từ DB sau decode. **Trắng:** test2 lớp/4 vai trò theo ma trận
đã chốt. **Sửa lỗi:** user bị khóa vẫn ghi bằng tokencũ; sửa ở server và giữ test
request trực tiếp, không chỉ logout UI.
