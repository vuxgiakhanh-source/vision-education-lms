# P0 — Từ yêu cầu đến một sản phẩm có thể nghiệm thu

Học sau chương 10 và xưởng. Đầu ra: một luồng giao → nộp → chấm → công bố
chạy bằng nhiều tài khoản, có dữ liệu thật trong DB học và có bằng chứng lỗi.
Những quy tắc dưới đây là hợp đồng lab, chưa tự thay yêu cầu sản phẩm thật.

## 1. Đổi “hoàn chỉnh” thành một phạm vi có thể kiểm

Hoàn chỉnh phải gắn với phiên bản. Viết một trang gồm: ai dùng, công việc họ
muốn xong, dữ liệu được giữ, điều cấm, quy mô dự kiến và điều chưa làm.

Ví dụ bản 0.1: cô giao bài văn bản cho lớp; học sinh nộp một bản cuối; cô chấm
điểm nguyên 0..10 rồi quyết định công bố. Không sửa bài đã nộp, không upload,
không ngân hàng đề và không nháp bài tập trong lát cắt này. Giao bài là công bố
ngay. Đổi quy tắc này cần schema/API/UI/test tương ứng.

| Câu hỏi | Quyết định lab | Cách phản chứng |
|---|---|---|
| Ai giao/chấm? | Cô sở hữu lớp | Token cô khác biết id vẫn không đọc/chấm được |
| Ai nộp? | Học sinh active là thành viên | Cô hoặc học sinh lớp khác bị từ chối |
| Hạn dựa đồng hồ nào? | Giờ UTC server; bằng hạn vẫn được | Sửa đồng hồ browser không kéo dài hạn |
| Mất response rồi gửi lại? | Cùng nội dung trả bản cũ | Id/timestamp không đổi, chỉ một row |
| Gửi nội dung khác? | 409, giữ nguyên bản gốc | Đọc DB bằng Session mới |
| Khi nào thấy điểm? | Sau publish; thu hồi sẽ ẩn lại | Kiểm JSON của học sinh, không chỉ text UI |

Từ bảng này viết acceptance test trước khi thêm màn hình. Một nút hiện đẹp
không chứng minh hậu quả của nó đã được lưu và được bảo vệ.

## 2. Chọn kiến trúc và vẽ ranh giới

Bản đầu dùng một backend có module rõ, một DB và frontend riêng. Ghi quyết
định vào ADR ngắn: vấn đề → các lựa chọn → lựa chọn → hậu quả → lúc xét lại.

```text
React form → workflow-api.ts → HTTP + DTO
 → router + current_user → WorkflowService
 → WorkflowRepository + Transaction → MySQL
```

Router dịch giao thức/status; service điều phối quyền và nghiệp vụ; repository
giữ query; DB giữ FK/UNIQUE/CHECK. Frontend kiểm input để giúp người nhập,
server vẫn quyết định. Không thêm microservices để chứng minh kiến trúc tốt;
hãy chứng minh thay một rule không phải sửa ngẫu nhiên khắp hệ thống.

Trong [workflow.py](workshop/lms_lab/workflow.py), schema/router/DTO/repository/
service được đặt cùng file để đọc hết một lát cắt. Khi file khó điều hướng,
tách theo module assignments/submissions; giữ dependency hướng rõ. Đây là bài
tổ chức lại có test bảo vệ ở P1, không phải quy ước mọi module phải chung file.

## 3. Thiết kế dữ liệu và trạng thái trước UI

```text
users ─ classes.teacher_id
classes ─ memberships ─ users(student)
classes ─ assignments ─ submissions ─ users(student)
```

Submission có UNIQUE(assignment_id, student_id), answer, submitted_at, score
nullable, grade_published. Điểm 0 là giá trị; null là chưa có/chưa được xem theo
DTO. Foreign key student_id chỉ chứng minh user tồn tại, không chứng minh user
thuộc lớp. Membership được service kiểm trước khi nộp.

Assignment.due_at trong DB là UTC không kèm tzinfo theo hợp đồng. Input bắt
buộc offset nếu có thời điểm; output thêm UTC offset. Nếu chuyển sang policy
khác, cần đổi cả schema, truy vấn, serialize và tests; không thêm bảy giờ tùy chỗ.

| Trạng thái | Hành động | Kết quả |
|---|---|---|
| Chưa có bài nộp, chưa quá hạn | Nộp | Tạo một bản |
| Đã có cùng nội dung | Nộp lại | Trả bản cũ, kể cả đã quá hạn |
| Đã có khác nội dung | Nộp lại | 409 |
| Chưa chấm | Cô lưu điểm, publish=false | Cô thấy điểm; học sinh nhận null |
| Đã chấm | Cô publish=true | Học sinh thấy cả điểm 0 |
| Đã công bố | Cô lưu publish=false | Thu hồi hiển thị theo policy lab |

Lab chưa lưu lịch sử thay đổi điểm. Nếu cần audit, thêm GradeRevision và actor/
timestamp/reason trong cùng transaction; không coi log HTTP là sổ lịch sử điểm.

## 4. Dựng lab chạy thật theo thứ tự

Làm theo [README xưởng](workshop/README.md). Dùng DB học mới vì schema mới thêm
assignments/submissions. Bản SQLite cũ có thể thiếu bảng; không xóa DB cũ để
chữa lỗi. Chọn URL SQLite mới hoặc thực hành migration trên một bản sao riêng.

