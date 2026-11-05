# G4 — Từ hàm Python đến một tính năng đi qua cả hệ thống

G3 đã giúp mày tự chia chương trình nhỏ thành file có lý do. G4 nối chính
những ý đó sang HTTP, database và React. Mình làm kỹ **tạo/đổi tên lớp** trước,
rồi giảm gợi ý khi làm **lưu trữ lớp**. Không bắt mày thuộc cả framework mới
được bắt đầu. Từ mới xuất hiện đến đâu thì mở nghĩa đến đó.

Học 9 buổi nhỏ. Mỗi buổi có một thứ chạy được hoặc một quyết định viết ra.
Đừng mở patch đáp án ngay: chụp lại dự đoán và lỗi của mình trước khi so.
Source tham chiếu là xưởng học độc lập; đây chưa phải toàn bộ LMS sản phẩm.

## Buổi G4.1 — Dựng bản học và lần theo một request thật

**Đích:** biết mình đang chạy file nào, bằng Python nào, dữ liệu ở đâu.
Trước hết hoàn thành G3: tự viết được create/list/archive thuần Python và giải
thích được từ chối không đổi kho. Chỉ biết đọc source chưa qua checkpoint này.

Tạo một thư mục học riêng, thống nhất dùng `D:\lms-tu-hoc` trong chương này.
Nó độc lập với các sandbox G1/G2; không giả định G0 đã dựng project cho mày.
Nếu đã dùng đúng thư mục này, New-Item chỉ giữ nó, không xóa nội dung. Kiểm
Get-Location phải ra đúng thư mục học trước lệnh Git hay tạo môi trường.
`D:\vision-education-lms` là nơi bản giáo án này đang đặt; đổi phần đường dẫn
nguồn đó nếu mày chuyển sách. Script chỉ sao chép source, bỏ database,
node_modules và dist, từ chối ghi đè đích đã có.

```powershell
$learningRoot = 'D:\lms-tu-hoc'
New-Item -ItemType Directory -Force -Path $learningRoot
Set-Location $learningRoot
Get-Location
git --version
git init
git status --short
python -X utf8 D:\vision-education-lms\docs\course\studio\backend\prepare_workshop.py .\lab-workshop
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r .\lab-workshop\requirements.txt -r .\lab-workshop\deploy\requirements.txt
```

Nếu đã có `.venv` của repo học, dùng nó, không cần tạo lại. Cài dependency
cần mạng lần đầu. `python -m venv` tạo môi trường riêng; `-m pip` dùng pip của
đúng interpreter đứng trước nó. Không cần activate khi gọi đường dẫn đầy đủ.
Dependency trực tiếp có version trong requirements; chưa khóa mọi gói bắc cầu.

`git --version` phải in phiên bản; chưa có thì cài Git theo chương16 trước
khi tiếp tục. `git init` tạo metadata theo dõi thay đổi trong thư mục hiện tại;
chạy lại repo học đã có vẫn giữ file. `git status --short` xem file đang đổi,
không tự commit hay upload. Tạo `.gitignore` ngay gốc repo học bằng editor:

```text
.venv/
__pycache__/
node_modules/
dist/
*.db
*.db-*
.env
```

Git checkpoint chỉ đưa source bài vào commit sau khi tự xem diff, không đưa
DB/token/secret. Đừng git init tại D:\vision-education-lms để học bài này;
đó là repo chứa sản phẩm và sách, khác thư mục học mày vừa tạo.

Chuyển vào xưởng, tạo secret lab trong RAM của terminal, tạo DB và token:

```powershell
Set-Location .\lab-workshop
$env:LAB_SECRET = (..\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(48))")
$env:LAB_DATABASE_URL = 'sqlite:///./g4-learning.db'
..\.venv\Scripts\python.exe -m lms_lab init
$teacherToken = (..\.venv\Scripts\python.exe -m lms_lab token --user 1)
$studentToken = (..\.venv\Scripts\python.exe -m lms_lab token --user 2)
..\.venv\Scripts\python.exe -m uvicorn lms_lab.main:app --host 127.0.0.1 --port 8001
```

Init cần in “Đã tạo fixture SQLite học…”. Nếu báo đã có fixture, dùng DB học
mới với tên mới; không xóa DB để che lỗi. User 1 là cô, user 2 thuộc lớp 1, user 3
ngoài lớp, user 4 bị khóa. Token giả hết hạn 30 phút. Chỉ dùng cho máy học.
Giữ terminal server chạy. Secret mới làm token cũ mất hiệu lực.

Mở `http://127.0.0.1:8001/health` ở browser: cần thấy `{"status":"ok"}`.
Browser vừa gửi một **request** (lời yêu cầu) và server trả **response** (kết
quả). Một request không chỉ có dữ liệu: method nói hành động, path chỉ nơi
xử lý, header mang metadata như xác thực, body mang dữ liệu nếu có. JSON là
cách viết dữ liệu giữa hai chương trình; dấu ngoặc/khóa chuỗi ở đây không
phải một hàm Python đang chạy trên server.

| Phần | Lần tạo lớp này | Đọc nghĩa |
|---|---|---|
| Method + path | POST `/classes` | Yêu cầu tạo lớp mới |
| Request header | `Authorization: Bearer <token-lab>` | Credential để server xác minh actor |
| Request header | `Content-Type: application/json` | Body đang dùng định dạng JSON |
| Request body | `{"title":"  Python  "}` | Đầu vào client gửi; chưa phải record DB |
| Response status | 201 | Server đã tạo thành công |
| Response body | `{"id":2,"title":"Python","teacher_id":1}` | Dữ liệu trả; id có thể khác 2 |
| Response status khi sai tên | 422 | Body không qua validation, không được tạo |
| Response status khi sai quyền | 403 | Actor đã xác minh nhưng không được tạo |

GET đọc dữ liệu, POST thường tạo/thực hiện hành động; method là một phần của
hợp đồng, không phải tên tùy ý. Status 200/201 là thành công, 401 cần xác thực,
403 thiếu quyền,404 không thấy trong phạm vi,422 dữ liệu sai; lỗi mạng có thể
chưa nhận được response/status nào. Server kiểm token đã ký/hết hạn, lấy id
để đọc User và trạng thái hoạt động trong DB; không tin role client tự gửi.
Xem [chương 02, Bài 02.5 và xưởng “Đọc đủ một hợp đồng HTTP”](02-typescript-http.md)
khi cần soi thêm URL/query/header/body. Mày vừa có một request cụ thể để đối
chiếu những khái niệm đó, không cần học thuộc cả chương trước khi thử.

