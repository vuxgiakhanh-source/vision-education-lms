# 08 — SQLAlchemy, repository và migration

Trước bài này phải viết được SQL SELECT/JOIN và giải thích transaction. ORM
giúp thao tác object; nó không loại bỏ việc hiểu SQL hoặc quyền dữ liệu.

## Bài 08.1 — Ba đối tượng khác nhau

Engine quản lý kết nối/pool; Session theo dõi thay đổi và đơn vị làm việc;
model ánh xạ dữ liệu. Repo tạo một Engine, SessionLocal tạo Session cho request,
get_db đóng Session sau khi dùng. Không dùng một Session global chung cho mọi request.

`session.add` đánh dấu cần lưu; `flush` gửi thay đổi xuống DB trong transaction,
thường giúp có id; `commit` xác nhận transaction; `rollback` hủy transaction.
Flush không có nghĩa dữ liệu đã được commit và tồn tại sau lỗi ở bước sau.

## Bài 08.2 — Model, schema, domain khác trách nhiệm

| Đối tượng | Trách nhiệm |
|---|---|
| Model ORM | Bảng/cột, quan hệ, trạng thái gắn với Session |
| Schema Pydantic | Hợp đồng vào/ra API, validation tương ứng |
| Object nghiệp vụ thuần nếu cần | Quy tắc/trạng thái có thể kiểm thử độc lập framework |

Repo hiện dùng `Column`/`db.query`, có thể tiếp tục nhất quán. Ví dụ riêng sau
dùng API typed để học, không đổi Base hoặc User đang chạy:

```python
from sqlalchemy import String, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

class LearningBase(DeclarativeBase):
    pass

class LearningClass(LearningBase):
    __tablename__ = 'learning_classes'
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)

class ClassRepository:
    def __init__(self, db: Session):
        self.db = db

    def add(self, title: str) -> LearningClass:
        classroom = LearningClass(title=title)
        self.db.add(classroom)
        self.db.flush()
        return classroom

    def list_page(self, offset: int, limit: int) -> list[LearningClass]:
        statement = select(LearningClass).order_by(LearningClass.id).offset(offset).limit(limit)
        return list(self.db.scalars(statement).all())
```

Mapped là kiểu thuộc tính ORM, mapped_column khai báo cột; String(200) giới hạn
theo schema DB, vẫn cần validation API. `select` mô tả truy vấn; `scalars` lấy
đối tượng/cột chính thay vì Row chứa tuple. Với code cũ `db.query`, hiểu câu SQL
tương đương trước khi nghĩ đến đổi phong cách.

## Bài 08.3 — Quyền sở hữu transaction

Một nghiệp vụ tạo lớp và thêm cô làm thành viên phải cùng thành công. Repository
không commit riêng từng bước; service điều phối commit/rollback. Minh họa cấu
trúc, các repository membership phải được tự xây sau khi chốt mô hình:

```python
def create_class_with_owner(db, class_repository, membership_repository, title, teacher_id):
    try:
        classroom = class_repository.add(title)
        membership_repository.add(classroom.id, teacher_id, 'teacher')
        result = {'id': classroom.id, 'title': classroom.title}
        db.commit()
        return result
    except Exception:
        db.rollback()
        raise
```

Ở đây bắt Exception chỉ để rollback rồi ném lại; không biến mọi lỗi thành lỗi
người dùng. Auth hiện có repository commit cho thao tác đơn; khi mở rộng nhiều
bước, phải chọn boundary rõ, tránh hai bên cùng commit. Đừng đổi auth đang chạy
chỉ để khớp một bài mẫu mà chưa có bài kiểm tra tương ứng.

`with db.begin()` là cách quản lý transaction khác; Session có thể đã tự mở
transaction sau một lần SELECT trong dependency auth, nên không gọi begin lồng
một cách mù quáng. Commit có thể expire thuộc tính model; đừng truy cập lazy
relationship sau khi Session đã đóng. Tạo response trong phạm vi phù hợp, lấy
đủ dữ liệu cần trả và không dùng refresh để chữa mọi lỗi vòng đời.

## Bài 08.4 — Quan hệ và truy vấn lặp

Relationship hỗ trợ điều hướng object, FK mới là ràng buộc tham chiếu ở DB.
Một trang 20 lớp mà mỗi lớp truy vấn thêm học sinh có thể tạo N+1 query.
Quan sát SQL/log và dùng truy vấn tổng hợp/eager loading phù hợp, như selectinload
khi cần. Đừng eager-load mọi bảng; chỉ lấy dữ liệu màn hình thực sự cần.

Không trả toàn bộ quan hệ lồng nhau vô hạn. Thiết kế response danh sách gọn,
chi tiết riêng, phân trang từ backend.

