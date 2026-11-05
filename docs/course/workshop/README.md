# Xưởng tham chiếu: lớp học và giao/nộp/chấm/công bố

Đọc [chương Xây từ số 0](../21-xay-tu-so-0.md) trước khi mở implementation.
Đây là project học độc lập, không được import vào ứng dụng sản phẩm. Không dùng
database, secret hoặc token thật của repo. SQLite giúp chạy bài đầu; MySQL,
migration, concurrency và vận hành là các checkpoint tiếp theo trong chương.
P0–P5 bổ sung core loop API/React, refactor transaction, script k6, migration
và deployment lab. Mở [P0](../23-san-pham-hoan-chinh.md) sau khi tự làm chương 10.

## Backend

Từ thư mục `docs/course/workshop`, dùng venv backend hiện có:

Khi tạo repo học ở nơi khác, tạo venv riêng và cài `requirements.txt` của xưởng.
File này ghi các dependency trực tiếp theo phiên bản môi trường đã kiểm tra;
chưa phải lock toàn bộ dependency bắc cầu. Khi đó thay đường dẫn interpreter
trong lệnh bên dưới bằng interpreter của repo học.

```powershell
$env:LAB_SECRET = (..\..\..\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(48))")
..\..\..\.venv\Scripts\python.exe -m lms_lab init
..\..\..\.venv\Scripts\python.exe -m lms_lab token --user 1
..\..\..\.venv\Scripts\python.exe -m uvicorn lms_lab.main:app --host 127.0.0.1 --port 8001
```

Lệnh token hiển thị **credential giả của lab** để dùng tại máy học; không ghi
vào tài liệu/export/ảnh. User1 cô,2 học sinh thuộc lớp,3 ngoài lớp,4 bị khóa.
Token hết hạn30 phút. Secret mới làm token cũ không còn hợp lệ. Terminal mới
cần cùng LAB_SECRET để tạo token tương ứng; không xuất secret vào git.

CLI init chỉ cho SQLite và không reset dữ liệu đã có. Muốn tạo token trong
terminal đang chạy server, dùng terminal khác với cùng secret; hoặc tạo các
token fixture cần dùng trước khi chạy server. Không dừng server giữa mỗi request.

## Frontend

Copy `frontend` sang repo học hoặc dùng ngay thư mục này; chạy `npm install`
lần đầu (cần mạng và tạo lockfile/node_modules của project học), rồi `npm run dev`.
Giữ cổng5173 như CORS lab. Mở trang, nhập token fixture và thử tạo lớp. Quyền
được backend thực thi; học sinh nhìn thấy nút tạo để thực hành lỗi403.
Phiên mẫu giữ trong RAM, thay token remount vùng dữ liệu để không giữ dữ liệu
người trước. Đây chưa phải UX auth hoàn chỉnh.

Package tham chiếu dùng cùng nhóm thư viện và có lockfile riêng. Khi đã có
lockfile, dùng `npm ci` để cài tái lập rồi `npm run build` để kiểm strict/build.
Không tự cài hay cập nhật dependency sản phẩm khi đọc sách.

## Core loop trong browser

Với DB SQLite học mới: cô token1 chọn lớp1 giao bài; học sinh token2 thấy/nộp;
cô tải lại và chấm0 với checkbox công bố bỏ chọn; học sinh tải lại chưa thấy
điểm; cô công bố rồi học sinh tải lại thấy0. Token3 không đọc được lớp1.
Refresh xóa token RAM: nhập lại token, dữ liệu đã commit vẫn còn trong SQLite file.
Điểm lab là số nguyên0..10; bài tập giao là công bố ngay, chưa có trạng thái nháp.
Mỗi danh sách tải20hàng; điều khiển page tiếp theo là bài tự làm, không coi
trang đầu là toàn bộ dữ liệu.

Đổi schema cũ không tự migration SQLite: dùng URL file DB học mới hoặc migrate
bản sao đã review, không xóa DB cũ. SQLite trong bộ nhớ + StaticPool chỉ dùng
tests tuần tự; browser dùng SQLite file để các request không dùng chung một
connection đồng thời. MySQL dùng Session/connection riêng và test cạnh tranh.

Source mới: [workflow.py](lms_lab/workflow.py), [Transaction](lms_lab/unit_of_work.py),
[WorkflowPractice.tsx](frontend/WorkflowPractice.tsx), [HTTP/parser](frontend/workflow-api.ts).
Service nộp khóa assignment trên MySQL để giữ retry đơn giản, có thể nghẽn khi
nhiều người cùng nộp một bài. Đây là bài đo/tối ưu P2, chưa có cam kết capacity.

## Toàn bộ kiểm thử và deployment riêng

Venv hiện tại có Alembic; môi trường mới cài thêm `deploy/requirements.txt`
để chạy test migration. Từ gốc repo:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s docs/course/workshop -p "test_*.py" -v
node docs/course/examples/perf-script.test.cjs
```

Tests không dùng Temp của Windows: mỗi test tạo SQLite trong bộ nhớ và hủy
engine. Chúng kiểm commit/rollback bằng Session mới, không chứng minh bền qua
process restart hay concurrency. Trên sandbox Windows có thể cần chạy lệnh
test FastAPI ngoài sandbox vì threadpool bị treo; đó là giới hạn môi trường.

`test_mysql_concurrency.py` mặc định skip. Muốn chạy: tạo DB MySQL trống tên
`lms_concurrency_<moc-rieng>`, cấp URL qua LAB_MYSQL_TEST_URL trong terminal,
chạy test. Nó từ chối DB không rỗng hoặc sai prefix và không tự drop/reset.
Giữ mật khẩu ngoài Git/log; lần sau dùng một DB học mới. Test dùng hai Session
song song, không phải hai lần gọi tuần tự. MySQL kiểm khóa không thay test tải.

Theo [deployment README](deploy/README.md) để dựng React/Nginx/FastAPI/MySQL,
Alembic, fixture, đo k6 và backup/restore. Template CI nằm trong deploy, chưa
cài vào workflow sản phẩm. API container là entrypoint server.py; main.py
vẫn dành cho SQLite học local. Các thông số pool/worker/limit là mẫu để đo.

## Kiểm tra đã chạy được với môi trường hiện tại

Từ gốc repo:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s docs/course/workshop -p test_workshop.py -v
```

Tests thực hiện HTTP qua giao diện ASGI trong process và SQLite tạm, không cần
httpx/pytest hoặc cổng mạng. Chúng không kiểm CORS trong browser, MySQL thật,
TCP, reverse proxy hay toàn luồng frontend. Phạm vi thực tế ghi ở VALIDATION.

Không coi source tham chiếu là bài đã hoàn thành của người học. Tự viết từ
đặc tả, chạy checkpoint, rồi mới so sánh tên/trách nhiệm và cách xử lý lỗi.