Mở `/docs`: Swagger là màn hình thử HTTP do FastAPI tạo. Bấm **Authorize**, dùng
giá trị token cô vừa tạo; nếu cần xem nó, dừng server bằng Ctrl+C, in
`$teacherToken` tại máy học, rồi chạy lại đúng lệnh uvicorn trong cùng terminal.
Không thay secret. Gửi POST `/classes` với body `{"title":"  Python  "}`.
Kỳ vọng HTTP 201, title `Python`, teacher_id 1 và id mới. Gửi title toàn khoảng
trắng: HTTP 422. Dùng token học sinh tạo lớp: HTTP 403.

Lệnh uvicorn có nghĩa: import module `lms_lab.main`, lấy object `app`, nghe
HTTP tại host/cổng đã chỉ. Dấu `:` ở đây thuộc cú pháp CLI của uvicorn.
`main.py` tạo engine rồi gọi `create_app`; nó không tự chạy một vòng `input()`.

Theo request đầu qua source, chưa học tất cả dòng:

```text
JSON {title} → app.py create_class → schemas.py ClassInput
actor từ current_user → ClassService.create
ClassRepository.add → Session.flush → SqlTransaction.commit
ClassOutput → JSON response → người gọi
```

Mở một file mỗi lần theo mũi tên. Ghi tên đầu vào/đầu ra của từng chỗ. Source
được đặt trong một package `lms_lab`: `__init__.py` đánh dấu package; lệnh `-m`
chạy nó theo ngữ cảnh package. `from .models import User` nghĩa là lấy User
từ models cùng package. Chạy `python lms_lab/app.py` trực tiếp sẽ làm mất
ngữ cảnh relative import; chạy entry đúng thay vì xóa các dấu chấm import.

**Tự đổi:** title thành `CSS`, kiểm response và GET danh sách. **Tự kể:**
reload browser không tạo lại lớp vì GET khác POST; restart process vẫn giữ
lớp vì SQLite file, khác kho RAM G3. Chưa kiểm được cả hai thì sửa trước G4.2.

## Buổi G4.2 — Tại sao hàm thành class, self và lắp ghép nghĩa là gì?

**Đích:** đọc được `ClassService(repository, transaction)` mà không coi nó là
bùa framework. G3 truyền `store` vào mỗi hàm. Một cách khác là giữ dependency
trong object để nhiều method cùng dùng. Gõ thử riêng file `object_demo.py`:

```python
class LabelMaker:
    def __init__(self, prefix):
        self.prefix = prefix

    def label(self, title):
        return self.prefix + title.strip()


maker = LabelMaker('Lớp: ')
print(maker.label('  Python  '))
print(LabelMaker.label(maker, '  CSS  '))
```

Kết quả là `Lớp: Python` rồi `Lớp: CSS`. `class` định nghĩa kiểu object;
`LabelMaker(...)` tạo object và gọi `__init__` để gắn giá trị ban đầu. `self`
là chính object đang nhận lời gọi; `self.prefix` là thuộc tính của object.
Hai cách gọi method trên tương đương về việc truyền object đầu tiên. Không
phải mọi method đều tự chạy khi tạo object: chỉ `__init__` có vai trò đó.

Bây giờ đọc đúng constructor trong `lms_lab/service.py`:

```python
class ClassService:
    def __init__(self, repository, transaction):
        self.repository = repository
        self.transaction = transaction
```

Đây là trích đoạn giải nghĩa constructor, chưa thay toàn bộ class trong xưởng.
`repository` là object biết truy vấn; `transaction` biết commit/rollback.
Constructor chỉ giữ chúng, không tự truy vấn hay commit. Tham chiếu có thêm
type hint `Transaction`; type hint mô tả hợp đồng, không tự tạo transaction.

Đọc `app.py` có hàm lắp thực tế:

```python
def service(db=Depends(get_db)):
    return ClassService(ClassRepository(db), SqlTransaction(db))
```

Đoạn này được đặt **bên trong create_app**, nơi get_db đã được định nghĩa.
Giải từ trong ra ngoài: tạo repository dùng db; tạo transaction dùng **cùng
db**; tạo service giữ hai object đó. Đây là composition, tức ghép những object
có trách nhiệm riêng. Không phải kế thừa. Nếu hai object dùng Session khác nhau,
repository ghi bên A nhưng transaction commit bên B: ghép sai dù tên file đẹp.

