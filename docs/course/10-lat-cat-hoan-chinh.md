# 10 — Tự làm chức năng giao, nộp và chấm bài từ đầu đến cuối

Đây là bài lớn đầu tiên sau nền tảng. Các quy tắc dưới đây là hợp đồng của bài
thực hành, chưa phải quyết định nghiệp vụ đã duyệt cho LMS. Làm từng lát cắt,
không viết hết backend rồi cuối cùng mới thử frontend.

## Bài 10.1 — Chốt một phạm vi có thể kiểm tra

Phiên bản học: bài làm văn bản, một bài nộp cuối, không upload và không nhiều
lượt. Cô tạo bài nháp, công bố cho một lớp, học sinh nộp, cô chấm, công bố điểm.

Quy tắc nộp của ví dụ chạy được:

1. Actor là học sinh active, được xác định bởi backend; không lấy từ body.
2. Bài tập phải tồn tại, học sinh phải là thành viên lớp.
3. Answer trim rồi có độ dài 1–10000 ký tự trong Python.
4. Nếu đã có bài nộp cùng nội dung chuẩn hóa, trả bản cũ, không đổi timestamp.
   Việc thử lại vẫn trả bản cũ khi deadline đã qua hoặc bài đã đóng.
5. Nếu có bài nộp khác nội dung, báo xung đột; chưa hỗ trợ sửa bài trong phiên bản này.
6. Bài nộp mới chỉ được nhận khi published. Giờ server <= due_at được nhận;
   sau due_at bị từ chối. due_at=None nghĩa chưa có hạn theo hợp đồng bài học.
7. Lưu một bản nộp duy nhất theo assignment/student. Ví dụ bộ nhớ chỉ minh họa;
   khi dùng DB cần UNIQUE và xử lý cạnh tranh thật.

Tại sao xem bản nộp cũ trước deadline? Vì request đầu có thể đã được commit
nhưng response bị mất. Gửi lại cùng nội dung không nên tạo thêm bài hoặc đổi
thời điểm. Điều này không cho phép một bài mới được nộp sau hạn.

## Bài 10.2 — Dữ liệu và trạng thái

```text
Assignment: id, class_id, title, content, status, due_at, created_by
Submission: id, assignment_id, student_id, answer, submitted_at
Grade: submission_id, score, feedback, graded_by, graded_at, published_at
Membership: class_id, user_id, member_role và quyền đã chốt
```

Tách trạng thái bài tập (draft/published/closed) với trạng thái chấm/công bố.
Một bài đã nộp nhưng chưa chấm không phải bài chưa nộp. Điểm 0 không phải chưa
có điểm; score=None biểu diễn chưa chấm. Không bắt client tự suy ra mọi trạng
thái bằng cách nhìn chuỗi thông báo.

Quy tắc chấm cần chốt thêm trước khi code: người được chấm, thang điểm, cho
phép sửa hay không, công bố tự động hay thủ công, lưu lý do/lịch sử khi sửa điểm.

## Bài 10.3 — Thiết kế hợp đồng API trước

Tên route là đề xuất cho bài học, chưa tồn tại trong backend hiện tại.

| Yêu cầu | Dữ liệu client gửi | Kết quả dự kiến |
|---|---|---|
| POST /classes/{id}/assignments | title, content, due_at | 201, bài nháp có id |
| POST /assignments/{id}/publish | dữ liệu theo chính sách | Bài published |
| GET /classes/{id}/assignments | page, page_size, filter | Danh sách có phân trang |
| POST /assignments/{id}/submissions | answer | 200, bản nộp được xác nhận, kể cả retry |
| GET /assignments/{id}/my-submission | không có student_id | Bài của current user hoặc trạng thái chưa nộp |
| PUT /submissions/{id}/grade | score, feedback | Kết quả chấm, đúng quyền |

Thống nhất 404/403 cho ngoài phạm vi; 409 cho xung đột trạng thái/nội dung;
422 cho dữ liệu không hợp lệ. Bảng này chưa thay thế thiết kế schema cụ thể.
Tách schema học sinh và giáo viên nếu có field chưa được công bố.

## Bài 10.4 — Làm service thuần trước HTTP

Đọc đặc tả, tự viết SubmitService với repository giả. Hàm nhận actor, assignment id,
answer và now. Trong ứng dụng thật, now do server tạo; truyền vào trong bài học
để test đúng mốc thời gian, không phải cho client được chọn giờ nộp.

```python
from datetime import datetime, timezone

def server_now():
    return datetime.now(timezone.utc)
```

Tự quyết định thứ tự các điều kiện theo hợp đồng phía trên; chạy test trước
khi mở [lời giải domain](examples/domain.py). Dùng datetime aware nhất quán.
Datetime naive so với aware có thể lỗi; không xóa timezone để giấu lỗi dữ liệu.

## Bài 10.5 — Thay fake bằng MySQL

