# 14 — Quản trị, lịch học, tài liệu, thông báo và cộng đồng

Học sau khi một luồng lớp/giao/nộp/chấm chạy đúng. Dùng lại kiến thức nền và cách
đi từng lát cắt, không mở mỗi chức năng thành một dự án có cấu trúc khác nhau.

## Bài 14.1 — Màn quản trị có hành động và phạm vi rõ

Tách quản trị tài khoản/hệ thống với nghiệp vụ giảng dạy. Mỗi màn viết ma trận:
đối tượng → bộ lọc → hành động → quyền → xác nhận → hậu quả → lịch sử.

Ví dụ danh sách học sinh: tìm theo tên/số điện thoại theo quyền, phân trang ở
server, xem lớp, khóa tài khoản nếu được cấp quyền. Khóa tài khoản không xóa
bài nộp cũ. Khi cho sửa vai trò phải xác minh quyền backend và ghi người sửa.
Không hiển thị mật khẩu đã lưu; reset mật khẩu là một luồng riêng có xác minh,
hết hạn và chính sách phiên cần thiết.

Bulk action phải nói rõ đang chọn hàng ở trang hiện tại hay mọi kết quả lọc.
Import CSV cần kiểm tra cấu trúc, dòng lỗi, trùng trong file và trùng DB; có bản
xem trước và chính sách nhận một phần/toàn bộ. Upload CSV không phải chạy SQL
từ nội dung file. Export chỉ chứa field/phạm vi được phép; cẩn thận công thức
khi xuất dữ liệu người dùng vào spreadsheet.

**Bài AD1:** tự làm danh sách lớp có lọc/phân trang và một hành động được cấp
quyền. Thử thay id, chọn nhiều trang, lỗi giữa quá trình và refresh.

## Bài 14.2 — Lịch học: sự kiện thật trước lịch lặp

Mô hình buổi học đề xuất: id, class_id, starts_at, ends_at, location/link,
status, created_by. Chốt ends_at > starts_at, cách xử lý hủy/dời buổi và phạm
vi cô quản lý. Hiển thị theo timezone thống nhất; truyền ISO có offset hoặc UTC.

Lịch lặp cần phân biệt quy tắc series với buổi đã phát sinh. Khi sửa một buổi,
sửa các buổi sau hay toàn bộ series là ba nghiệp vụ khác nhau. Đừng lưu duy nhất
chuỗi 'thứ 2, 19h' rồi không thể ghi điểm danh một ngày cụ thể.

```text
API tạo buổi: kiểm quyền → kiểm thời gian → kiểm xung đột theo policy → lưu.
API đổi lịch: kiểm quyền/trạng thái → lưu thời điểm mới và lịch sử cần thiết.
Sau commit: tạo/phát thông báo đúng người bị ảnh hưởng.
```

**Bài SC1:** tạo/đổi/hủy một buổi học trước; đọc trên hai tài khoản; xử lý buổi
qua ngày và client hiển thị sai timezone. Chỉ thêm series khi đã chốt quy tắc.

## Bài 14.3 — Điểm danh có khóa và lịch sử

Attendance liên kết session_id/student_id, trạng thái present/late/absent/excused
theo yêu cầu đã duyệt; UNIQUE(session_id, student_id). Người ghi có quyền theo
lớp; người được điểm danh thuộc lớp/buổi theo chính sách lịch sử đã chốt.

```sql
SELECT session_id,
       SUM(CASE WHEN status = 'present' THEN 1 ELSE 0 END) AS present_count,
       SUM(CASE WHEN status = 'late' THEN 1 ELSE 0 END) AS late_count
FROM attendance
WHERE session_id = 30
GROUP BY session_id;
```

Query là minh họa cho bảng bài học, chưa có trong DB repo. Tổng có mặt có bao
gồm đi muộn hay không là định nghĩa báo cáo. Không suy ra điểm danh từ việc em
đã đăng nhập. Sửa điểm danh cần ghi ai sửa/khi nào/lý do nếu sản phẩm yêu cầu.

**Bài AT1:** ghi danh sách điểm danh một buổi; thử gửi lại, học sinh ngoài lớp,
trợ giảng không đủ quyền và lỗi ghi một phần. Chốt atomic hay kết quả từng dòng.

