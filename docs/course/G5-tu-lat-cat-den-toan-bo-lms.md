# G5 — Từ một lát cắt đến tự xây các phần còn lại của LMS

Mày đã làm một luồng có UI, HTTP, Python và DB ở G1–G4. Bây giờ đổi bài toán:
**điểm danh một buổi**. Không đổi tên Class thành Attendance rồi coi là xong.
Điểm danh có danh sách lịch sử, trạng thái chưa ghi, ghi nhiều hàng cùng lúc
và hai tab tranh nhau lưu. Ta sẽ suy ra thiết kế từ những khác biệt đó.

Đi theo ba mức: điểm danh có bài làm mẫu và code tham chiếu; tài liệu có khung
với chỗ để tự quyết định; thông báo có đề trước, gợi ý sau. Mỗi phiên dưới đây
chỉ tạo một đầu ra. Nếu chưa giải thích được đầu ra đó, giữ ở phiên hiện tại.

Reference chạy thật ở [studio/attendance](studio/attendance/README.md) gồm
Python nghiệp vụ, SQLAlchemy và tests. Nó chưa có màn điểm danh hay API chạy
sẵn. Các hợp đồng API/UI dưới đây là bài nối tiếp từ phần HTTP/React đã học,
không phải danh sách endpoint đang tồn tại trong backend sản phẩm.

## Phiên 1 — Biến “cô muốn điểm danh” thành quy tắc đủ để code

**Đầu ra:** một trang đặc tả phiên bản đầu, gồm cả quyết định và câu chưa chốt.

Người dùng nói: “Cô muốn ghi em nào có mặt trong buổi học.” Nếu lập tức tạo
`student.attended = true`, ta đã âm thầm chọn một mô hình sai: một học sinh
có nhiều buổi; có mặt hôm nay không nói gì về tuần trước.

Hỏi theo tình huống cụ thể thay vì hỏi chung “muốn hệ thống thế nào?”:

| Câu hỏi cần hỏi | Quyết định dùng trong bài học | Hệ quả lên code |
|---|---|---|
| Điểm danh theo lớp hay theo buổi? | Theo một buổi của một lớp | Mỗi hàng có sheet/buổi và student |
| Chưa ghi có tính là vắng không? | Không | Cần `null` khác `absent` |
| Có đi muộn/vắng có phép không? | Có: present/late/absent/excused | Bốn giá trị hợp lệ, không boolean |
| Ai được ghi? | Giáo viên active được phụ trách buổi | Actor do auth xác định, không lấy từ body |
| Đổi thành viên sau buổi thì sao? | Danh sách buổi được chốt khi tạo | Cần snapshot roster; không JOIN mọi thành viên hiện tại để dựng lại quá khứ |
| Một dòng lỗi thì các dòng trước có lưu không? | Cả buổi thành công hoặc không đổi | Validate hết trước ghi; một transaction |
| Hai tab cùng sửa? | Bản cũ bị báo xung đột, không ghi đè | Cần revision phía server |
| Gửi lại đúng nội dung sau mất response? | Trả trạng thái đã lưu, không tạo thay đổi mới | Retry cùng nội dung là no-op |

Đây là quyết định lab, chưa thay cho việc hỏi giáo viên thật. Giới hạn bản đầu:
1–100 học sinh/buổi, một người phụ trách, chưa chuyển người phụ trách, chưa
sửa roster lịch sử, chưa đóng khóa buổi và chưa báo cáo học sinh qua nhiều tháng.
Giới hạn giúp mày hoàn thành một vấn đề rõ; mở rộng sẽ có bài ở G6.