1. Viết migration đã review cho bài tập/bài nộp.
2. Implement cùng thao tác repository bằng Session, không mang dict global vào production.
3. Đặt UNIQUE(assignment_id, student_id).
4. Trong transaction, kiểm tra và ghi; nếu hai request cạnh tranh, xử lý xung đột
   đúng ràng buộc, rollback rồi đọc bản đã có khi phù hợp để so nội dung.
5. Đảm bảo quyền/trạng thái không bị thay đổi giữa kiểm tra và ghi theo mức bảo
   đảm sản phẩm chọn. Khi cần dùng khóa/atomic update/isolation phù hợp và test.
6. Gửi response sau khi commit thành công. Thông báo bên ngoài chỉ phát sinh theo
   cơ chế tránh gửi trùng và không làm request thành công giả.

Fake chạy đúng chưa chứng minh hành vi MySQL, concurrency hoặc migration đúng.
Đây là phần cần kiểm thử tích hợp riêng.

## Bài 10.6 — Lắp router và auth

Router lấy actor từ dependency current user rồi gọi service. Không cho form
gửi student_id và không tin cờ is_teacher từ trình duyệt. Map lỗi service theo
hợp đồng đã chốt; response không trả password hash hoặc ghi chú riêng của cô.

Mỗi thao tác chỉ cần code nhỏ ở router; service giữ quy tắc, repository giữ truy
vấn. Truyền Session nhất quán trong request. Đọc lại cách lắp dependency login
hiện có để đặt module mới theo cùng quy ước, tránh tạo cấu trúc song song tùy hứng.

## Bài 10.7 — Nối frontend và xác nhận trạng thái

Thiết kế trước: loading → detail hoặc error; editing → submitting → confirmed
hoặc failed/unknown. Timeout không chứng minh server chưa lưu.

Handler thực hiện:

```text
Kiểm tra form.
Đặt submitting, ngăn bấm trùng ở UI.
Gọi API bằng client api của repo.
Thành công: nhận bản nộp server xác nhận, cập nhật/refetch dữ liệu liên quan.
Lỗi HTTP đã biết: hiển thị thông báo theo hợp đồng.
Lỗi mạng: báo chưa xác nhận được; cho kiểm tra trạng thái/thử lại an toàn.
Cuối cùng: bỏ trạng thái đang gửi nếu component còn phù hợp.
```

Disable nút chỉ giảm thao tác trùng; tính duy nhất/idempotency thuộc backend/DB.
Khi nộp thành công, cả chi tiết và số bài cần nộp trên dashboard phải nhất quán;
không chỉ đổi màu nút. Reload trang cần lấy trạng thái thật từ server.

## Bài 10.8 — Làm từng lát cắt và tự bảo vệ thiết kế

| Lát cắt | Bằng chứng hoàn thành |
|---|---|
| A: lớp và thành viên | Cô xem đúng lớp; học sinh ngoài lớp bị chặn |
| B: giao bài | Cô tạo/công bố; học sinh lớp đó nhìn thấy sau reload |
| C: nộp bài | Học sinh nộp; cô xem đúng bài; timestamp không đổi khi retry |
| D: chấm/công bố | Cô có quyền chấm; học sinh thấy theo chính sách công bố |
| E: dashboard thật | Task/count lấy từ dữ liệu, không sửa mock để giả thành công |

Với mỗi lát cắt: đặc tả → schema/API → service → repository → router → UI → test.
Không chờ làm hết cả năm lát cắt mới thử bằng hai tài khoản.

## Ma trận nghiệm thu bắt buộc của bài

- Đúng quyền, nội dung hợp lệ, trước hạn: lưu đúng một bản.
- Đúng thời điểm deadline: theo quy tắc inclusive đã chọn.
- Sau hạn và chưa có bản: bị từ chối, không tạo hàng.
- Nội dung trống/dài, lớp khác, tài khoản khóa: bị từ chối và DB không đổi.
- Gửi lại cùng nội dung kể cả sau hạn: trả cùng id/thời điểm.
- Gửi lại nội dung khác: conflict, bản gốc giữ nguyên.
- Hai request đồng thời: kiểm tra bằng DB thật, vẫn đúng ràng buộc và hợp đồng.
- Cô khác lớp hoặc trợ giảng thiếu quyền: không đọc/chấm được bài.
- Điểm 0 được lưu/hiển thị; điểm ngoài thang bị từ chối.
- Chưa công bố: response học sinh không chứa điểm/lời giải bị hạn chế.
- Reload, đổi tài khoản và lỗi mạng: không giữ dữ liệu riêng của người trước.

Qua bài khi tự thực hiện được lát cắt mới có yêu cầu thay đổi. Ví dụ bổ sung nộp
muộn có phép: phải biết sửa quy tắc, dữ liệu, API, UI và test nào; không chỉ đổi if.