## Bài 14.4 — Tài liệu và tóm tắt theo tuần

Resource gồm metadata: id, class_id, title, kind, storage_key/link, size,
published_at/status, created_by, week/module nếu cần. Tách tên gốc với đường dẫn
lưu; tên file người dùng không được dùng trực tiếp để quyết định đường dẫn hệ thống.

```text
Nhận upload → xác thực/quyền → kiểm dung lượng/loại nội dung theo policy
→ lưu file bằng khóa do server tạo → lưu metadata → trả trạng thái.
Download → kiểm quyền tài nguyên → cấp luồng tải hoặc URL ngắn hạn phù hợp.
```

Chỉ kiểm đuôi file là chưa đủ. Lựa chọn quét file/nơi lưu phụ thuộc loại upload
và môi trường; không thực thi nội dung upload. Nếu file lưu thành công nhưng DB
lỗi hoặc ngược lại, cần cleanup/retry có thể theo dõi. Transaction DB không tự
xóa file ngoài DB. File chưa công bố cũng cần được bảo vệ ở đường tải.

Weekly summary là nội dung có cấu trúc theo chương/tuần, có công thức, tài liệu
và thảo luận; không cần biến tất cả thành PDF. Chốt có phiên bản/nháp và ai sửa.

**RS1:** đăng tài liệu cho lớp, học sinh đúng lớp tải được, lớp khác không; thử
tên dài, loại cấm, quá dung lượng, lỗi lưu và tài liệu nháp.

## Bài 14.5 — Thông báo và công việc nền

Bản đầu có Notification: recipient_id, type, resource_id, created_at, read_at.
Giao bài/đổi lịch là sự kiện tạo thông báo; tải danh sách có phân trang. Đánh dấu
đã đọc phải đúng chủ thông báo, làm lại không tạo tác dụng sai.

Thông báo ngoài hệ thống có thể lỗi. Không để email gửi rồi DB rollback làm
người học nhận bài không tồn tại. Một hướng khi nhu cầu đủ lớn là outbox:

```text
Trong transaction: lưu bài tập và hàng outbox mô tả sự kiện.
Worker: đọc hàng chưa xử lý → gửi → đánh dấu; retry khi lỗi.
Consumer: nhận lại cùng event_id không tạo thông báo trùng.
```

Outbox hỗ trợ phối hợp DB và tác vụ ngoài DB, không tự tạo bảo đảm exactly-once
cho mọi dịch vụ. Cần idempotency, theo dõi lỗi và cách retry. Đừng thêm broker
ngay khi danh sách thông báo qua HTTP đã đáp ứng bản đầu.

**NT1:** thông báo trong ứng dụng, unread count tính đúng khi gửi/đọc lại; dữ liệu
của A không xuất hiện ở B. Sau đó mới học background jobs nếu có tác vụ thật.

## Bài 14.6 — Hỏi đáp dưới bài trước chat trực tiếp

Comment liên kết resource, author, content, created_at, parent_id nếu có trả lời.
Quyền đọc kế thừa quyền bài/lớp; chỉnh/xóa/ẩn và ghim có quy tắc riêng. Phân trang,
giới hạn nội dung, xử lý nội dung nguy hiểm và lịch sử điều chỉnh theo yêu cầu.

Một câu hỏi gắn đúng bài/câu thi thường hữu ích hơn chat chung không có ngữ cảnh.
Làm create/list/reply trước; người dùng refresh vẫn thấy dữ liệu và không đọc
được thread của lớp khác.

**QA1:** hỏi một câu dưới bài, cô trả lời, học sinh thấy; test id ngoài phạm vi,
nội dung trống, xóa tài nguyên và phản hồi đã bị ẩn.

## Bài 14.7 — WebSocket khi cần cập nhật ngay

HTTP thích hợp tải lịch sử và các thao tác bình thường; WebSocket giữ kết nối
để nhận/gửi sự kiện. Kết nối socket vẫn cần xác thực và phân quyền theo room/lớp.
Không cho client tự join một class_id bất kỳ mà không kiểm tra membership.

```text
Kết nối → xác thực → kiểm quyền room.
Gửi tin → kiểm nội dung/quyền → lưu message với id server.
Sau lưu → phát sự kiện đến người có quyền.
Mất kết nối → reconnect có giới hạn → lấy phần lịch sử bỏ lỡ bằng cursor.
```

