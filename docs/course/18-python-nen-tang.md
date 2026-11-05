# Python trước OOP: đọc, viết và sửa từng khối lệnh

## 1. Chạy một file và hiểu thứ tự

Trong repo học riêng, tạo `hello.py`:

```python
student_name = 'Khánh'
completed = 2
print(student_name)
print(completed + 1)
```

Chạy bằng interpreter đã chọn: `python hello.py`. Python thực hiện top-level
từ trên xuống. Đặt tên hàm chưa thực hiện thân hàm. Import một module có code
top-level cũng có thể thực hiện code đó; vì vậy không đặt seed DB hoặc tác vụ
xóa dữ liệu ở top-level của module ứng dụng.

## 2. Kiểu giá trị và phép tính

| Cú pháp | Ý nghĩa | Lỗi dễ gặp |
|---|---|---|
| `name = 'An'` | Gán chuỗi | Không có khai báo let/const |
| `count = 2` | Số nguyên | Đầu vào HTTP có thể là chuỗi |
| `score = 8.5` | Số dấu phẩy động | Không dùng tùy tiện cho tiền/đáp án số chính xác |
| `active = True` | Boolean | Viết hoa True/False |
| `grade = None` | Chưa có điểm theo hợp đồng | 0 là điểm hợp lệ khác None |
| `a == b` | Bằng nhau về giá trị | `is` kiểm identity, không thay == |
| `a and b` | Short-circuit | Có thể trả toán hạng, không chỉ bool |
| `not active` | Đảo truthiness | `bool('false')` vẫn True |

```python
raw = ' 12 '
number = int(raw)
assert number + 1 == 13
assert bool('false') is True
assert 7 // 2 == 3
assert 7 % 2 == 1
```

`int('abc')` ném ValueError. Đọc lỗi để biết chuyển đổi sai, không chữa bằng
đổi mọi giá trị thành 0. Python int không có cùng giới hạn biểu diễn như JS
Number; API vẫn cần hợp đồng id và giới hạn dữ liệu chung giữa hai phía.

## 3. Thụt lề là cấu trúc

```python
score = 0
if score is None:
    label = 'Chưa chấm'
elif score >= 5:
    label = 'Đạt'
else:
    label = 'Cần ôn'
print(label)
```

`:` mở khối. Các dòng cùng thụt lề thuộc cùng khối. Dòng print không thụt lề
chạy sau toàn bộ if/elif/else. Với score=0, nhánh cuối chạy. `if not score`
sẽ gom cả 0 và None, khác hợp đồng bài này. Dùng 4 spaces nhất quán; không trộn tab.

## 4. List, dict, tuple, set

```python
students = ['An', 'Bình']
student = {'id': 1, 'name': 'An'}
pair = (7, 1)
seen_ids = {1, 2}
students.append('Chi')
assert students[0] == 'An'
assert student['name'] == 'An'
assert student.get('email') is None
assert pair == (7, 1)
assert 2 in seen_ids
```

List có thứ tự và sửa được. Tuple giữ vị trí phần tử, thường dùng khóa ghép;
tuple chứa object mutable không làm object đó bất biến. Dict tìm theo key;
`student['email']` thiếu key ném KeyError, `.get` có default. Set giữ giá trị
không trùng, không phải cấu trúc dùng để giữ thứ tự nghiệp vụ.

## 5. Viết vòng lặp trước comprehension

```python
scores = [0, 8, None, 10]
graded = []
for score in scores:
    if score is not None:
        graded.append(score)

if len(graded) == 0:
    average = None
else:
    average = sum(graded) / len(graded)
```

Vết: [] → [0] → [0,8] → [0,8] → [0,8,10]. Tổng18, số3, trung bình6.
Chỉ khi giải thích được mới rút gọn:

```python
graded = [score for score in scores if score is not None]
average = sum(graded) / len(graded) if graded else None
```

`for score in scores` duyệt giá trị; `for index, score in enumerate(scores)`
có cả vị trí. `break` thoát vòng lặp, `continue` sang lượt kế, `return` thoát
hàm. Đặt return trong for có thể làm bạn xử lý đúng một phần tử rồi kết thúc.

## 6. Hàm và hợp đồng

```python
def average_graded(scores: list[int | None]) -> float | None:
    graded = [score for score in scores if score is not None]
    if not graded:
        return None
    return sum(graded) / len(graded)

assert average_graded([0, None, 10]) == 5
assert average_graded([None]) is None
```

`def` định nghĩa hàm. `scores` là tham số; annotation mô tả kiểu mong đợi.
`->` mô tả kiểu trả về. Python không tự cấm mọi lời gọi sai annotation.
Hàm trên giả định đúng kiểu số/ngữ cảnh điểm; validation dữ liệu ngoài hệ thống
thuộc schema/service. Docstring có thể ghi rõ giới hạn đó.

```python
def append_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```

