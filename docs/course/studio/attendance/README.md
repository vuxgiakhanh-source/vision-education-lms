# Điểm danh: reference nghiệp vụ và transaction cho G5

Mở [G5](../../G5-tu-lat-cat-den-toan-bo-lms.md) trước. Đây là ví dụ độc lập,
không import vào backend sản phẩm và không tự tạo endpoint/UI trong workshop.
Python chạy ở đây là code thực; bảng API và UI ở G5 là bài nối tiếp người học
tự triển khai sau khi đã làm G3/G4. Không dùng trạng thái của phần chưa viết để
coi toàn module đã chạy.

Từ gốc repo `D:\vision-education-lms`:

```powershell
.\.venv\Scripts\python.exe docs/course/studio/attendance/demo.py
.\.venv\Scripts\python.exe -m unittest discover -s docs/course/studio/attendance -p test_attendance.py -v
```

G6 thêm một bài review: chạy `bad` cố ý tái hiện lỗi và trả exit code1,
chạy `fixed` xác minh cùng fixture. Đây là bài riêng, không đổi policy lưu
điểm danh của G5:

```powershell
.\.venv\Scripts\python.exe docs/course/studio/attendance/review_lab.py bad
.\.venv\Scripts\python.exe docs/course/studio/attendance/review_lab.py fixed
.\.venv\Scripts\python.exe -m unittest discover -s docs/course/studio/attendance -p test_review_lab.py -v
```

`review_lab.py` có lời giải báo cáo sai và bản sửa (late được tính đi học,
excused/unmarked nằm ngoài mẫu số). `renewal_reference.py` là đáp án nghiệp
vụ thuần cho bài chuyển miền gia hạn sách có deadline, giới hạn2 lần và hàng
chờ; không có library API/UI/DB. `test_review_lab.py` kiểm fixture, biên và
quy tắc của cả hai. Đọc [G6](../../G6-tu-lam-va-duoc-phan-hoi.md) trước đáp án.

Yêu cầu: Python và SQLAlchemy đã dùng trong xưởng. Chạy bằng interpreter của
venv đó, không cài thêm package nếu môi trường đã có. Nếu dựng repo học mới,
khai báo SQLAlchemy theo phiên bản đã chọn trong requirements/lock của repo
học, dùng đúng interpreter rồi chạy lại. `ModuleNotFoundError` là lỗi môi
trường, chưa chứng minh thuật toán sai. Code dùng import trực tiếp vì runner
thêm thư mục chứa script vào đường tìm module; chạy từ lệnh trên.

Kết quả demo:

```text
saved revision: 1
retry revision: 1
stale different content: conflict
stored marks: (Mark(student_id=2, status='present'), Mark(student_id=3, status='absent'))
```

`core.py`: actor, dữ liệu bất biến, validate, quyền, xử lý revision/retry.
`storage.py`: hai bảng, snapshot đọc bằng một SELECT, update có điều kiện và
các mark trong cùng transaction. `demo.py`: fixture một buổi với hai học sinh.
`test_attendance.py`: nghiệp vụ, khóa PK/FK/CHECK, rollback, hai snapshot cũ,
nhánh có người ghi xen giữa read và write. Không có tài khoản/token thật.

Danh sách fixture được chốt lúc tạo buổi; `None` nghĩa chưa ghi. Service chỉ
cho giáo viên active đúng `teacher_id` đã gán cho buổi đọc/ghi. Bài lab chưa có
chuyển người phụ trách hay thay roster. Khi ghép sản phẩm, quyền hiện tại phải
được resolve từ dữ liệu lớp/phân công hiện hành; không copy owner ban đầu rồi
coi đó là quyền vĩnh viễn. `class_id/teacher_id/student_id` là fixture số trong
lab, chưa có FK sang bảng user/class của một LMS khác.

Mỗi lần ghi hợp lệ có nội dung đổi tăng revision một. Nội dung y hệt trả trạng
thái hiện tại mà không tăng; thứ tự hàng không có ý nghĩa. Revision cũ với nội
dung khác bị conflict. Không tự ghi đè để giải quyết conflict cho người dùng.

SQLite trong bộ nhớ và các test tuần tự chứng minh kết quả ở cấu hình đó.
Test hai snapshot không phải đo hai transaction MySQL chạy song song. SQLite
lab bật foreign_keys, kiểm PK/FK/CHECK. Muốn đưa vào MySQL phải làm migration,
test transaction/race với engine thật, quyền hiện hành, index và quy mô roster
đã chốt. Không có số capacity, kết quả browser, API, load hay deploy từ suite này.