Chốt thứ tự, nhận lặp, trạng thái đã nhận/đã đọc, giới hạn tốc độ và quyền khi
bị loại khỏi lớp giữa kết nối. Nhiều process cần cơ chế phối hợp sự kiện; dict
socket trong bộ nhớ một process không tự phát đến mọi worker.
Không đưa token vào URL lưu lâu trong log chỉ vì tiện. Thiết kế cơ chế handshake
phù hợp client/server và môi trường triển khai.

**WS1:** room lớp có hai người, reconnect không mất/trùng message hiển thị;
người bị thu hồi quyền không tiếp tục nhận dữ liệu. Đây là bài mở rộng, chưa có
implementation WebSocket production trong giáo án.

## Bài 14.8 — Thành tích, xếp hạng và mục tiêu học

Leaderboard cần định nghĩa thời gian, dữ liệu hợp lệ, lượt nào được tính, cách
xử lý hòa điểm và quyền hiển thị tên. Hall of Fame cần nguồn minh chứng, người
duyệt và chính sách công khai. Không lấy dữ liệu mẫu làm thành tích thật.
Streak phải dựa trên hành động học có ý nghĩa đã chốt, timezone và quy tắc ngày;
đăng nhập không mặc nhiên được tính một ngày học.

**GM1:** tính bảng xếp hạng từ fixture nhỏ có thể tính tay; thử hòa điểm, thiếu
dữ liệu, bài bị hủy/chấm lại và học sinh không muốn công khai hồ sơ.

## Kiểm tra cuối chương

Chọn một module, tự viết đặc tả → dữ liệu → API → service → repository → UI →
test → vận hành. Dùng lại form/list/error và quyền hiện có. Với chức năng chưa
cần ngay, giữ ở backlog thay vì để nút trông như hoàn thiện nhưng không làm gì.

