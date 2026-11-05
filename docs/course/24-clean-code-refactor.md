# P1 — Clean code bằng một lần refactor có bằng chứng

> Đọc sau bài tách module có lời giải [G3](G3-python-tu-mot-file-den-module.md) và lần ranh giới HTTP/DB ở [G4](G4-thiet-ke-tinh-nang-xuyen-he-thong.md). Bài tách workflow ở cuối chương là bài tự làm tiếp theo; dùng quá trình trước/sau và tiêu chí trách nhiệm đã luyện trong G3.

Đầu ra: một diff dễ review, giữ nguyên hành vi quan trọng và giảm phụ thuộc
không cần thiết. Đọc OOP/SOLID trước; dùng code xưởng để thực hành.

## 1. Nhận diện code khó bảo trì bằng hậu quả

Code sạch giúp người khác tìm rule, hiểu tác dụng, thay yêu cầu và kiểm đúng.
Tên hay, formatter và nhiều folder có ích nhưng không đủ để chứng minh điều đó.

| Dấu hiệu | Hậu quả cần kiểm | Hướng sửa đầu tiên |
|---|---|---|
| Router vừa query, chấm, commit, gửi email | Khó rollback và test rule | Tách use case và tác dụng ngoài DB |
| Component giữ cả dữ liệu gốc lẫn filtered state | Hai nguồn lệch nhau | Tính derived data từ source/query |
| Repository commit sau mỗi add | Bước sau lỗi để lại dữ liệu dở | Đưa transaction về nghiệp vụ |
| Catch mọi exception thành success/400 | Che lỗi, client hiểu nhầm | Bắt loại đã biết, rollback rồi ném lại |
| Tách mỗi dòng thành một class | Khó theo luồng hơn | Gom theo trách nhiệm có thật |
| Mọi module import model nội bộ của nhau | Đổi schema phá lan rộng | Định hợp đồng tại ranh giới cần thiết |

Đọc một PR bằng câu hỏi: thay đổi này làm hành vi gì dễ hiểu/kiểm/thay hơn?
Nếu không chỉ được, có thể mới là đổi hình thức.

## 2. Chốt hợp đồng trước khi đụng cấu trúc

Trước refactor ClassService.create, ghi: chỉ teacher, trim title, giới hạn
1..200 code point, teacher_id từ actor, thành công được commit, lỗi không để
lại lớp mới. Response/status/quyền phải giữ nguyên.

Chạy bộ test hiện có, lưu kết quả và diff sạch liên quan. Không dùng coverage
cao để suy ra đã giữ đủ hợp đồng; chọn test quan sát được ở DB/API.

Nếu chưa có test cho lỗi sau flush, viết trước. Cho repository add rồi ném lỗi;
dùng Session mới xác nhận row không tồn tại. Một test chỉ kiểm `.commit()` gọi
một lần sẽ không phát hiện code commit quá sớm trước tác dụng thứ hai.

## 3. Trước refactor: service biết chi tiết repository

Phiên bản trước có đoạn sau, chỉ dùng để đọc và so sánh:

```python
def create_before(repository, classroom):
    try:
        repository.add(classroom)
        repository.db.commit()
    except Exception:
        repository.db.rollback()
        raise
```

Service phải biết repository có `.db`; fake muốn test cũng phải giả một session.
Khi cần hai repository chung transaction, dependency này làm trách nhiệm mơ hồ.
Nó chưa tự gây lỗi dữ liệu, nhưng là điểm nên sửa khi nghiệp vụ đã có nhiều bước.

Không tách thêm framework transaction tổng quát cho mọi loại tài nguyên. DB
transaction không thể tự rollback email hay file; đó là contract khác.

## 4. Sau refactor: transaction là dependency rõ

Mở [unit_of_work.py](workshop/lms_lab/unit_of_work.py) và
[service.py](workshop/lms_lab/service.py). Transaction chỉ yêu cầu commit/rollback;
SqlTransaction adapter giữ session. Repository vẫn add/flush/query.

```python
def create_after(repository, transaction, classroom):
    try:
        repository.add(classroom)
        transaction.commit()
    except Exception:
        transaction.rollback()
        raise
```

Ý nghĩa từng dòng: add tạo thay đổi trong transaction hiện tại; commit thuộc
use case; catch dọn phần DB khi lỗi; raise giữ thông tin lỗi cho caller. Không
trả thành công ở finally, không bắt lỗi xong nuốt traceback.

Composition root trong app.py lắp ClassRepository(db) và SqlTransaction(db)
bằng cùng Session. Hai adapter dùng hai Session sẽ không còn atomic; thêm một
interface không tự làm kiến trúc đúng. Auth đã SELECT có thể mở transaction;
không tự thêm `db.begin()` lồng khi chưa xét lifecycle.