1. Tạo LAB_SECRET, init fixture và tạo token cô 1, học sinh 2, ngoài lớp 3.
2. Chạy API ở 8001, React ở 5173; dùng hai browser profile để giữ hai phiên.
3. Cô chọn lớp 1, giao một bài; copy id từ response, refresh vẫn thấy.
4. Học sinh 2 chọn lớp 1, nộp `A`; refresh vẫn có bản nộp và giờ server.
5. Cô tải lại bài, lưu điểm 0 chưa công bố. Học sinh tải lại: JSON score=null.
6. Cô công bố. Học sinh tải lại: score=0. Dùng token 3 gọi API trực tiếp: 404.

UI tham chiếu là [WorkflowPractice.tsx](workshop/frontend/WorkflowPractice.tsx),
HTTP/parser là [workflow-api.ts](workshop/frontend/workflow-api.ts). Token chỉ
giữ RAM; đổi token remount vùng dữ liệu. Đây là workbench fixture, chưa phải
login/onboarding của sản phẩm. Các bài P3/P4 yêu cầu thay cơ chế fixture trước
khi cho người thật sử dụng.

## 5. Theo một lần nộp qua từng lớp

Đọc theo đường: submit form → submitAnswer → AnswerInput trim/length → actor
từ token/DB → WorkflowService.submit → khóa assignment → kiểm scope → đọc
bản nộp hiện tại → kiểm deadline khi tạo mới → add/flush → DTO → commit → UI.

Service tạo DTO trước commit nhưng chỉ return sau commit thành công. Nếu lỗi
flush/commit, rollback rồi ném lại. Trường hợp exception sau flush được test
bằng Session khác để xác nhận không còn row, không chỉ assert rollback được gọi.

Trên MySQL, khóa assignment tuần tự hóa việc nộp trong cùng bài. Đây là lựa
chọn đơn giản để học correctness; có thể trở thành nút nghẽn khi cả lớp nộp.
UNIQUE vẫn giữ invariant. P2 yêu cầu đo và thiết kế thay thế bằng constraint/
conflict handling hay cơ chế phù hợp, rồi test cạnh tranh thật. SQLite không
chứng minh SELECT FOR UPDATE đã có hiệu lực.

## 6. Ma trận nghiệm thu có thể chạy

| Tình huống | Status/response | Bằng chứng DB |
|---|---|---|
| Thiếu token | 401 | Không ghi |
| User khóa | 403 | Không ghi |
| Học sinh ngoài lớp nộp | 404 | Không có bài của người đó |
| Cùng bài, cùng answer đã trim | 200, id/giờ cũ | Một row |
| Cùng bài, khác answer | 409 | Nội dung cũ giữ nguyên |
| Mới nộp sau hạn | 409 | Không tạo row |
| Điểm -1, 11, bool, 2.5 hoặc chuỗi | 422 | Điểm cũ giữ nguyên |
| Cô lớp khác chấm | 404 | Điểm không đổi |
| Chưa công bố | score=null cho học sinh | Cô vẫn đọc được điểm thật |
| Exception sau INSERT | Lỗi server | Session mới không đọc được row |

Chạy `test_workflow.py` và `test_workshop.py` theo README. Đây là ASGI + SQLite
trong bộ nhớ, chưa phải browser/MySQL/TCP test. Nộp thêm video/bước thao tác,
Network đã ẩn token và kết quả MySQL ở môi trường riêng.

## 7. Hoàn thiện từng module còn lại bằng cùng khuôn

Chương 14 nêu module. Với mỗi module, tạo thư mục bằng chứng gồm specification,
ERD, API contract, permission matrix, tests, UI state và runbook. Làm xong một
hành động trước khi mở thêm nhiều màn.

| Module | Luồng đầu tiên | Điều kiện chưa được bỏ |
|---|---|---|
| Tài khoản | Tạo → đăng nhập → đổi/quên mật khẩu | Xác minh, hạn token, thu hồi phiên, audit |
| Thành viên | Thêm → đọc lớp → rời lớp | Quyền người thêm, trùng, lịch sử sau rời |
| Luyện thi | Phát đề → lưu tiến độ → nộp/chấm | Version câu hỏi, giờ server, không lộ đáp án |
| File | Upload nháp → công bố → tải | Streaming/limit, private storage, cleanup khi DB lỗi |
| Lịch/điểm danh | Tạo buổi → ghi → sửa | Timezone, người ngoài buổi, lịch sử sửa |
| Thông báo | Tạo event → phát → đọc | Outbox, nhận lặp, retry, quyền khi mở link |
| Quản trị | Lọc → bulk action → audit | Scope, lỗi từng dòng, hậu quả có thể giải thích |

## 8. Bài tự xây và điều kiện qua

**Điền:** thêm nút phân trang assignments/submissions, reset page khi đổi lớp,
thử trả response ngược thứ tự; tổng kết quả không được lẫn tài khoản trước.

**Trắng:** thêm “nháp → công bố bài tập”. Tự quyết schema/migration/quyền/list
và bảo vệ download/submission của bài nháp. Không chỉ ẩn một card trong React.

**Sửa lỗi:** người khác bỏ filter lớp hoặc trả score thẳng ORM. Test phải đỏ
trước khi sửa, xanh sau sửa; chứng minh bằng API học sinh ngoài lớp và JSON.

Qua khi một người khác chạy README, tự hoàn thành luồng bằng hai tài khoản,
và mày tự xử lý được biến thể. Lab là mẫu đối chiếu cho luồng cốt lõi, chưa
phải implementation trọn mọi module của LMS.