Default được tính khi định nghĩa hàm. Viết `items=[]` có thể khiến nhiều lời gọi
chia sẻ cùng list. Mẫu None tạo list mới cho mỗi lần cần default, nhưng nếu
caller truyền list thì hàm này sửa list của caller: phải ghi hợp đồng rõ.

## 7. Tham chiếu và copy

```python
original = {'meta': {'attempts': 1}}
alias = original
shallow = original.copy()
shallow['meta']['attempts'] = 2
assert alias['meta']['attempts'] == 2
next_value = {**original, 'meta': {**original['meta'], 'attempts': 3}}
assert original['meta']['attempts'] == 2
assert next_value['meta']['attempts'] == 3
```

Tên khác không tự tạo object khác. Copy dict nông vẫn dùng chung dict con.
Đây là cùng loại vấn đề đã gặp ở JavaScript. Với ORM, sửa object còn có thể được
Session theo dõi; không đưa ORM object đang sống sang mọi lớp mà không hiểu lifecycle.

## 8. Exception: đường chạy thứ hai

```python
def require_title(value: str) -> str:
    title = value.strip()
    if not title:
        raise ValueError('Tên lớp không được rỗng')
    return title

try:
    title = require_title('   ')
    print('Dòng này không chạy')
except ValueError as error:
    print(str(error))
finally:
    print('Kết thúc lần thử')
```

Raise bỏ phần còn lại của đường bình thường cho đến handler phù hợp. Finally
phục vụ dọn tài nguyên; đừng return trong finally vì có thể che lỗi/kết quả.
Chỉ catch lỗi bạn xử lý có ý nghĩa. Exception domain được router ánh xạ sang
HTTP, không nhất thiết service phải biết FastAPI.

## 9. Module, package và import

```text
learning_project/
  app/
    __init__.py
    main.py
    services.py
```

`from app.services import ...` cần interpreter tìm được app trên module path.
Chạy từ learning_project bằng `python -m app.main` cho package context rõ.
`if __name__ == '__main__':` dùng để chỉ chạy phần CLI khi module được thực thi
trực tiếp; phần định nghĩa vẫn import được cho test. Không sửa sys.path lung
tung để import “hết đỏ” rồi không hiểu process production chạy từ đâu.

## 10. Generator, yield và context manager

```python
from contextlib import contextmanager

@contextmanager
def tracked_resource():
    print('mở')
    try:
        yield {'ready': True}
    finally:
        print('đóng')

with tracked_resource() as resource:
    assert resource['ready'] is True
```

Context manager thực hiện mở → thân with → dọn. Yield không giống return:
generator có thể tạm dừng và tiếp tục. Dependency get_db trong FastAPI tận dụng
yield để đóng Session sau xử lý. `db.close()` dọn Session không đồng nghĩa đã
commit nghiệp vụ thành công. Chương ORM chỉ rõ commit/rollback riêng.

## 11. Chuỗi, JSON, thời gian và file

```python
import json
from datetime import datetime, timezone
from pathlib import Path

payload = {'title': 'Đại số', 'score': None}
encoded = json.dumps(payload, ensure_ascii=False)
assert json.loads(encoded)['score'] is None
now = datetime.now(timezone.utc)
example_path = Path('notes') / 'lesson.txt'
```

JSON là định dạng trao đổi, dict là object Python trong RAM. None thành null.
Thời gian cần timezone nhất quán; datetime naive/aware không nên so sánh tùy
tiện. Path từ người dùng phải được kiểm soát, không ghép vào đường dẫn nhạy cảm.
Dùng `with open(..., encoding='utf-8')` khi cần đọc/ghi file bài học.

## 12. Bài tự viết và tự kiểm

1. Viết lại average_graded bằng vòng lặp, không dùng comprehension.
2. Viết `normalize_title`, từ chối rỗng sau trim; test khoảng trắng, tên dài,
   dữ liệu sai kiểu theo hợp đồng bạn chọn.
3. Tạo hai dict chứa list, chứng minh copy nông chia sẻ gì; cập nhật đúng mức.
4. Tách một hàm sang module và import bằng cấu trúc package chuẩn.
5. Viết unittest cho điểm 0, không điểm, một lỗi và một trường hợp đúng.

<details><summary>Khung unittest để tự hoàn thiện</summary>

```python
import unittest

class AverageTests(unittest.TestCase):
    def test_zero_is_a_grade(self):
        self.assertEqual(average_graded([0, None, 10]), 5)

    def test_missing_is_not_zero(self):
        self.assertIsNone(average_graded([None]))
```

Đặt import từ module của bạn ở đầu file. Chạy bằng `python -m unittest` theo
đúng thư mục/package. Cố tình sửa sai hàm để xác nhận test có thể đỏ.

</details>

Qua bài khi tự viết được hàm và test, đọc traceback từ dòng gọi đến nguyên nhân,
giải thích exception/import/yield. Sau đó mới học class/self/Protocol.
Đối chiếu [Python Tutorial](https://docs.python.org/3/tutorial/).