Service vẫn tạo ORM Classroom trong ví dụ. Đây là mức tách vừa đủ của lab,
chưa phải domain hoàn toàn độc lập SQLAlchemy. Khi cần domain thuần, có thể
thêm object/result và adapter mapping; phải nêu lợi ích cụ thể trước khi tạo.

## 5. Quy trình refactor từng bước để tự làm lại

1. Đọc tests và ghi những behavior phải giữ.
2. Thêm Transaction Protocol và SqlTransaction, chưa đổi query hay API.
3. Đổi constructor service, thay hai lời gọi commit/rollback.
4. Sửa composition root và các test khởi tạo trực tiếp.
5. Chạy tests quyền, trim, persistence, rollback và workflow.
6. Xem diff: có vô tình đổi status, schema, filtering hoặc seed không?

Trong repo học, làm lại refactor từ đoạn before rồi so với source after. Nếu
muốn thay contract API, tạo bước riêng với tests mới; đừng trộn vào refactor
cấu trúc rồi nói “hành vi không đổi”.

## 6. Refactor frontend bằng trạng thái và ranh giới

Đọc [WorkflowPractice.tsx](workshop/frontend/WorkflowPractice.tsx). Page chọn
lớp; AssignmentPanel tải bài nộp; GradeForm giữ draft điểm/công bố. HTTP/parser
ở workflow-api.ts. State form không đồng nghĩa dữ liệu đã lưu server.

Một bài refactor tiếp theo: tách hook tải dữ liệu có trạng thái loading/error/
success và cancellation. Viết contract: đổi token/lớp thì response cũ không
được ghi vào dữ liệu mới; lỗi giữ input; unmount không cập nhật vùng cũ.

Không tạo hook chỉ để giấu ba dòng mà làm caller khó hiểu dependency. Khi dùng
server-state library, thiết kế query key có actor/scope, invalidation sau ghi
và xóa dữ liệu riêng khi logout. Memoization chỉ thêm khi có số đo vấn đề render.

## 7. Các quy ước cần thống nhất trong một dự án

| Mảng | Quy ước phải viết | Cách kiểm |
|---|---|---|
| Tên | Động từ cho hành động, domain term thống nhất | Đọc use case không phải đoán |
| Lỗi | Domain error → status tại boundary | Không lộ SQL/traceback qua response |
| Kiểu | TS strict; Python hint tại public boundary | Compiler/type checker + runtime parser |
| Module | Public API nhỏ, tránh import vòng | Vẽ dependency, đổi rule thử |
| Dữ liệu | Không sửa input ngoài contract | Test bản gốc sau hành động |
| Comments | Ghi lý do/giới hạn quan trọng | Xóa comment chỉ đọc lại tên hàm |
| Dependencies | Runtime/dev và lock tái lập | Cài sạch, không nhờ node_modules cũ |

Lab frontend bật strict. Sản phẩm hiện tại chưa bật toàn bộ strict; việc này
không tự thay cấu hình sản phẩm. Backend lab chưa có bước static type checker
bắt buộc; chọn và cấu hình công cụ khi chuẩn hóa pipeline, không báo đã có.

## 8. Review một PR có khả năng bảo trì

Mô tả PR phải nói: vấn đề gì, trigger nào, hành vi sau sửa, vì sao tách trách
nhiệm như vậy, đã kiểm gì và giới hạn. Reviewer lần theo một request, tìm quyền,
transaction, lỗi và schema change. Xem cả test có bắt được bug trước sửa không.

Tránh checklist “đủ SOLID” mà không có tình huống. Một hàm thuần dễ đọc có thể
tốt hơn năm interface; một abstraction có test thay adapter thật có thể cần.

## 9. Bài tập và bảo vệ

**Điền:** fake transaction đếm commit/rollback để kiểm luồng điều phối; bổ sung
integration DB xác nhận effect. Giải thích hai test chứng minh khác nhau gì.

**Trắng:** tách workflow.py thành schemas/repository/service/router cùng module,
không đổi URL/response/quyền. Chạy lại acceptance matrix và diff trước/sau.

**Sửa lỗi:** cố ý lắp repository và transaction bằng Session khác trong repo
học. Viết test quan sát orphan/không commit được dữ liệu, rồi sửa composition.

Qua khi reviewer đổi “điểm nguyên” thành Decimal theo một policy rõ và mày chỉ
được các boundary phải đổi, giữ điểm 0, validation, DB và output nhất quán.
Đừng sửa chỉ type ở TypeScript rồi coi cả hệ thống đã hỗ trợ điểm thập phân.