Tham khảo để học tiếp khi thực hành: [FastAPI WebSockets](https://fastapi.tiangolo.com/advanced/websockets/),
[FastAPI UploadFile](https://fastapi.tiangolo.com/tutorial/request-files/).

## Xưởng — Một module mới phải được làm theo thứ tự nào?

Không tạo ngay10màn hình và để nút chưa làm gì. Với mỗi module, đi hết một
hành động nhỏ theo bảy bước: hợp đồng → fixture tính tay → schema/migration →
service/quyền → API → UI → kiểm lỗi/dữ liệu sau lỗi. Dùng phiếu ở bài Tra cứu.

| Module | Endpoint đầu tiên để tự viết | UI cần có | Kiểm thử bắt buộc trong bài |
|---|---|---|---|
| Lịch | POST/GET buổi theo lớp | Form giờ/múi giờ, list và trạng thái hủy | ends<=starts,ngoài lớp,trùng theo policy |
| Điểm danh | PUT danh sách một buổi | Danh sách học sinh,trạng thái,lỗi lưu | Gửi lặp,người ngoài buổi,lỗi một dòng |
| Tài liệu | POST metadata/upload;GET download | File/progress/lỗi/danh sách | Size/type/quyền/lưu file thành công DB lỗi |
| Thông báo | GET của tôi;PATCH read | Badge,list,empty/error | Không đọc của người khác,read lặp |
| Quản trị | GET paginated;PATCH active | Filter,table,confirm,hậu quả | Scope,bulk selection,không tự khóa sai user |
| Hỏi đáp | POST/GET theo resource | Thread,reply,loading/error | Resource ngoài lớp,xóa/ẩn,nội dung trống |
| Realtime | Connect/join/send theo room | Kết nối/reconnect/gửi lặp | Thu hồi quyền,cursor lịch sử,nhiều process |

Method/path cụ thể phải được chốt thống nhất trong contract sản phẩm; bảng
là đề thực hành. Đừng thêm endpoint với danh từ “admin” rồi quên kiểm action.

## Xưởng — Upload đi từ trình duyệt đến storage

Browser chọn File → client kiểm UX cơ bản → FormData multipart → API xác thực/
quyền/giới hạn → storage ghi bằng khóa server → DBmetadata → response → UI.
FormData khác JSON; browser cần boundary đúng, không chép header
Content-Type application/json của request login sang upload. Axios client
chung cần hỗ trợ loại body này theo cấu hình thực tế.

FastAPI multipart cần dependency thích hợp như python-multipart, hiện chưa
có trong requirements đã rà. Khi triển khai, khai báo dependency rõ trong repo
học/sản phẩm theo yêu cầu được duyệt; đọc UploadFile streaming/lifecycle và
giới hạn server/proxy. Không đọc file rất lớn toàn bộ vào RAM chỉ vì ví dụ nhỏ.

Storage_key do server tạo; filename gốc là metadata cần xử lý khi hiển thị/tải.
Không cho path traversal hoặc public URL cố định vô tình bỏ qua quyền lớp.
Nếu storage thành công nhưng commit thất bại, cleanup phải theo dõi và retry
được; nếu cleanup cũng lỗi, log task xử lý chứ không giấu file mồ côi.

**Bài trắng:** tài liệu PDF cho lớp với size tối đa do bạn chốt,role được phép
upload,nháp/công bố và quyền download. Viết cả happy path và ba lỗi storage/DB/
permission. Ghi rõ storage local ở lab chưa đồng nghĩa lưu bền production.

## Xưởng — Import và export có hợp đồng dữ liệu

CSV cần encoding,cột bắt buộc,kiểu,giới hạn số dòng,trùng trong file/trong DB,
quyền gán lớp và policy atomic/partial. Bản preview phải nói đúng số nhận/từ
chối; không được validate một bộ rồi ghi bộ khác sau khi user sửa dữ liệu.
Export chỉ lấy field được phép với cùng scope/filter đã chốt; tránh công thức
được spreadsheet thực thi từ input không tin cậy bằng policy xuất phù hợp.

Viết parser thuần trước API. Fixture có tên tiếng Việt,dòng rỗng,id sai,trùng
và lỗi dòng cuối. Với file lớn, nghĩ streaming/background task,progress và
retry thay vì giữ HTTP mở vô thời hạn. Không cài queue để xử lý một file10dòng
trước khi có nhu cầu và cách quan sát job.

## Xưởng — Notification không bắt buộc realtime ngay

HTTP list+unread count+mark read có thể đủ cho bản đầu. Event tạo trong phạm vi
transaction phù hợp; outbox tách gửi ngoài DB. Worker cần trạng thái pending/
processing/sent/failed,attemptcount,next_retry và cách tránh xử lý trùng theo
hợp đồng. Thiết kế failure case gửi xong nhưng chưa đánh dấu sent.

User đổi lớp/thu hồi quyền trước lúc mở notification: link dẫn resource vẫn
phải kiểm quyền hiện tại. Notification không trở thành giấy phép tải bài vĩnh viễn.
Unread count từ cùng nguồn dữ liệu; không tăng số local vô hạn khi nhận cùng event.

## Xưởng — Hiệu năng và trạng thái khi dữ liệu lớn dần

List cần pagination/filter/sort ở server với allowlist và limit; query theo
scope trước limit. Search debounce hỗ trợ UX nhưng không bảo vệ server trước
spam. Thêm cancellation/ignore response cũ và giới hạn request phù hợp.

Đo query count,elapsed time,payload size và render trước khi tối ưu. Cache cần
key bao gồm actor/phạm vi khi cần và invalidation lúc dữ liệu/quyền đổi;
không chia sẻ cache điểm giữa học sinh vì cùng resourceid. TanStack Query,
Redis hoặc queue chưa là dependency của repo; chỉ bổ sung khi giải quyết một
vấn đề đã quan sát, với hợp đồng/lifecycle/test rõ.

## Xưởng — Phiếu hoàn thành từng module

1. Tự viết đặc tả và các câu hỏi chưa chốt.
2. Tạo schema/fixture và tính một kết quả bằng tay.
3. Thực hiện một endpoint có quyền; gọi từ UI rồi refresh.
4. Dùng hai tài khoản thử scope ở list/detail/write/file khi có.
5. Thử lỗi giữa nghiệp vụ và xác nhận dữ liệu/tác dụng ngoài DB.
6. Thêm một yêu cầu mới; chỉ đúng file/test bị ảnh hưởng và tự sửa.

Khi một module chưa làm được bước3–6, ghi là bài đang học. Checklist là công
cụ hướng dẫn thực hành, không phải implementation đã có sẵn của mọi module.