## Bài 08.5 — Alembic lưu lịch sử thay đổi schema

Trên môi trường phát triển đã cấu hình và sau khi kiểm tra dữ liệu mục tiêu:

```powershell
cd backend
..\.venv\Scripts\python.exe -m alembic current
..\.venv\Scripts\python.exe -m alembic revision --autogenerate -m "add classes and memberships"
```

Đây là hướng dẫn thực hành, không phải lệnh đã chạy trong lần soạn giáo án.
Trước autogenerate phải khai báo/import model vào metadata được Alembic đọc;
repo hiện `alembic/env.py` import User và Base.metadata.

Mở file migration vừa tạo: kiểm tra tên, kiểu, null/default, index, FK, dữ liệu
cũ có chuyển được không, downgrade có mất dữ liệu không. Autogenerate là bản
nháp; đổi tên cột có thể bị nhận thành xóa/thêm. Chỉ sau review và thử trên DB
phát triển mới áp dụng bằng `alembic upgrade head`. Không sửa migration đã được
phát hành cho người khác để làm lịch sử trông đẹp hơn.

## Bài tự viết

- **ORM1:** dịch query lấy bài đã công bố của lớp từ SQL sang ORM; xem SQL tương đương.
- **ORM2:** tạo lớp kèm thành viên; gây lỗi bước hai và xác nhận lớp không lưu.
- **ORM3:** ràng buộc unique bài nộp và xử lý đúng khi gửi hai request cùng lúc.
- **ORM4:** tạo migration, đọc trước khi apply; kiểm tra trên DB mới và DB có fixture.
- **ORM5:** đếm query khi mở danh sách; tìm một trường hợp N+1 và sửa có bằng chứng.

Qua chương khi giải thích được add/flush/commit/refresh/rollback và vòng đời
Session. Ví dụ ORM trong giáo án được kiểm tra cú pháp; migration/query MySQL
phải được thực hành trên DB riêng để xác nhận hành vi thật.

Tham khảo: [SQLAlchemy Session](https://docs.sqlalchemy.org/en/20/orm/session_basics.html),
[Alembic autogenerate](https://alembic.sqlalchemy.org/en/latest/autogenerate.html).

## Xưởng — Lifecycle có thể quan sát

```text
Session mới → add(object): theo dõi pending
 → flush: gửi SQL trong transaction, có thể nhận id/lỗi constraint
 → commit: flush nếu cần và xác nhận transaction
 → close: dọn Session/connection theo cơ chế thư viện
Khi thao tác lỗi → rollback trước khi tiếp tục dùng Session phù hợp
```

SELECT có thể kích hoạt autoflush. Id sau flush chưa chứng minh một Session
khác đọc được bản commit. Sau commit, thuộc tính có thể expire theo config;
lazy load sau close có thể lỗi. Chọn query/DTO/lifecycle rõ, không dùng Session
global suốt đời process. Reference xưởng chọn expire_on_commit=False có chủ đích.

## Xưởng — Transaction qua hai repository

```text
Service kiểm quyền và input
 → class_repository.add dùng Session A
 → flush lấy id
 → membership_repository.add cũng dùng Session A
 → commit chung
Nếu lỗi ở bất cứ bước ghi nào → rollback → ném lại lỗi phù hợp
```

Hai repo phải cùng Session và không commit riêng. Context transaction là một
cách tổ chức khác; xét autobegin/request trước khi lồng db.begin tùy tiện.
Test gây lỗi ở bước 2 rồi dùng Session mới xác nhận bước 1 không được lưu.
Đừng chỉ assert rollback được gọi trong mock.

## Xưởng — Relationship, query có scope và migration

Relationship điều hướng object/loading; FK/UNIQUE giữ constraint ở DB.
Endpoint list cần actor filter và pagination ngay query. Tải100 lớp rồi lazyload
học sinh từng lớp có thể N+1; quan sát số query và dùng join/selectinload/
tổng hợp tùy mục tiêu. Tránh join nhiều quan hệ làm nhân hàng.

DTO không serialize cả graph có password hoặc submission chưa công bố.
Total và items phải cùng filter/scope. Thêm status cho lớp cần default/backfill
hàng cũ,nullable policy,app cũ/app mới và kế hoạch quay lại. Autogenerate không
hiểu mọi rename; drop+add có thể mất dữ liệu. Revision đã áp dụng cần được
tiếp nối bằng revision mới có review, không sửa lịch sử tùy tiện.

**Điền:** model theo ERD với PK/FK/index. **Trắng:** repo list đúng scope,
không commit/HTTPException. **Sửa lỗi:** IntegrityError rồi query tiếp thiếu
rollback; sửa lifecycle và kiểm dữ liệu/request kế tiếp trên DB học.