**Dự kiến:** mày giải thích được vì sao `attended: bool` thiếu thông tin.
**Nếu kẹt:** kể một học sinh đi học thứ Hai nhưng vắng thứ Tư. Nếu thiết kế
không lưu đồng thời được cả hai sự thật, quay lại xác định “một hàng đại diện
cho cái gì”. Đọc đúng đoạn [trạng thái và dữ liệu ở chương 10](10-lat-cat-hoan-chinh.md#bài-102--dữ-liệu-và-trạng-thái).

## Phiên 2 — Tính kết quả bằng tay trước khi viết bảng

**Đầu ra:** fixture nhỏ và bảng kết quả của năm thao tác.

Giả sử lớp 7 có giáo viên 1, học sinh 2 và 3. Buổi điểm danh có id 42. Lúc
tạo buổi, chốt roster `[2, 3]`; mọi trạng thái là `null`, revision bằng 0.
Revision là số phiên bản dữ liệu, tăng mỗi lần nội dung thực sự đổi. Nó không
phải số request và không phải ngày giờ.

| Bước | Request/việc xảy ra | Kết quả phải có |
|---|---|---|
| A | Tab A đọc buổi | Revision 0; cả hai chưa ghi |
| B | A gửi revision 0: 2 present, 3 absent | Revision 1; lưu cả hai |
| C | A mất response rồi gửi lại đúng nội dung, revision vẫn 0 | Trả revision 1; dữ liệu không đổi |
| D | Tab B đang giữ revision 0 gửi 2 late, 3 absent | Conflict; không đổi thành late |
| E | B tải lại revision 1, quyết định sửa rồi gửi revision 1 | Revision 2; lưu quyết định mới |

Đảo thứ tự hai hàng trong request không làm đổi ý nghĩa. Gửi học sinh 2 hai
lần là dữ liệu sai, không phải cách chọn “dòng sau thắng”. Gửi 2 nhưng bỏ 3
cũng sai vì phiên bản API này ghi **toàn bộ buổi**, không ghi từng phần.

Tự thêm ba dòng: student 9 không thuộc roster; status trống; actor là học sinh.
Với cả ba, ghi chính xác DB sau request: giống trước request.

**Dự kiến:** mày có thể dùng bảng này làm test mà chưa có UI.
**Nếu kẹt:** đừng đọc tiếp SQL. Dùng hai tờ giấy làm hai tab và một tờ làm DB.
Chỉ tăng revision trên tờ DB khi dữ liệu mới được chấp nhận. Sửa UI hay disable
nút không ngăn được tab khác gửi request cũ.

## Phiên 3 — Từ câu nói sang dữ liệu, rồi mới chọn file

**Đầu ra:** sơ đồ hai bảng và ba ví dụ dữ liệu hợp lệ/không hợp lệ.

Ta cần một đối tượng cho toàn buổi và một hàng cho từng học sinh trong buổi:

```text
AttendanceSheet: id, class_id, teacher_id, revision
AttendanceMark: sheet_id, student_id, status

Sheet 42 ── nhiều Mark
Mark (42, 2) chỉ tồn tại một lần
Mark.status = null | present | late | absent | excused
```

`teacher_id` trong reference là người được gán cố định của buổi lab. Khi ghép
LMS có chuyển phân công, phải kiểm quyền từ phân công **hiện hành** theo policy,
không coi owner đã copy lúc tạo là quyền vĩnh viễn. Reference chưa cài chuyển
phân công; không dùng nó để kết luận phần quyền đó đã hoàn thành.

Tại sao không đặt `student_ids` trong một cột chuỗi? Khi cần sửa đúng một học
sinh, đặt ràng buộc duy nhất hoặc đếm có mặt, các hàng riêng cho phép DB kiểm
và truy vấn rõ. Một JSON có thể phù hợp vài bài toán, nhưng ở đây nó không cho
ta ràng buộc từng cặp bằng primary key theo cách đang học.

Ràng buộc phân trách nhiệm:

| Ràng buộc | Ai giữ và tại sao |
|---|---|
| Một mark cho một người/buổi | Primary key `(sheet_id, student_id)` chống cả ghi ngoài service |
| Mark thuộc buổi có thật | Foreign key tới sheet |
| Status thuộc tập cho phép hoặc null | Service báo lỗi dễ hiểu; CHECK là lớp bảo vệ DB |
| Gửi đúng và đủ roster | Service so tập id với snapshot; FK một mình không biết roster |
| Một lần ghi toàn buổi | Transaction bao cả revision và các mark |
| Không mất sửa của tab khác | UPDATE có điều kiện revision, không chỉ `if` trước ghi |

Trong sản phẩm, `class_id/student_id` còn có FK sang class/user. Lab tách riêng
nên dùng fixture số, không nối DB của repo sản phẩm. Tạo buổi thật phải lấy
membership hợp lệ phía server và chụp roster trong cùng ranh giới ghi đã chọn;
không nhận danh sách “học sinh của lớp” do trình duyệt tự khai.

Sau khi hiểu dữ liệu, mới chọn nơi đặt code:

```text
attendance/
  core.py             dữ liệu và quy tắc, không biết HTTP/SQL
  storage.py          hai bảng, đọc snapshot, ghi atomic
  demo.py             lắp đối tượng và thử một câu chuyện
  test_attendance.py  bằng chứng đúng/sai
```

Đây là cấu trúc đủ nhỏ cho bài. Chưa tách mỗi dataclass thành một file vì chưa
có trách nhiệm riêng đáng kể. Khi thêm HTTP/UI, thêm adapter tương ứng; không
đưa status HTTP vào core chỉ vì lỗi nghiệp vụ xuất hiện từ request.

**Dự kiến:** mày nói được một constraint không thay được quyền và một điều
kiện quyền không thay được constraint.
**Nếu kẹt:** đọc phần FK/UNIQUE/transaction ở [SQL](06-sql.md), rồi tự viết
một cặp mark trùng. Đọc đúng phần Session ở [SQLAlchemy](08-sqlalchemy.md)
khi cần hiểu `Session.begin`, không phải học toàn bộ ORM mới được thử bài.

## Phiên 4 — Viết quy tắc bằng Python trước, theo dấu từng nhánh

**Đầu ra:** tự dựng và chạy được phiên bản tương đương `core.py`, rồi giải
thích luồng save mà không mở đáp án.

Mở [core.py](studio/attendance/core.py) sau khi đã viết phác thuật toán từ
fixture. Bốn lỗi có tên riêng: `InvalidInput`, `Forbidden`, `NotFound`,
`Conflict`. Chúng giúp tầng HTTP phân biệt lỗi nhập, quyền và bản đã cũ.

`@dataclass(frozen=True)` tạo các đối tượng dữ liệu có field rõ và không cho
gán lại field. `Mark(2, 'present')` tương đương cách nghĩ một record có hai
field, không phải một thư viện điểm danh. `tuple` giữ danh sách snapshot bất
biến. Ta chọn chúng để việc kiểm tra thất bại không âm thầm sửa bản đang lưu.
Nếu lạ decorator/class, thử tự viết một class có `__init__` nhận hai field
trước; xem [Python OOP](05-python-oop.md) tại đoạn class/composition.

Thuật toán đã suy ra:

```text
1. Xác minh actor được đọc/ghi buổi.
2. Kiểm revision đúng kiểu; kiểm mọi hàng, trùng id, đủ roster, status.
3. Chuẩn hóa thứ tự theo student_id để so nội dung, không so thứ tự nhập.
4. Nếu giống dữ liệu hiện tại: trả dữ liệu hiện tại, không ghi.
5. Nếu revision cũ: Conflict.
6. Chuẩn bị snapshot mới, revision tăng 1.
7. Nhờ store ghi khi revision vẫn bằng bản vừa đọc.
8. Nếu request khác đã thắng: đọc lại; cùng nội dung thì trả bản đó,
   khác nội dung thì Conflict.
```

Một lỗi dễ bỏ sót nằm trước bước chuyển list thành dict:

```python
ids = [mark.student_id for mark in marks]
if len(set(ids)) != len(ids):
    raise InvalidInput('Trung hoc sinh trong request')
```

Nếu tạo `{mark.student_id: mark.status for mark in marks}` ngay, dòng sau đã
ghi đè dòng trước và bằng chứng trùng mất. `set(ids)` giữ id duy nhất;
so hai độ dài phát hiện trùng. `type(value) is int` ở revision/id từ chối cả
`True`, vì trong Python `isinstance(True, int)` là True nhưng True không phải
một revision mà hợp đồng chấp nhận.

Khi cần bản mới, code dùng `replace(current, revision=..., marks=...)`.
`dataclasses.replace` tạo một instance mới với các field được thay; nó không
gọi DB hay commit. Đừng nhầm nó với `SqlStore.replace`, là phương thức do ta
định nghĩa để ghi có điều kiện. Trùng từ tiếng Anh không đồng nghĩa cùng API.

**Dự kiến:** mày chỉ đúng nhánh xử lý B/C/D của bảng fixture.
**Nếu kẹt:** thêm log cục bộ `current.revision`, `base_revision`, nhánh đã đi;
không sửa thứ tự if ngẫu nhiên. Với một hàm lạ, điền input/output/tác dụng theo
[F2 — đọc hàm và tool](F2-doc-ham-va-tool.md), rồi mới dùng nó.

## Phiên 5 — Dạy DB giữ điều kiện khi hai người cùng ghi

**Đầu ra:** chỉ ra transaction và chứng minh lỗi giữa chừng không lưu nửa buổi.

Hai request có thể cùng đọc revision 0. Nếu cả hai chỉ chạy `if revision == 0`
rồi ghi, cả hai đều đã qua if. Ta cần điều kiện nằm **ngay trong câu ghi DB**:

```sql
UPDATE attendance_sheets
SET revision = 1
WHERE id = 42 AND revision = 0;
```

Nếu số hàng đổi bằng 1, request đã giành được lượt ghi phiên bản này. Nếu bằng
0, dữ liệu đã thay đổi hoặc buổi không còn tồn tại; không được tiếp tục ghi
các mark như thể thành công. Đây là compare-and-set: đổi chỉ khi bản cũ khớp.

Mở [storage.py](studio/attendance/storage.py), tìm `SqlStore.replace`:

```text
with self.sessions.begin() as db:
    # UPDATE sheet WHERE revision khớp
    # Nếu không khớp: return False, không sửa mark
    # Nếu khớp: UPDATE toàn bộ các mark trong cùng transaction
    # Nếu có exception: context manager rollback cả revision lẫn mark
```

Đoạn trên là sơ đồ đọc, không phải source thay thế đầy đủ. Source thực có ở
file liên kết. `self.sessions` là session factory đã lắp với engine. Context
manager `begin()` commit khi thoát thành công, rollback khi exception; nó
không phải vòng lặp Python. Adapter sở hữu một thao tác ghi atomic trọn buổi,
vì vậy transaction nằm trong thao tác store đó. Nếu một use case sau này cần
ghi điểm danh **và** notification trong cùng DB, phải cho hai thao tác dùng
chung transaction; không gọi hai store tự commit rồi nghĩ chúng atomic chung.

Code đọc revision và các mark bằng **một SELECT JOIN**. Nếu đọc revision bằng
một SELECT, sau đó request khác commit, rồi đọc marks bằng SELECT thứ hai,
ta có thể dựng snapshot trộn cũ/mới ở một số mức isolation. Đọc một kết quả
cùng câu truy vấn tránh lỗi thiết kế đó cho dữ liệu lab này.

Test quan trọng cố ý bypass service: ghi học sinh 2 thành present, rồi học sinh
3 thành status bị CHECK cấm. DB ném lỗi ở dòng 3. Sau đó một Session mới phải
đọc được revision 0 và cả hai vẫn `None`. Mục tiêu là kiểm **hậu quả sau lỗi**,
không chỉ kiểm “có exception”.

**Dự kiến:** test `test_db_exception_rolls_back_guard_and_earlier_marks` qua.
**Nếu kẹt:** tìm `commit` nằm trong vòng lặp không. Nếu có, rollback phía sau
không hoàn tác được transaction đã commit trước. Giữ một ranh giới ghi trọn
buổi. Tests SQLite ở đây không thay kiểm MySQL hai transaction thật;
đến [P2](25-hieu-nang-chiu-tai.md) mới đo/rà race trong môi trường đó.

## Phiên 6 — Nối nghiệp vụ đã hiểu vào hợp đồng HTTP

**Đầu ra:** một contract JSON và hai route trong repo học, sử dụng auth/dependency
đã dựng ở G3/G4. Không viết lại login hay học một framework mới ở phiên này.

| Hành động | Contract |
|---|---|
| GET `/attendance-sheets/42` | Trả id, class_id, revision, marks; mỗi mark có student_id/status |
| PUT `/attendance-sheets/42` | Body có base_revision và toàn marks; response là snapshot server xác nhận |
| Chưa đăng nhập | 401 từ auth dependency |
| Học sinh/teacher bị khóa | 403; không ghi dữ liệu |
| Giáo viên khác/buổi không có | 404 theo policy phạm vi lab |
| Roster/status/revision sai | 422; không ghi dữ liệu |
| Revision cũ và nội dung khác | 409; client giữ bản đang sửa và cho tải bản mới |

Ví dụ body, không có `teacher_id`, `saved_by` hay `class_id` tùy ý:

```json
{
  "base_revision": 0,
  "marks": [
    {"student_id": 2, "status": "present"},
    {"student_id": 3, "status": "absent"}
  ]
}
```

Schema input là ranh giới đọc JSON, không phải ràng buộc duy nhất của nghiệp vụ:

```python
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

class MarkInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    student_id: int = Field(strict=True, gt=0)
    status: Literal['present', 'late', 'absent', 'excused']

class AttendanceInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    base_revision: int = Field(strict=True, ge=0)
    marks: list[MarkInput] = Field(min_length=1, max_length=100)
```

`Literal[...]` chỉ cho những chuỗi đã liệt kê; `extra='forbid'` từ chối field
ngoài schema. Schema chưa biết roster của buổi nên service vẫn phải kiểm
trùng/đúng đủ học sinh. Client TypeScript không thay được schema Python.

Lắp route theo mẫu dependency ở [FastAPI](07-fastapi.md), với thuật toán:

Reference make_lab_engine() chỉ dựng SQLite trong RAM cho demo/test đơn process.
Khi ghép vào HTTP, dùng engine và Session theo request của bản học với DB file
phù hợp, tạo bảng/migration và seed một lần trước khi phục vụ. Đừng tạo engine
hoặc seed fixture trong từng request. Dùng actor từ current_user; fixture số
trong demo chưa xác thực danh tính. Kiểm lại quyền và transaction trên engine
thật trước khi xem kết quả unit test là bằng chứng cho API. Xem G4 phần Session.

```text
payload đã được parse
actor = current_user (backend resolve, active/role hiện hành)
service = AttendanceService(store đã lắp với DB học)
marks = tuple(Mark(row.student_id, row.status) for row in payload.marks)
result = service.save(actor, sheet_id, payload.base_revision, marks)
map InvalidInput/Forbidden/NotFound/Conflict sang status đã chốt
serialize result theo output schema allowlist
```

Đây là việc chuyển dữ liệu/giao thức; không đặt thêm một bản kiểm revision
chỉ ở router. Chốt riêng output schema, chỉ trả field client cần. Không trả
nguyên ORM `__dict__` hoặc nội dung exception DB cho trình duyệt.

**Dự kiến:** gọi PUT bằng API client cho bước B/C/D ra 200/200/409, rồi GET
vẫn đúng nội dung cuối được xác nhận. Thử thêm teacher_id vào body phải 422.
**Nếu kẹt:** dùng Network hoặc API client tách lỗi transport khỏi core. Nếu
unit test qua nhưng HTTP sai, kiểm JSON/schema/error mapping/dependency trước
khi thay thuật toán. Nếu chưa tự nối được route, quay G3/G4; không coi việc
copy một handler chưa hiểu là đã hoàn thành phiên.

## Phiên 7 — UI giữ bản người dùng đang sửa và bản server đã xác nhận

**Đầu ra:** trang điểm danh có loading/error, từng trạng thái chưa ghi, lưu,
conflict và tải lại; refresh cho dữ liệu đã commit.

Tách hai điều dễ nhầm:

```text
loaded: snapshot server đã xác nhận, gồm revision
draft: các lựa chọn cô đang sửa, chưa được server xác nhận
requestState: idle | saving | failed | conflict
```

Không tăng `loaded.revision` trong client khi bấm nút. Server trả bản nào thì
client nhận bản đó. Không dùng `absent` làm giá trị mặc định của select chưa
được chọn. Một em chưa ghi phải hiện “Chưa chọn”.

Trong TS, biểu diễn trạng thái để compiler giúp mày phát hiện field thiếu:

```typescript
type AttendanceStatus = 'present' | 'late' | 'absent' | 'excused';
type MarkView = { student_id: number; status: AttendanceStatus | null };
type SheetView = {
  id: number;
  class_id: number;
  revision: number;
  marks: MarkView[];
};

function changeMark(rows: MarkView[], studentId: number,
                    status: AttendanceStatus): MarkView[] {
  return rows.map(row => row.student_id === studentId ? {...row, status} : row);
}
```

`changeMark` trả array mới và object mới ở hàng đổi. Nếu chưa hiểu `map`/spread,
tự viết bản vòng lặp trước theo [F0](F0-python-sang-js-ts.md), chạy fixture rồi
mới dùng dạng ngắn. Nó không gọi API; UI dùng nó để cập nhật draft.

Luồng lưu:

1. Nếu còn status null, chỉ dòng cần chọn và giữ các lựa chọn khác.
2. Chụp body từ draft, `base_revision` từ loaded; đặt saving.
3. Thành công: thay cả loaded/draft bằng snapshot response đã validate.
4. 409: giữ draft; báo “Buổi đã được sửa ở nơi khác”; cung cấp thao tác tải
   bản mới với cảnh báo lựa chọn chưa lưu sẽ bị thay. Không tự gửi lại với
   revision mới, vì đó là tự ghi đè quyết định người khác.
5. Mất mạng: nói “Chưa xác nhận lưu”; cho GET kiểm trạng thái hoặc retry cùng
   body. Không báo chắc “Chưa lưu”, vì response có thể đã mất sau commit.

Khi đổi buổi hoặc đổi tài khoản, bỏ dữ liệu và request cũ theo cách cleanup đã
học. Response của buổi A về sau response buổi B không được thay màn B. Select
cần label có tên học sinh, nút có trạng thái saving và thông báo đọc được bằng
bàn phím; màu đỏ/xanh một mình không đủ giải thích trạng thái.

**Dự kiến:** hai tab thử đúng bảng A–E; lỗi không làm mất draft âm thầm.
**Nếu kẹt:** ghi `loaded/draft/requestState` ở ba cột trên giấy. Nếu một state
vừa có nghĩa “đã lưu” vừa có nghĩa “đang sửa”, tách lại trước khi thêm effect.
Xem phần state/effect/form ở [React](04-react.md) theo đúng chỗ đang vướng.

## Phiên 8 — Chạy reference, làm hỏng một điều rồi chứng minh đã sửa

**Đầu ra:** kết quả chạy của mày và một lỗi đã tái hiện bằng test.

Nếu đang dùng repo nguồn ở máy soạn và venv của repo đó, đứng ở gốc repo:

```powershell
.\.venv\Scripts\python.exe docs/course/studio/attendance/demo.py
.\.venv\Scripts\python.exe -m unittest discover -s docs/course/studio/attendance -p test_attendance.py -v
```

Nếu đã tạo môi trường riêng ở G4, dùng chính interpreter đó với đường dẫn
source đầy đủ. Hai đường dẫn dưới có hai vai trò: venv của mày và nơi sách
đang đặt; đổi chúng khi giải nén ZIP hoặc chuyển thư mục:

```powershell
$learningPython = 'D:\lms-tu-hoc\.venv\Scripts\python.exe'
$attendanceSource = 'D:\vision-education-lms\docs\course\studio\attendance'
& $learningPython -X utf8 "$attendanceSource\demo.py"
& $learningPython -X utf8 -m unittest discover -s $attendanceSource -p test_attendance.py -v
```

Toán tử & gọi chương trình có đường dẫn nằm trong biến; nháy giữ đường dẫn có
khoảng trắng. G4 đã cài SQLAlchemy vào venv đó. Chỉ có bản giải nén và chưa làm
G4 thì làm bước môi trường của G4 trước; đừng chép đường dẫn .venv của máy soạn
vào máy khác và mong nó tồn tại.

Demo phải in `saved revision: 1`, `retry revision: 1`, báo conflict cho bản cũ
khác nội dung. Test suite kiểm quyền, roster thiếu/trùng/ngoài phạm vi, status,
revision sai kiểu, retry, CAS, PK/FK/CHECK và rollback. Mở
[test_attendance.py](studio/attendance/test_attendance.py), chọn một test và
chỉ ra **assertion nào** sẽ fail nếu luật tương ứng bị bỏ.

Trong **bản copy repo học**, bỏ điều kiện `SheetRow.revision == expected_revision`
ở UPDATE. Test hai snapshot phải phát hiện bản sau ghi đè. Khôi phục điều kiện,
chạy lại đúng test rồi cả suite. Không chỉnh expected result để làm test xanh.

Tự thêm test: một buổi tồn tại với roster rỗng. Policy lab không cho save
1–100 người nên phải nhận lỗi và không đổi. Nếu sản phẩm cần buổi rỗng, đổi
policy và UI có chủ đích, không xóa validation chỉ để hết lỗi.

**Dự kiến:** bằng chứng có lệnh, interpreter, kết quả thật và giải thích giới
hạn. Tests tuần tự SQLite chưa chứng minh race MySQL, HTTP, UI hay chịu tải.
**Nếu kẹt:** `ModuleNotFoundError` → dùng đúng venv theo README reference;
assert fail → ghi expected/actual và dựng fixture nhỏ; test chạy xanh dù đã
bỏ luật → test chưa kiểm được luật đó, cần sửa assertion hoặc tình huống.

## Phiên 9 — Tài liệu: làm có gợi ý, chưa nhảy ngay vào upload

**Đầu ra:** một module tài liệu liên kết có nháp/công bố, sau đó mới thiết kế
upload. Mức trợ giúp giảm: đề và khung có sẵn, mày tự điền schema/API/quyền.

Đề: giáo viên lớp đăng đường dẫn tài liệu; học sinh đúng lớp chỉ xem tài liệu
đã công bố. Tiêu đề 1–200 ký tự sau trim; link dùng `https`, không để server
tự fetch URL. Sửa/ẩn tài liệu theo quyền; link ngoài có thể yêu cầu đăng nhập
ở dịch vụ ngoài và không đảm bảo private chỉ vì LMS kiểm quyền.

Trước khi mở gợi ý, điền sáu ô:

```text
Một hàng Resource đại diện cho:
Các field cần lưu và field lấy từ actor:
Điều kiện list/detail của cô và học sinh:
Thao tác nháp → công bố → ẩn:
API input/output và lỗi:
UI giữ draft khi request thất bại thế nào:
```

<details><summary>Gợi ý 1 — Chỉ xác định trạng thái và phạm vi</summary>

Resource thuộc class; `draft/published/hidden` khác nhau. Membership là điều
kiện đọc, không phải field client dùng để khai rằng mình có quyền. Route
list và detail phải dùng cùng policy, tránh list đã ẩn nhưng biết id vẫn đọc.

</details>

<details><summary>Gợi ý 2 — Khung tham chiếu sau khi đã điền</summary>

`Resource(id,class_id,title,kind='link',url,status,created_by,revision)`.
Create lấy created_by từ actor và kiểm quyền class. Edit gửi revision để không
ghi đè giữa hai tab. Publish/hidden là chuyển trạng thái được kiểm server.
Student output không chứa tài liệu nháp; không chỉ lọc ở React.

Các route có thể là POST/GET `/classes/{id}/resources`, GET/PATCH
`/resources/{id}`, POST `/resources/{id}/publish`, POST `/resources/{id}/hide`.
Đây là một lựa chọn, không phải tên route duy nhất đúng. Viết test đọc ngoài
lớp, đọc nháp, list/detail cùng scope, title trống và revision cũ.

</details>

Sau khi link chạy qua UI/API/DB, mới nhận yêu cầu “cô muốn upload PDF tối đa
5 MiB”. Phần mới không chỉ là thêm input: có hai nơi lưu độc lập — DB metadata
và file storage. `commit` DB không tự rollback file.

Tự vẽ ba trường hợp trước khi dùng FormData:

| Trường hợp | Quyết định tham chiếu |
|---|---|
| Storage ghi lỗi | Không tạo metadata published; UI cho thử lại |
| Storage xong, DB commit lỗi | Xóa file vừa ghi; cleanup lỗi phải ghi nhận để retry |
| DB có metadata nhưng file mất về sau | Download báo lỗi phù hợp; theo dõi và phục hồi, không trả success giả |

Key lưu do server sinh, filename gốc chỉ là metadata. Download kiểm quyền
hiện tại rồi đọc private storage hoặc cấp URL ngắn hạn theo thiết kế. Không
lấy `../../...` từ tên file làm đường dẫn; không coi đuôi `.pdf` là bằng chứng
nội dung an toàn. Chọn giới hạn/kiểm nội dung, quota và nơi lưu theo loại tài
liệu thực tế. Xem đúng phần [upload](14-module-mo-rong.md#xưởng--upload-đi-từ-trình-duyệt-đến-storage)
và [giới hạn upload](27-bao-mat-va-van-hanh.md#4-giới-hạn-tài-nguyên-và-upload)
khi bước vào phiên upload, chưa cần cài queue/broker.

**Dự kiến:** bản link có code và tests; upload có contract lỗi trước khi viết.
**Nếu kẹt:** nếu link còn chưa đi từ form đến DB, quay luồng nhỏ đó. Nếu upload
download được bằng URL public khi user ngoài lớp, sửa ranh giới quyền/storage;
ẩn nút tải trong UI không khắc phục được.

## Phiên 10 — Thông báo: tự thiết kế trước khi mở đáp án

**Đầu ra:** một inbox trong ứng dụng: list của tôi, số chưa đọc, mark read an
toàn khi gửi lại. Không email/push/WebSocket trong bản đầu.

Đề độc lập: khi một bài tập được công bố lần đầu, tạo một thông báo cho mỗi
học sinh hợp lệ của lớp. Retry publish không tạo thông báo trùng. Học sinh chỉ
đọc/đánh dấu của mình. Mở link của thông báo vẫn kiểm quyền bài hiện tại; rời
lớp không biến notification thành quyền xem vĩnh viễn.

Trước khi code: viết event nào tạo notification; recipient chốt khi nào;
định nghĩa “chưa đọc”; cách giữ publish và notification nhất quán khi có lỗi.
Tạo fixture 2 học sinh, publish hai lần, người A đọc hai lần; tính tay số row
và unread của A/B. Khi chưa có câu trả lời, chỉ mở **một** tầng gợi ý.

<details><summary>Gợi ý 1 — Dữ liệu cần phân biệt</summary>

Event xảy ra một lần; một event có nhiều người nhận. `read_at=None` là chưa
đọc. Recipient lấy từ membership phía server. Một action mark read có thể là
no-op nếu đã đọc; không tăng/giảm một counter local không có nguồn chuẩn.

</details>

<details><summary>Gợi ý 2 — Ràng buộc và transaction</summary>

UNIQUE(event_id,recipient_id) bảo vệ trùng. Event id phải được giữ ổn định khi
retry cùng lần publish, không tạo UUID mới mỗi lần nhận HTTP rồi mong UNIQUE
chặn được. Transition bài từ draft sang published và event/notifications cùng
DB nên có thể nằm trong một transaction. Ghi ở hai transaction khác nhau tạo
khả năng có bài nhưng không có thông báo hoặc ngược lại.

</details>

<details><summary>Thiết kế tham chiếu — Chỉ đối chiếu sau bản tự làm</summary>

```text
PublicationEvent: id, assignment_id, publication_revision
  UNIQUE(assignment_id, publication_revision)
Notification: id, event_id, recipient_id, created_at, read_at
  UNIQUE(event_id, recipient_id)
```

Trong transaction publish: kiểm actor/phạm vi/trạng thái, đổi bài, tạo event
cho lần phát hành đó, lấy recipients theo policy rồi tạo notification. Nếu
retry một publish đã thành công, đọc cùng publication/event; không tạo đợt
mới. Nếu sau này cho thu hồi/tái công bố, cần định nghĩa có tạo đợt mới hay
không và tăng publication_revision theo chuyển trạng thái được phép.

GET `/me/notifications` query theo actor.id trước phân trang; GET count cũng
cùng scope. PATCH `/notifications/{id}/read` chỉ update khi recipient bằng
actor.id và read_at còn null; lấy giờ server. Gửi lại trả trạng thái đã đọc,
không đổi read_at lần đầu. Không nhận recipient_id để chọn hộ trong body.

Fixture tham chiếu: một lần publish cho 2 học sinh → 2 notification; retry
publish → vẫn 2; A đọc hai lần → unread A=0, B=1, timestamp A giữ lần đầu.
Request A đánh dấu notification B → không đổi dữ liệu B.

Không bắt mọi cách làm có cùng tên class. Nếu thiết kế dùng event khác nhưng
giữ được invariants, có thể hợp lệ. Reviewer cần xem code/test, không chỉ cây
thư mục. Với lớp rất lớn, tạo fanout trong HTTP có thể dài; lúc có số đo mới
tách batch/job và theo dõi tiến độ, vẫn giữ dedupe/transaction hợp lý.

</details>

Chỉ khi yêu cầu thêm email, mới học outbox/worker: publish và outbox cùng
transaction; worker có thể gửi rồi chết trước đánh dấu nên phải thiết kế retry
và chống trùng phù hợp nhà cung cấp. Xem [thông báo nền](14-module-mo-rong.md#bài-145--thông-báo-và-công-việc-nền).
Không gọi email trong một transaction dài rồi nghĩ rollback thu hồi được email.

**Dự kiến:** reviewer chỉ được một test sẽ fail nếu bỏ scope và một test sẽ
fail nếu publish tạo trùng. UI refetch số chuẩn sau đọc/thử lại.
**Nếu kẹt:** chưa nghĩ ra unique key → quay câu “hai bản nào bị coi là trùng?”;
badge âm → tính từ dữ liệu server hoặc cập nhật idempotent, không trừ mỗi click.

## Phiên 11 — Mở rộng toàn LMS theo phụ thuộc, không mở mọi màn cùng lúc

**Đầu ra:** kế hoạch ba phiên bản của chính mày, mỗi lát cắt có điểm bắt đầu
nhỏ, rule mới và nơi học đúng lúc. Đây là lộ trình thực hành, không phải tuyên
bố mọi module đã có implementation.

| Thứ tự hợp lý | Lát cắt đầu và lý do học lúc này | Rule mới phải tự giải thích | Tài liệu đọc khi vướng |
|---|---|---|---|
| 1. Tài khoản/phiên | Login/logout và trạng thái tài khoản; mọi quyền sau dựa vào actor | Token hợp lệ khác quyền hiện tại | [09](09-auth-phan-quyen.md), [P4](27-bao-mat-va-van-hanh.md) |
| 2. Lớp/thành viên | Tạo lớp, thêm/xem thành viên; có phạm vi cho dữ liệu học | Một user nhiều lớp; rời lớp giữ lịch sử | [G4 nền backend qua xưởng](21-xay-tu-so-0.md) |
| 3. Giao/nộp/chấm | Một bài văn bản đi hết luồng, rồi nháp/công bố/thu hồi | Retry, deadline, điểm 0 và chưa chấm | [10](10-lat-cat-hoan-chinh.md), [P0](23-san-pham-hoan-chinh.md) |
| 4. Lịch/điểm danh | Một buổi có giờ bắt đầu/kết thúc rồi chụp roster | Timezone, hủy/dời; lịch sử roster và revision | [14 phần lịch](14-module-mo-rong.md), các phiên 1–8 ở đây |
| 5. Tài liệu | Link trước, file sau; dùng lại scope lớp và form | Private download; file/DB có thể lỗi riêng | Phiên 9, [14](14-module-mo-rong.md) |
| 6. Thông báo/hỏi đáp | Inbox HTTP và một thread dưới bài; giá trị trước realtime | Recipient/dedupe và quyền resource hiện tại | Phiên 10, [14](14-module-mo-rong.md) |
| 7. Luyện thi | Một câu một đáp án → một attempt → submit/chấm; rồi thêm dạng | Snapshot đề, clock server, autosave có thứ tự | [11](11-luyen-thi-bao-cao.md) |
| 8. Báo cáo/dashboard | Một số đếm/tỉ lệ tính tay từ fixture trước | Mẫu số, first/best/latest attempt, không có dữ liệu khác điểm 0 | [11 phần báo cáo](11-luyen-thi-bao-cao.md) |
| 9. Quản trị/phục hồi tài khoản | Khóa user, reset mật khẩu và lịch sử thao tác | Token reset một lần/hết hạn, policy phiên cũ, quyền đổi role | [14](14-module-mo-rong.md), [P4](27-bao-mat-va-van-hanh.md) |
| 10. Realtime | Chỉ thêm khi inbox/lịch sử HTTP đã đúng và có nhu cầu cập nhật ngay | Auth room, revoke, reconnect, cursor, gửi lặp, nhiều process | [14 phần WebSocket](14-module-mo-rong.md) |

Trong mỗi hàng, dùng lại cách làm đã thực hành: fixture tay → service/test →
storage/constraint → HTTP → UI → hai tài khoản → lỗi → yêu cầu đổi. Không cần
một kiến trúc mới cho từng module. Khi dữ liệu mới có vòng đời riêng, tạo
module/domain rõ; khi chỉ thêm trường vào cùng hành động, đừng tự động tạo
service/repository/interface cho riêng một field.

Ba phiên bản tham chiếu:

- **MVP dùng thử:** tài khoản đã xác thực thật, lớp/thành viên, bài văn bản,
  nộp/chấm/công bố, trạng thái UI và phân quyền thực. Chỉ dùng giả lập/fixture
  trong lab; chưa đưa CLI cấp token giả cho người dùng thật.
- **LMS theo phạm vi đã chốt:** thêm lịch/điểm danh, tài liệu, thông báo, một
  luồng thi, báo cáo, quản trị/phục hồi. Chốt rõ dạng thi/loại file/quy tắc,
  không gọi “đủ mọi chức năng” khi chỉ làm một dạng.
- **Bản vận hành cho quy mô mục tiêu:** kiểm MySQL, đo workload thật, làm
  deployment/backup/restore, quan sát lỗi, quyền/phiên, UX và hướng dẫn bàn giao.

**Dự kiến:** backlog có phụ thuộc và một lát cắt hiện tại; mỗi nút trong bản
demo có hậu quả thực hoặc được ghi chưa làm.
**Nếu kẹt:** một mục quá to như “xong module thi” → thu xuống “bắt đầu một
attempt một câu và refresh vẫn thấy cùng câu”; viết tình huống nghiệm thu
được trong một vòng phát triển trước khi thêm toàn ngân hàng đề.

## Phiên 12 — Đưa mục tiêu clean, chịu tải và được đánh giá thành bằng chứng

**Đầu ra:** kế hoạch kiểm tra cho phiên bản của mày, dùng số đo và artefact thực.

“Clean” bắt đầu bằng chỗ đặt rule có lý do. Với điểm danh, thêm `excused` không
buộc sửa HTTP status hay SQL connection; đổi storage không đổi nghĩa conflict.
Nhưng tách nhiều file không tự làm code sạch: xem một lần save có đi qua
những trách nhiệm rõ, có tên diễn đạt đúng và có test bảo vệ luật hay không.
Đọc [P1](24-clean-code-refactor.md) khi refactor chính feature vừa chạy được,
giữ hành vi qua tests rồi mới thay cấu trúc.

“Nhiều user” phải thành workload: bao nhiêu người, đọc gì/ghi gì, cùng một lớp
hay nhiều lớp, trong bao lâu, dữ liệu bao lớn. Hai tab điểm danh tranh cùng
buổi khác nghìn học sinh đọc các bài riêng. Sau khi đúng luật, chuyển sang
[P2](25-hieu-nang-chiu-tai.md) để đo latency/lỗi và correctness sau tải; không
suy ra capacity từ async, số worker hay một unit test.

“Dùng được” còn cần một môi trường khác dựng lại, refresh/deep link, quyền
hai tài khoản, thao tác bàn phím, thông báo lỗi không mất input. Sang
[P3](26-trien-khai-ci-cd.md) từng bước deployment và
[P4](27-bao-mat-va-van-hanh.md) phiên/reset/observability/restore, chỉ học công
cụ mới khi có thao tác cần làm. Backup chỉ là file cho tới khi restore thử và
đối chiếu được dữ liệu. Hồ sơ/demo/rubric ở [P5](28-do-an-va-nghiem-thu.md)
giúp người khác đánh giá, không bảo đảm điểm số của một hội đồng chưa biết.

**Dự kiến:** mày chỉ được “đã chạy gì, trên bản nào, kết quả gì, chưa biết gì”.
**Nếu kẹt:** một báo cáo toàn từ “tốt/nhanh/hoàn chỉnh” → đổi mỗi tính từ thành
một thao tác, một bằng chứng và một giới hạn. Sau đó qua
[G6](G6-tu-lam-va-duoc-phan-hoi.md) để kiểm khả năng tự làm và sửa theo review.