`Depends(get_db)` nhận **hàm**, không gọi `get_db()` ngay tại lúc định nghĩa.
FastAPI giải dependency khi xử lý request, gọi get_db, dùng giá trị nó yield,
rồi dọn Session sau request. Các dependency cùng request mặc định được cache,
nên current_user và service dùng get_db chung. Không đặt Session global để
mọi user dùng cùng một object. [Cơ chế dependency của FastAPI](https://fastapi.tiangolo.com/tutorial/dependencies/).

**Tự đổi:** tạo hai LabelMaker với prefix khác nhau và chứng minh chúng giữ
hai thuộc tính riêng. **Lỗi để sửa:** bỏ `self` ở định nghĩa label, dự đoán
TypeError rồi chạy. **Tự kể:** dependency injection ở đây là bên ngoài đưa
đúng object vào, thay vì service tự mở database/đọc secret ở mọi lời gọi.

## Buổi G4.3 — Tạo lớp: phân biệt JSON, DTO, ORM và transaction

**Đích:** tự biết rule nào nằm ở ranh giới dữ liệu, rule nào thuộc hành động.
Theo dõi cùng một title qua bốn hình dạng:

| Chỗ | Giá trị | Việc nó làm |
|---|---|---|
| HTTP | JSON `{"title":"  Python  "}` | Dữ liệu client gửi, chưa đáng tin |
| ClassInput | object Pydantic, title `Python` | Chuẩn hóa/kiểm dạng, cấm trường thừa |
| Classroom | object ORM với title/teacher_id | Theo dõi bản ghi sẽ ghi DB |
| ClassOutput | id/title/teacher_id | Giới hạn dữ liệu trả ra ngoài |

DTO là object vận chuyển dữ liệu qua ranh giới, ở đây là ClassInput/Output.
ORM ánh xạ object Python với bảng/cột DB, ở đây là Classroom. DTO không tự
lưu; ORM không tự xác thực user. TypeScript type cũng không kiểm JSON lúc
chạy. Tên na ná không có nghĩa dùng thay nhau được.

Mở `schemas.py`: `ClassInput(BaseModel)` dùng Pydantic, `Field` giới hạn độ dài,
validator strip **trước** kiểm độ dài, `extra='forbid'` từ chối teacher_id
client tự nhét vào. `@field_validator` đăng ký hàm với thư viện; decorator
không phải một bước nghiệp vụ client gọi riêng. `cls` chỉ class hiện tại ở
classmethod, không phải object payload như `self` ở instance method.

Mở `service.py` và chép riêng method create vào sổ, chia thành bốn khối:

1. Chỉ teacher được tạo; actor đã xác minh từ token/DB, không lấy từ body.
2. Chuẩn hóa/kiểm title vì service có thể được gọi ngoài HTTP.
3. Tạo Classroom và giao repository thêm vào Session.
4. Commit thành công thì trả; gặp lỗi thì rollback rồi ném lại lỗi.

Trước ORM, hiểu bảng DB bằng dữ liệu nhỏ. Bảng là nhóm bản ghi có cùng cột;
một row ở classes có thể là `(id=2, title='Python', teacher_id=1)`.

| Khái niệm | Ở ví dụ này | Giới hạn của nó |
|---|---|---|
| Cột | title/teacher_id | Tên trường và kiểu dữ liệu, chưa phải quyền |
| Row | Lớp id 2 | Một bản ghi cụ thể |
| Primary key, PK | classes.id | Định danh duy nhất để tìm đúng lớp |
| Foreign key, FK | classes.teacher_id → users.id | Chủ trỏ tới user có thật; chưa chứng minh caller là chủ |
| Transaction | Nhóm thay đổi commit hoặc rollback | Giữ các bước cùng chốt/hủy, không tự quyết định policy |

G3 dùng key dict để tìm record; DB dùng PK và truy vấn, giữ dữ liệu sau process
restart. Không có nghĩa dict tương đương đầy đủ database: ràng buộc, truy vấn
và concurrency là những trách nhiệm mới. Nếu còn lẫn bảng với object, đọc
[chương 06, Bài 06.1–06.3 và 06.5](06-sql.md), thử SELECT trên dữ liệu nhỏ rồi
quay lại. ORM tạo SQL giúp mình, không miễn việc hiểu row/PK/FK/transaction.

Đọc lớp model theo từng dòng:

```python
class Classroom(Base):
    __tablename__ = 'classes'
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    teacher_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
```

Đây là trích đoạn trong models.py, nơi Base/Column/các kiểu đã được import.
`Base` do SQLAlchemy tạo; khai báo cột là metadata mô tả schema, chưa phải một
INSERT. Khi viết `Classroom(title=title, teacher_id=actor.id)`, ORM cung cấp
constructor nhận các thuộc tính đã ánh xạ. ForeignKey giữ liên kết id ở DB,
không tự chứng minh actor là chủ lớp; nghiệp vụ vẫn phải kiểm quyền.

`Session` là vùng làm việc theo dõi object và transaction. `add` đánh dấu
object mới; `flush` gửi thay đổi vào transaction hiện tại để có id/kiểm ràng
buộc; **flush chưa commit**. `commit` chốt transaction; `rollback` hủy thay đổi
chưa chốt. Một Session mới đọc lại là cách quan sát đã lưu, thay vì chỉ nhìn
object vừa sửa trong RAM. [Giải thích Session của SQLAlchemy](https://docs.sqlalchemy.org/en/20/orm/session_basics.html).

**Tự thử:** gửi teacher_id 2 kèm title, phải422. Tắt server, chạy lại cùng DB
và cùng secret, GET lớp đã tạo, vẫn còn. **Tự kể:** nếu repo tự commit trước
khi service hoàn tất hai bước thì không còn rollback cả hai cùng nhau được.
Vì vậy repo ở đây không commit. Đây là lý do tách trách nhiệm, không phải
một quy luật “càng nhiều lớp càng clean”.

## Buổi G4.4 — Đổi tên lớp: tự suy từ yêu cầu đến file cần sửa

**Đích:** làm được một lát cắt nữa khi đã có mẫu tạo lớp. Dùng chức năng đổi
tên có sẵn làm bài che đáp án: tạm đóng phần rename trong source, tự viết kế
hoạch trước rồi mở so. Không xóa bản mẫu trong xưởng gốc.

Yêu cầu: chủ lớp sửa tên; học sinh trong lớp xem được nhưng không sửa; user
ngoài phạm vi nhận404. Tên rỗng sau strip bị từ chối, từ chối thì title không
đổi. Trước code, viết năm dòng hợp đồng:

```text
PATCH /classes/{class_id}
body: {title: string}; không nhận teacher_id
200: lớp với title mới
401 chưa xác thực; 403 học sinh thuộc lớp; 404 ngoài phạm vi/không có lớp
422 sai body hoặc id không dương; lỗi không đổi title đã lưu
```

Tại sao PATCH? Mình đổi một phần của lớp. Không dùng GET cho thao tác ghi vì
người gọi/cache có thể lặp GET. Trong lab này PATCH nhận title bắt buộc, chưa
là bộ patch mọi trường tùy ý. Quyết định hợp đồng trước sẽ tránh FE và BE
đoán hai cách khác nhau.

Tự đề xuất file sửa, rồi so bảng:

| Việc | Nơi hợp lý trong project này | Lý do |
|---|---|---|
| URL, đọc payload, đổi lỗi thành HTTP | app.py | Biết HTTP |
| Ai sửa được và lúc nào commit | ClassService.rename | Biết hành động đổi tên |
| Tìm lớp/phạm vi | repo + service.read | Tái dùng đọc dữ liệu/kiểm phạm vi |
| Dạng title đầu vào/đầu ra | schemas.py | Dùng lại ClassInput/Output |
| Cột DB | Không thêm | title đã tồn tại, chưa đổi schema |
| Test kết quả + đọc Session mới | test_workshop.py | Quan sát hành vi/lưu thật |

Trong source, read kiểm lớp có trong phạm vi trước; rename kiểm thêm quyền
teacher/chủ lớp. Tách **được đọc** và **được ghi** vì học sinh có thể đạt điều
kiện đầu mà không đạt điều kiện sau. Nếu chỉ gọi read rồi sửa luôn, học sinh
cũng đổi được tên. Nếu kiểm role trước mọi read, có thể đổi chính sách lỗi
và làm lộ khác biệt với hợp đồng; phải xem yêu cầu, không đoán.

Gõ route tương tự create, dùng `@app.patch`, payload ClassInput và class_id.
Ở route gọi `translate(lambda: classes.rename(actor, class_id, payload.title))`.
`lambda` tạo hàm chưa gọi để translate chạy bên trong try/except; nếu viết
`translate(classes.rename(...))`, lỗi phát ra trước khi translate được gọi.

**Tự chạy:** cô sửa, học sinh thuộc lớp sửa, học sinh ngoài lớp sửa, title trắng,
id999. Mỗi tình huống đọc lại bằng GET. **Tự đổi yêu cầu:** giới hạn tên 100:
cần đồng bộ validator HTTP, service, FE và test; có thể giữ cột 200 để tránh
migration vô ích. Tách file giúp biết phạm vi sửa, không khiến rule tự đồng bộ.

### Bản tách theo tính năng đã giải hoàn chỉnh

Để thấy cả cách lắp FastAPI khi đổi cấu trúc, có
[class-feature-split.patch](studio/backend/class-feature-split.patch) chứa
**toàn bộ thay đổi**, không phải một cây thư mục để mày tự đoán imports.
Đây là bản đối chiếu riêng **trên xưởng gốc trước archive**. Không áp nối với
archive patch vì hai bài cùng thay app/service; chọn bản copy mới để học từng
quyết định độc lập. Học cách đọc diff ở G4.8 rồi quay lại nếu còn lạ.

Trước và sau:

```text
Trước lms_lab/                 Sau lms_lab/
  app.py  (auth + classHTTP)     app.py (auth + gọi install_classes)
  schemas.py                    classes/__init__.py
  repository.py                 classes/schemas.py
  service.py                    classes/repository.py
  models.py                     classes/service.py
  unit_of_work.py                classes/router.py
  workflow.py                   models.py, unit_of_work.py, workflow.py
                                schemas.py/repository.py/service.py (shim)
```

Làm từng việc: chuyển DTO/repo/service vào classes; sửa imports lên cha;
chuyển route và hàm lắp service vào classes/router; app chỉ gọi installer.
Các file cũ còn là **shim**: module chuyển tiếp import để caller/test cũ không
vỡ giữa lần tách. Trong service.py cũ chỉ còn:

```python
"""Compatibility import while callers move into the classes feature."""
from .classes.service import ClassService, Forbidden, NotFound
```

Trong classes/service.py hai imports đầu trở thành:

```python
from ..models import Classroom
from ..unit_of_work import Transaction
```

Một dấu chấm là package hiện tại; hai dấu chấm lên lms_lab. Không chuyển
models vào classes lúc này vì workflow cũng dùng cùng Base/bảng liên kết;
tách tiếp cần cân nhắc ownership/schema, không đổi chỗ chỉ để cây đối xứng.
File classes/router.py import chính xác các dependency dưới và giữ toàn bộ
list/create/read/rename routes trong installer, không còn nhét chúng ở app:

```python
from fastapi import Depends, HTTPException, Path, Query
from .repository import ClassRepository
from .schemas import ClassInput, ClassOutput
from .service import ClassService, Forbidden, NotFound
from ..unit_of_work import SqlTransaction


def install_classes(app, get_db, current_user):
    def service(db=Depends(get_db)):
        return ClassService(ClassRepository(db), SqlTransaction(db))

    @app.get('/classes', response_model=list[ClassOutput])
    def list_classes(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
                     actor=Depends(current_user), classes=Depends(service)):
        return classes.list_visible(actor, page, page_size)
```

Block trên giải thích một route của file; patch có đầy đủ các route còn lại
và translate. app.py xóa imports/helper/routes đã chuyển, gọi hai dòng sau
bên trong create_app, ngay trước install_workflow:

```python
from .classes.router import install_classes
install_classes(app, get_db, current_user)
```

Cùng get_db/current_user truyền vào cả hai feature. Không tạo app thứ hai,
không tạo Session khác. Test cũ import qua shim vẫn dùng **cùng class lỗi**;
copy nguyên định nghĩa Forbidden ở hai nơi sẽ làm except bắt sai identity.
Sau khi tìm và chuyển mọi caller sang imports mới, mới bỏ shim trong lần
refactor riêng có test. Đây là cách chia nhỏ thay đổi mà vẫn chạy được.

Để kiểm bản giải, chạy chính xác từ gốc repo học:

```powershell
Set-Location D:\lms-tu-hoc
python -X utf8 D:\vision-education-lms\docs\course\studio\backend\prepare_workshop.py .\lab-split
git apply --check --directory=lab-split D:/vision-education-lms/docs/course/studio/backend/class-feature-split.patch
git apply --directory=lab-split D:/vision-education-lms/docs/course/studio/backend/class-feature-split.patch
.\.venv\Scripts\python.exe -X utf8 -m unittest discover -s .\lab-split -p "test_*.py" -v
```

Expected 28 test: 26 pass, 2 skip MySQL.
Hợp đồng HTTP/database không đổi nên không thêm migration hay đổi FE.

Vì sao chưa tách mọi file? Với tính năng nhỏ, vài lớp trong một module có thể
dễ đọc hơn 9 module rỗng. Khi lớp học có thêm nhiều use case và người sửa độc
lập với workflow, gom feature giúp nhìn cùng một thay đổi gần nhau. G3 đã
giải từng lần di chuyển hàm; patch này giải tiếp import/composition FastAPI.
Tách toàn bộ workflow.py vẫn là bài refactor sau đó; archive patch **không**
tự làm thay bài đó.

## Buổi G4.5 — Nối React: dữ liệu đi và về, mỗi trạng thái có màn hình

**Đích:** nối một API đã hiểu vào giao diện đã học ở G1–G2. Nếu chưa tự làm được
form, state và component ở G2, quay lại trước khi mở toàn bộ component xưởng.

Ở terminal thứ hai, đứng trong `lab-workshop/frontend` của repo học:

```powershell
Get-Location
npm ci
npm run dev -- --host 127.0.0.1
```

Mở URL Vite in ra, mặc định `http://127.0.0.1:5173`. Giữ cổng 5173 vì CORS lab
cho phép hai origin localhost/127.0.0.1 ở cổng này. Nếu Vite tự nhảy 5174, giải
quyết process cũ đang giữ 5173 hoặc đổi cấu hình CORS đã hiểu; không tắt kiểm
tra trong browser. Dán token fixture vào ô của app. Refresh mất token RAM,
nhưng không mất DB. UI này chưa phải sản phẩm đăng nhập hoàn chỉnh.

Mở `frontend/class-api.ts`, lần theo createClass:

```typescript
export async function createClass(token: string, title: string): Promise<Classroom> {
  const response = await axios.post<unknown>('/classes', { title }, { baseURL, headers: authorization(token) });
  return classroomSchema.parse(response.data);
}
```

Đoạn này nằm trong module đã import axios/z và định nghĩa baseURL/schema.
`{title}` là cách viết gọn `{title: title}`; object thứ ba là cấu hình request.
`<unknown>` nói chưa tin kiểu dữ liệu trả về; không tự kiểm dữ liệu. Axios
trả object response có status/headers/data; JSON body nằm ở `.data`. Zod parse
kiểm body lúc chạy, trả object hợp lệ hoặc ném lỗi. `async` trả Promise;
`await` đợi kết quả trong hàm, không đóng băng toàn browser. Tra hợp đồng API
theo F2 khi gặp method lạ, không đoán từ tên.

Vẽ bằng lời đường submit:

```text
input → form values → handleSubmit → submit → createClass → HTTP
       ← lỗi title         ← catch/setError          ← lỗi HTTP hoặc parse
commit thành công → reset form → tăng reload → effect GET lại → render items
```

Component tham chiếu dùng React Hook Form + Zod sau khi G2 đã làm form thủ
công. `register('title')` nối input với form, `handleSubmit(submit)` validate
rồi gọi submit, `isSubmitting` phục vụ nút chờ. Đây là API thư viện, không
phải cú pháp React bắt buộc. Viết form bằng useState vẫn được nếu bảo toàn
validation/trạng thái và kiểm thử tương đương.

Tại sao class-api là file riêng? Nó biết URL, header và parser; component chỉ
cần gọi `createClass` và diễn tả giao diện. Không trả nguyên Axios response
vào UI để mọi component phải biết `.data` và header. Tách component theo vùng
có trách nhiệm/dữ liệu rõ, chưa cần một component cho mỗi dòng HTML.
[Cách suy từ UI đến component/state](https://react.dev/learn/thinking-in-react).

**Tự kiểm:** đang tải, lỗi API tắt server, dữ liệu rỗng, có dữ liệu, sai tên,
đang gửi, token học sinh bị403. Dùng DevTools Network xem method/URL/body/status;
Console không thay Network. **Bài giảm gợi ý:** thêm đổi tên lớp theo API G4.4.
Trước code, ghi state cần thêm: lớp đang sửa, title draft, đang gửi, lỗi. Đừng
copy toàn ClassPractice thành màn hình thứ hai. Source chưa có form rename;
đó là phần mày tự nối, không coi chỉ gọi Swagger đã hoàn tất giao diện.

## Buổi G4.6 — “Lưu trữ lớp”: khóa nghĩa trước khi thêm nút

**Đích:** biến một câu mơ hồ thành đặc tả có thể kiểm. Đóng patch đáp án. Câu
“cô muốn lưu trữ lớp cũ” chưa trả lời dữ liệu cũ còn đọc được không, bài đang
nộp xử lý sao, bấm hai lần có lỗi không. Không bắt đầu bằng vẽ cây thư mục.

Tự ghi những câu cần chốt, rồi so với quyết định của bài này:

| Câu hỏi | Policy đã chốt cho bản học |
|---|---|
| Ai được lưu trữ? | Chỉ giáo viên chủ lớp; học sinh403, cô khác404 |
| Có xóa lớp/bài/điểm không? | Không xóa, vẫn đọc trong phạm vi cũ |
| Trạng thái? | active → archived; chưa có mở lại |
| Gọi lưu trữ hai lần? | Cùng trạng thái/response, không tạo bản ghi mới |
| Cô giao bài mới/học sinh nộp mới? | Chặn409 khi lớp archived |
| Retry cùng nội dung đã nộp trước đó? | Trả bài cũ với cùng id/thời điểm |
| Retry nội dung khác? | 409, không ghi đè bài cũ |
| Chấm/công bố/thu hồi điểm cũ? | Vẫn được, theo quyền hiện có |
| Đổi tên lớp đã lưu trữ? | Vẫn được trong phạm vi cũ |

Đây là lựa chọn sản phẩm của lab, không phải chân lý mọi LMS. Việc đề nghị
“đóng mọi thao tác ghi” xung đột với nhu cầu chấm bài cũ; phải nói rõ thay vì
thêm một `if archived` vào tất cả hàm rồi coi là đủ. Nếu yêu cầu đổi, sửa bảng
policy và test trước, sau đó sửa đúng use case.

Viết state transition và dữ liệu tối thiểu:

```text
Classroom: archived boolean, mặc định false
PUT /classes/{id}/archive: không body, trả ClassOutput có archived
GET/list/create/rename cũng trả archived để FE không đoán trạng thái
Không thêm bảng archive riêng khi chưa có lịch sử ai/lúc nào/lý do
```

Tại sao boolean? Bài chỉ có hai trạng thái. Nếu thêm scheduled/locked/deleted,
enum và quy tắc chuyển có thể hợp hơn. G3 dùng chuỗi status để quan sát dễ;
G4 chọn boolean theo hợp đồng trên. Đây là thay đổi biểu diễn có chủ ý, phải
đổi parser cùng schema, không để FE chờ status trong khi BE trả archived.
PUT ở đây là đặt cờ về cùng một trạng thái, lặp request giữ cùng hiệu ứng.

**Tự viết trước:** ít nhất 8 ví dụ kiểm cả quyền, ghi, giữ lịch sử, retry và
DB cũ. Ghi chỗ có thể phát hiện archived: service archive, create assignment,
submit new; grade/read không chặn. Nếu bảng chỉ có đường thành công, chưa code.

## Buổi G4.7 — Tự lập bản đồ thay đổi, rồi thực hiện từng bước

**Đích:** tự chọn nơi đặt code và thứ tự triển khai. Viết kế hoạch của mày
trước bảng gợi ý. Tạo Git checkpoint cho source đã chạy; DB học chưa đưa Git.

| Bước | File trong xưởng | Câu phải tự trả lời |
|---|---|---|
| Mô tả cột archived | models.py | DB mới có gì, default là gì? |
| Nâng DB cũ | migration 0002 | Lớp cũ thành false, có mất title không? |
| Trả trạng thái | schemas.py | Những endpoint nào dùng ClassOutput? |
| Archive có quyền/commit | service.py | Teacher khác bị chặn trước khi ghi? |
| Cung cấp truy vấn khóa | repository.py | Cần khóa gì khi archive đua với giao bài? |
| Chặn giao/nộp mới | workflow.py | Kiểm trước/ sau tìm bài nộp cũ? |
| URL/chuyển lỗi HTTP | app.py/workflow.py | 409 khác401/403/404 ở nghĩa nào? |
| Parser/call và UI | class-api.ts + hai component | Loading, stale view, lỗi xử lý ra sao? |
| Bằng chứng | test_archive + migration test | Quan sát bằng Session mới hay object cũ? |

Tự làm backend từng bước: thêm cột+DTO; thêm archive use case; thêm route;
test quyền/record; chặn create assignment; sửa submit; test lại luồng cũ.
Cuối cùng mới nối FE. Mỗi bước chạy test liên quan; không đổi 10 file rồi đợi
browser báo một lỗi không biết xuất phát từ đâu.

Gợi ý quan trọng về retry: tìm bài nộp cũ trước; nếu cùng nội dung trả cũ,
nếu khác báo conflict. **Chỉ khi chưa có bài cũ** mới kiểm archived/deadline
để chặn nộp mới. Đặt archived ở đầu hàm sẽ chặn cả retry hợp lệ sau khi mạng
mất response; đây là lỗi về thứ tự nghiệp vụ dù từng câu if đều đúng cú pháp.

Trên MySQL, archive khóa hàng Classroom; giao bài cũng khóa hàng Classroom
trước kiểm archived/ghi, để hai transaction không đều dựa trên trạng thái cũ.
Nộp trong mẫu khóa Assignment trước rồi Classroom; archive không khóa
Assignment. Phải xem toàn bộ thứ tự khóa khi thêm workflow khác, đo contention
và có chiến lược retry lỗi transaction phù hợp. `.with_for_update()` không
biến SQLite thành MySQL; test SQLite tuần tự không chứng minh race đã được
giải trên MySQL. Không bỏ test thật rồi hứa “cân nhiều user”.

Gợi ý UI: response/parser thêm archived; list hiển thị badge; nút archive có
busy/error; thành công tải lại list. Workflow đọc trạng thái lớp, giấu form
giao/nộp mới khi archived nhưng giữ lịch sử/chấm. Một tab khác vẫn có thể đã
lưu trữ sau lần GET của mày: backend 409 là chốt, UI xử lý lỗi và cho tải lại.
Ẩn nút không phải kiểm quyền. Lab giữ nút archive trên list cho cả học sinh
để quan sát 403; sản phẩm cần UX theo quyền rõ hơn.

**Tự làm:** hoàn thành ít nhất backend trước khi mở buổi đáp án. Nếu mắc, gửi
method/URL/input, expected/actual, traceback và trạng thái DB đang thấy; câu
“không chạy” chưa đủ để khoanh đúng ranh giới.

## Buổi G4.8 — Migration và đáp án đối chiếu sau lần tự làm

**Đích:** kiểm được bản tự làm và hiểu đáp án khác mình ở quyết định nào.
Đáp án đầy đủ là [archive-solution.patch](studio/backend/archive-solution.patch).
Patch ghi chính xác các dòng thêm/đổi so với xưởng gốc, gồm BE, FE, migration
và 7 test mới; không import vào sản phẩm. Dấu `+` là dòng thêm, `-` là dòng cũ.
Đọc mỗi hunk sau khi tìm phần tương ứng trong bài của mình.

Nếu muốn chạy đáp án, tạo **bản copy mới** tên `lab-answer` bằng script G4.1.
Đứng ở gốc repo học `D:\lms-tu-hoc`, nơi đã `git init` ở G4.1. Không áp patch
lên bản đã tự sửa:

```powershell
python -X utf8 D:\vision-education-lms\docs\course\studio\backend\prepare_workshop.py .\lab-answer
git apply --check --directory=lab-answer D:/vision-education-lms/docs/course/studio/backend/archive-solution.patch
git apply --directory=lab-answer D:/vision-education-lms/docs/course/studio/backend/archive-solution.patch
.\.venv\Scripts\python.exe -X utf8 -m unittest discover -s .\lab-answer -p "test_*.py" -v
```

`--check` kiểm patch có khớp trước khi ghi. Nếu lỗi, đọc đúng file/line, kiểm
đang ở gốc repo học và đích là xưởng gốc mới copy; không dùng force để đè
bản tự làm. Test dự kiến 35 tổng,33 pass,2 skip MySQL khi chưa cấp DB thử riêng.
Test migration cần Alembic đã cài ở G4.1. Chạy riêng test mình viết rồi so
với [test archive](studio/backend/archive_test_solution.py) và
[test nâng DB cũ](studio/backend/archive_migration_test_solution.py).

DB cũ không tự có cột khi sửa models.py. `create_all` tạo bảng còn thiếu,
không nâng bảng cũ. Migration 0002 có `down_revision='0001'`, thêm cột non-null
với server_default false để lớp cũ nhận giá trị hợp lệ. DefaultPython chỉ giúp
object ORM mới; default DB còn phục vụ insert không đi qua Python. Hai phần
phục vụ hai ranh giới khác nhau. [Quy trình Alembic](https://alembic.sqlalchemy.org/en/latest/tutorial.html).

Test migration đáp án làm thứ tự **nâng 0001 → chèn lớp cũ → nâng head → đọc
title/archived**. Nó bắt lỗi mà create_all DB rỗng không bắt được. Muốn nâng
file DB học cũ đã init bằng create_all, trước hết đối chiếu schema đúng 0001,
backup bản học rồi stamp 0001 có kiểm tra và upgradehead. Chưa biết schema
cũ có đúng thì không stamp để làm mất dấu; dùng test migration tạm trước.
G6/deployment dạy quy trình backup/migrate/rollback đầy đủ hơn.

Trong frontend của lab-answer chạy `npm ci` rồi `npm run build`. Expected:
TypeScript không lỗi và Vite xuất dist. Build không chứng minh click được;
chạy server với **DB học mới** riêng cho đáp án, bật frontend, tự đi bảng
tình huống G4.6. Với DB đã dùng trướcpatch, migrate bản học đúng quy trình;
không tái dùng file cũ thiếu cột rồi đổ lỗi cho browser.

**Đọc đáp án có chủ đích:** archive có try/except rollback cả find/commit;
create assignment đưa kiểm phạm vi vào transaction; submit giữ nhánh retry
trước archived; output/parser cùng đổi. Chưa cần thuộc mọi API SQLAlchemy để
hiểu bốn điều này. Nếu mình làm khác mà giữ đúng policy và test, viết lý do
và tradeoff; cùng tên file với đáp án không phải tiêu chí đạt.

**Giới hạn kiểm chứng:** test local dùng SQLite trong RAM, request ASGI trong
process, chạy tuần tự; không phải TCP/browser/MySQL concurrency/load. Patch
frontend đã kiểm strict/build, vẫn cần thực hành browser. Không có đo tải
hay chứng minh capacity cho tính năng này. Sandbox Windows có thể treo
threadpool ASGI; khi lệnh đứng yên ở test đầu, dừng và chạy terminal local
bình thường, không thay sync endpoint thành async để né lỗi môi trường.

## Buổi G4.9 — Bài độc lập: mở lại lớp và một thay đổi chưa có mẫu

**Đích:** chứng minh tự phân tích/chia file/sửa code được. Đóng đáp án archive.
Làm trên repo học của mày: chủ lớp mở lại; active gọi lại vẫn200; học sinh403,
cô khác404; không mất lịch sử; mở lại cho phép giao/nộp mới theo deadline cũ.
Chưa cấp route/cây file/mã mẫu. Trước code viết bảng actor/action/state/data,
hợp đồng HTTP, bản đồ file với lý do và những test sẽ bác bỏ lỗi.

Gợi ý chỉ khi thật sự kẹt: một hành động gần archive, không cần thêm bảng
khi chỉ đảo trạng thái. Còn dùng archived boolean thì thường chưa cần cột mới.
Mở lại không được thay submitted_at, score hay due_at. Tự chọn URL và nêu lý
do nhất quán; BE/FE/test phải cùng hợp đồng, không phải đoán đáp án tên route.

Sau khi chạy được, nhận yêu cầu mới: “chỉ mở lại trong7 ngày từ ngày lưu trữ”.
Dừng code và tự phân tích: boolean có đủ chứng minh ngày lưu trữ không? Cần
thêm timestamp UTC, clock test được, migration cho record cũ ra sao? Chọn
policy cho lớp cũ không có timestamp, không tự bịa ngày. Viết quyết định rồi
mới sửa. Đây là bài phát hiện cấu trúc/dữ liệu cần thay đổi khi yêu cầu đổi.

Tự nghiệm thu với sáu bằng chứng:

1. Từ câu yêu cầu tự viết tình huống và giải thích chỗ mơ hồ.
2. Tự đề xuất file cần sửa, nêu được vì sao file khác không cần đổi.
3. Theo dấu một request từ input tới DB tới màn hình, biết tìm lỗi mỗi đoạn.
4. Test được quyền, không đổi dữ liệu khi lỗi, retry, lịch sử và DB cũ.
5. Đổi policy7 ngày mà không phá giao/nộp/chấm/công bố đang có.
6. Người khác đọc README của mày và chạy được từ thư mục mới theo lệnh đã ghi.

Nếu chưa đạt một ý, quay lại đúng buổi dạy năng lực đó. Không bù bằng đọc thêm
100 trang framework. Khi đạt, G5 mở rộng cách phân chia toàn LMS theo module;
G6 đưa thêm migration, bảo mật, CI, backup và hiệu năng vào bằng chứng nghiệm
thu. Một lát cắt đã chạy là nền để học tiếp, chưa tự chứng minh toàn hệ thống
đã hoàn chỉnh hoặc chịu được một số user cụ thể.

## Buổi G4.10 — Tự chia kiến trúc cho chính Vision LMS

> [!KEY]
> **Kiến trúc là phân trách nhiệm, quyền sở hữu dữ liệu và chiều phụ thuộc.**
> Cây thư mục chỉ là một cách thể hiện. Đừng tạo service/repository trước
> rồi mới tìm việc để nhét vào.

### Xác nhận dự án đang ở đâu

Mục tiêu là LMS học toán/luyện thi: admin, giáo viên, trợ giảng, học sinh;
các luồng lớp → giao bài → nộp → chấm → công bố, rồi luyện tập, tài liệu,
lịch và báo cáo. **Đây là phạm vi cần xây**, không phải mọi module đã có.

Đối chiếu source tại lần soạn 22/10/2026:

| Khu vực | Bằng chứng đang có | Điều không được suy ra |
|---|---|---|
| Backend | main.py include login/change_password/me router | Chưa có đủ lớp/bài tập/bài nộp chỉ vì đã đăng nhập được |
| Frontend | React/TS, App routes, auth features | Dashboard hiện dùng mock chưa chứng minh dữ liệu lấy từ DB |
| Bảo vệ route | App đặt dashboard ngoài nhánh AuthGuard | Đi tới dashboard chưa chứng minh request được kiểm quyền |
| Cơ sở dữ liệu | User model, SQLAlchemy và cấu hình MySQL | Chưa có schema cho toàn bộ module hoặc bằng chứng chịu tải |

Đọc [App.tsx](../../frontend/src/App.tsx),
[LoginForm](../../frontend/src/features/auth/login/components/LoginForm.tsx),
[router đăng nhập](../../backend/app/modules/auth/login/router.py),
[service đăng nhập](../../backend/app/modules/auth/login/service.py) và
[repository đăng nhập](../../backend/app/modules/auth/login/repository.py).
Snapshot source trong sách thuộc lần build; dùng source repo hiện tại để
kiểm lại nếu sản phẩm đã đổi. Các nhận xét ở đây không thay việc chạy kiểm.

### Mỗi công cụ giải quyết một việc nào?

| Công cụ thật | Trách nhiệm | Kiến thức cần hiểu trước |
|---|---|---|
| JavaScript / TypeScript | Logic runtime / kiểm kiểu lúc viết và build | Biểu thức, hàm, scope, array/object, union, narrowing |
| React | Dựng UI từ dữ liệu, state và component | JSX, props, callback, render và sự kiện |
| Vite | Dev server và build frontend | Entry/module, manifest, config, artifact |
| CSS / Tailwind | Luật bố cục / class utility biểu diễn luật | Selector, hộp, flex/grid, breakpoint, cascade |
| React Router | Chọn màn theo URL, điều hướng phía client | Route, nested layout; khác API route backend |
| Axios | HTTP client, interceptor và response | Promise, await, header/body/status, lỗi mạng |
| React Hook Form / Zod | State form / kiểm schema runtime | Event, input, callback, dữ liệu chưa tin cậy |
| FastAPI / Pydantic | HTTP route, dependency và schema validation | Hàm Python, annotation, exception, JSON |
| SQLAlchemy / PyMySQL | ORM/session / driver nối MySQL | SQL, transaction, connection, model khác DTO |
| MySQL / Alembic | Lưu và ràng buộc dữ liệu / lịch sử schema | PK/FK/UNIQUE, JOIN, index, migration |
| bcrypt / python-jose | Hash mật khẩu / ký và kiểm token | Hash khác mã hóa, hạn token, current user và quyền |
| pytest / httpx | Kiểm Python / gửi HTTP trong bài kiểm | Fixture, assertion, expected độc lập với implementation |

Không cần nhớ mọi option của tất cả tool. **Bắt buộc đọc được hợp đồng của
những API mình dùng** và lần được import. Phiếu Tra hàm/tool có input,
output, tác dụng, lỗi và link tài liệu để tra đúng chỗ khi cần.

### Phân biệt đường chạy và chiều import

Khi login, đường dữ liệu đi qua:

```text
LoginForm → authService.login → Axios → HTTP POST /login
  → FastAPI router → LoginService → LoginRepository → MySQL
  ← body JSON ← LoginResponse ← kết quả nghiệp vụ
```

Form dùng camelCase phoneNumber. Client service chuyển thành key JSON
phone_number. Router nhận LoginRequest. Repository trả User hoặc None.
Service kiểm mật khẩu/trạng thái và tạo LoginResponse. Client service trả
res.data; form nhận body và quyết định điều hướng. Mỗi mũi tên đổi **ngữ
cảnh hoặc hợp đồng**; không phải mọi object xuyên suốt đều cùng một kiểu.

**Chiều import** là quan hệ giữa module trong cùng chương trình. Ví dụ
router import service; service dùng repository. Dù response chạy ngược về
router, repository không vì thế phải import router. Với Python đã biết,
mày phải chỉ được sự khác biệt này trước khi chia package.

### Tự quyết định một hàm ở đâu bằng lý do thay đổi

Đề mới: “Giáo viên lưu trữ lớp; vẫn đọc lịch sử; không giao/nộp bài mới”.
Chưa code, phân từng câu:

| Câu hỏi | Trách nhiệm phù hợp | Vì sao |
|---|---|---|
| Body có id/title đúng dạng? | Request schema | Bảo vệ hợp đồng dữ liệu ở biên HTTP |
| Ai là người gọi? | Dependency xác thực | Biến credential thành actor đã xác minh |
| Actor có được sửa lớp này? | Policy/use case trong service | Phụ thuộc người và tài nguyên, không chỉ JSON |
| Lớp đang trạng thái nào, được chuyển không? | Domain/service | Là quy tắc nghiệp vụ dùng được ngoài HTTP |
| Tìm/cập nhật hàng nào? | Repository/query | Phụ thuộc mô hình dữ liệu và cách truy vấn |
| Ghi gì cần cùng thành công/thất bại? | Transaction boundary của use case | Tránh nửa thao tác đã commit |
| Hiển thị loading/error/đã lưu trữ? | Component/hook của feature | Là trạng thái tương tác phía người dùng |

> [!TASK]
> Tự làm lại bảng cho “mở lại lớp”, rồi cho “nộp bài lần hai”. Với mỗi hàng,
> ghi input, output, lỗi và nơi kiểm. Không xem patch đáp án trước.

### Từ trách nhiệm đến cấu trúc, không chép cây thư mục

Repo dùng nhóm frontend theo feature, backend có package module auth.
Một hướng mở rộng vừa với phạm vi hiện tại là **một backend có các module
nghiệp vụ**, dùng chung hạ tầng DB/auth. Đó là modular monolith khi ranh
giới module được giữ; không cần tách mỗi tính năng thành một service mạng.

Tự đề xuất package classes/assignments/submissions. Bên trong module chỉ
tách router/schema/service/repository khi có trách nhiệm tương ứng. Một
hàm chuẩn hóa nhỏ có thể ở domain hoặc service; không tạo năm tầng chỉ để
chuyển cùng một đối số. Entry/composition root ghép DB session, repository
và service, thay vì domain tự mở DB connection.

Frontend cũng hỏi: “component nào sở hữu state?”, “phần nào chỉ hiển thị?”,
“HTTP được bọc ở service nào?”. Một ô input nhỏ không đòi một feature mới.
Dashboard hiển thị tổng hợp, không nên tự sửa trực tiếp mọi state của lớp,
bài nộp và tài khoản bằng một object toàn cục không có owner rõ.

> [!CHECK]
> Nếu đổi CSS, policy backend không đổi. Nếu đổi kho RAM sang SQL, luật tên
> lớp không phải viết lại. Nếu đổi quy tắc hạn nộp, phải tìm được một nơi
> quyết định và các ca kiểm liên quan. Nếu chưa đạt, xem lại ranh giới.

### Nhiều user tác động kiến trúc ở đâu?

Hai request có thể đọc cùng trạng thái cũ. Không giữ dữ liệu người dùng
trong biến global của process rồi coi đó là DB chung. Worker khác có vùng
RAM khác; restart mất RAM. Dữ liệu dùng chung cần nơi lưu đúng và transaction.

Hai lần điểm danh cùng cặp buổi/học sinh cần UNIQUE hoặc policy cập nhật rõ.
Hai người sửa cùng record cần chọn concurrency policy, ví dụ revision và
UPDATE có điều kiện, rồi xử lý conflict. Đừng chỉ disable nút ở frontend:
người dùng còn có thể gửi request từ tab khác hoặc retry do mạng.

API worker, DB connection pool, query/index và tải thực tế cần được đo.
Async không làm query đồng bộ tự hết nghẽn, thêm worker không tự tăng vô hạn
DB connection. Sang P2 để tự thiết kế workload và đo, thay vì đoán sức tải.

### Bài tự thiết kế từ trang trắng

Viết đề “học sinh nộp bài; cô chỉ chấm lớp mình; công bố điểm sau khi duyệt”.
Tự làm sáu thứ, **chưa xem implementation hoàn chỉnh**:

1. Ví dụ đúng/sai cho từng actor và trạng thái, có ca gửi lại.
2. Thực thể/quan hệ, khóa và ràng buộc; giải thích lịch sử cần giữ.
3. Hợp đồng request/response/status; lấy actor ở server.
4. Sơ đồ trách nhiệm và chiều import; chỉ ranh giới transaction.
5. Cây file do mày đề xuất, mỗi file có một lý do tồn tại.
6. Một lát cắt nhỏ tự code và ca kiểm thất bại trước khi mở rộng.

Nếu một dòng cú pháp còn không giải thích được, tách dòng đó thành bài nhỏ
ở F0/02/04 hoặc Python/OOP. Kiến trúc không thay được nền cú pháp; ngược lại,
thuộc cú pháp cũng chưa tự tạo ra một hệ thống có quy tắc đúng.
