# 05 — Python và OOP qua một nghiệp vụ thật

## Bài 05.1 — Cú pháp cần đọc được

```python
scores = [0, 8, None, 10]
graded = [score for score in scores if score is not None]
average = sum(graded) / len(graded) if graded else None
student = {'id': 12, 'full_name': 'Khánh'}
print(student['full_name'], average)
```

Python dùng thụt lề để tạo khối; dấu `:` mở khối. `None`, `True`, `False` viết hoa
chữ đầu. `is None` kiểm tra giá trị đặc biệt; `==` kiểm tra bằng nhau; `is` không
phải cách so sánh chung cho số/chuỗi. Dict dùng key; object thường dùng thuộc tính.
List comprehension tạo danh sách mới, có thể viết lại bằng for để hiểu.

```python
def normalize_answer(answer: str) -> str:
    normalized = answer.strip()
    if not normalized:
        raise ValueError('Câu trả lời không được rỗng')
    return normalized
```

Type hint giải thích hợp đồng và hỗ trợ công cụ; Python không tự kiểm tra mọi
kiểu ở runtime. Default argument được tạo khi định nghĩa hàm: tránh `items=[]`
cho tham số có thể bị sửa; dùng None rồi tạo list trong hàm.

## Bài 05.2 — Exception, import và phạm vi

```python
class EmptyAnswerError(ValueError):
    pass

def require_answer(answer: str) -> str:
    if not answer.strip():
        raise EmptyAnswerError('Hãy nhập bài làm')
    return answer.strip()

try:
    require_answer('   ')
except EmptyAnswerError as error:
    print(str(error))
```

Raise kết thúc luồng bình thường đến nơi có handler phù hợp. Không catch
Exception rồi trả thành công; chỉ bắt lỗi mình biết cách xử lý hoặc dọn tài nguyên
và ném lại. Module là file Python; import theo cấu trúc package, không tùy tiện
thêm sys.path vào từng file ứng dụng. Chạy backend từ đúng thư mục như README.

## Bài 05.3 — Class, object, self, constructor

```python
class SubmissionRepository:
    def __init__(self):
        self.answers = {}

    def find(self, assignment_id: int, student_id: int):
        return self.answers.get((assignment_id, student_id))

repo_a = SubmissionRepository()
repo_b = SubmissionRepository()
repo_a.answers[(10, 2)] = 'Đáp án A'
assert repo_b.find(10, 2) is None
```

Mỗi object có `self.answers` riêng. `self` là object nhận lời gọi; không phải từ
khóa ma thuật dành riêng cho nghiệp vụ. `__init__` khởi tạo trạng thái sau khi
object được tạo. Nếu đặt một dict dùng chung ở class rồi sửa, nhiều instance có
thể cùng nhìn một dữ liệu: phải phân biệt class attribute và instance attribute.

## Bài 05.4 — Bốn đặc tính OOP trong LMS

**Đóng gói:** service nộp bài gom quyền, hạn nộp và quy tắc chuyển trạng thái.
Cho phép mọi nơi đổi thẳng trạng thái mà bỏ qua quy tắc sẽ làm mục tiêu này yếu đi.
Tiền tố `_repository` là quy ước nội bộ, không phải khóa bảo mật Python.

**Trừu tượng:** service yêu cầu `find_submission`, không cần biết SQL cụ thể.
Tên thao tác phải mô tả điều nó làm; đừng che toàn bộ lỗi DB bằng một bool mơ hồ.

**Kế thừa:** `User(Base)` và schema kế thừa BaseModel tận dụng framework hiện có.
Một học sinh có thể có nhiều quan hệ trong lớp; không tự tạo cây User → Student
→ Teacher. Vai trò và thành viên lớp thường được biểu diễn bằng dữ liệu.

**Đa hình:** các bộ chấm cùng phương thức grade nhưng xử lý khác nhau. Ví dụ
sau chỉ chấm so sánh chuỗi chính xác, không phải bộ chấm toán hoàn chỉnh:

```python
from typing import Protocol

class Grader(Protocol):
    def grade(self, expected: str, answer: str) -> int: ...

class ExactGrader:
    def grade(self, expected: str, answer: str) -> int:
        return int(expected == answer)

class TrimmedGrader:
    def grade(self, expected: str, answer: str) -> int:
        return int(expected.strip() == answer.strip())

def score_one(grader: Grader, expected: str, answer: str) -> int:
    return grader.grade(expected, answer)

assert score_one(ExactGrader(), 'A', ' A ') == 0
assert score_one(TrimmedGrader(), 'A', ' A ') == 1
```

Protocol mô tả cấu trúc cho type checker; Python không tự cưỡng chế toàn bộ
hợp đồng khi chạy. Hai implementation không phải kế thừa Protocol mới dùng được.
Trimming có được phép hay không là quy tắc đề bài, không do OOP quyết định.

## Bài 05.5 — Composition và dependency injection

```python
class LoginService:
    def __init__(self, repository):
        self.repository = repository

    def find_user(self, phone_number: str):
        return self.repository.find_user_by_phone_number(phone_number)
```

Service sử dụng repository, không phải là repository. Truyền dependency từ
ngoài vào giúp thay bằng fake khi học/test. Trong repo, `get_auth_service`
được FastAPI dùng để tạo LoginRepository từ Session rồi tạo LoginService.

Dataclass có ích cho object dữ liệu thuần:

```python
from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class SubmittedAnswer:
    student_id: int
    answer: str
    submitted_at: datetime
```

Decorator bổ sung hành vi cho class. Frozen ngăn gán lại field theo cách thông
thường, không biến object lồng nhau thành bất biến sâu và không thay quyền truy cập.
Đừng tạo thêm ba bản sao model/schema/domain nếu chưa có trách nhiệm khác nhau rõ.

## Bài 05.6 — SOLID dùng để đặt câu hỏi

| Nguyên tắc | Câu hỏi cho project |
|---|---|
| S: trách nhiệm đơn | Service này có vừa tính điểm, gửi HTTP, truy vấn DB và render HTML không? |
| O: mở rộng | Thêm loại câu hỏi có bắt sửa khắp nơi không, hay thêm bộ chấm ở điểm được thiết kế? |
| L: thay thế | Thay bộ chấm có còn giữ hợp đồng đầu vào/đầu ra, lỗi và khoảng điểm không? |
| I: giao diện nhỏ | Service có bị buộc phụ thuộc hàng chục method không dùng không? |
| D: phụ thuộc vào hợp đồng | Logic nghiệp vụ có thể được kiểm tra mà không khởi động MySQL không? |

Đây là hướng dẫn suy nghĩ, không phải yêu cầu mỗi class phải có một interface,
factory và base class. DI hiện tại có ích nhưng chưa tự chứng minh đã áp dụng D
đầy đủ. Thêm abstraction khi có chỗ cần thay thế/kiểm thử thực tế.

## Bài viết tay

- **PY1:** đếm bài chưa nộp bằng for rồi comprehension, giải thích None và điểm 0.
- **PY2:** class repository trong bộ nhớ, hai instance không chia sẻ dữ liệu.
- **PY3:** service nhận repository ở constructor, ném lỗi riêng cho bài rỗng.
- **PY4:** thêm chính sách chấm khác và chạy cùng hàm score_one.
- **PY5:** đọc [domain.py](examples/domain.py), đóng lại, tự thực hiện quy tắc nộp bài
  từ đặc tả ở chương 10. Chưa cần giả lập database hay HTTP trong service thuần.

Qua chương khi giải thích được object đang giữ trạng thái nào, ai tạo nó,
dependency đến từ đâu và vì sao hàm thường đôi khi phù hợp hơn class.

Tham khảo: [Python Tutorial](https://docs.python.org/3/tutorial/),
[typing Protocol](https://docs.python.org/3/library/typing.html#typing.Protocol).
