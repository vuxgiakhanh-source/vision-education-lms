# G3 — Tự chia một chương trình Python thành những file có lý do

Mày biết biến, `if`, `for`, hàm Python. Bài này bắt đầu ở đúng chỗ đó. Chưa có
FastAPI, database hay kế thừa trong code ứng dụng. Mục tiêu là tự trả lời được:
“Có yêu cầu này, tao viết hàm nào, dữ liệu ở đâu, đặt hàm trong file nào, vì sao?”

Học 8 buổi nhỏ. Mỗi buổi chỉ qua khi mày chạy được, đổi được một chi tiết và
giải thích kết quả. Source [studio/backend](studio/backend/README.md) là đáp án
đối chiếu; tự gõ phần đang học trước khi mở toàn bộ. Gõ lại mà không dự đoán
được dữ liệu sau mỗi lời gọi thì chưa tính là tự làm.

## Buổi G3.1 — Bắt đầu bằng đầu vào, dữ liệu đang giữ và đầu ra

**Đích:** chạy một file do mày tạo. Chưa cần tạo cây 15 thư mục.

Trong thư mục `backend` của repo học riêng, tạo `hello.py` bằng editor:

```python
teacher = {'id': 1, 'role': 'teacher'}
title = '  Python  '
normalized = title.strip()
print(teacher['id'], normalized)
```

Ở terminal đang đứng trong thư mục chứa file, chạy:

```powershell
Get-Location
python --version
python -X utf8 hello.py
```

Kết quả dòng cuối là `1 Python`. `-X utf8` bảo Python dùng UTF-8, tránh lỗi in
chữ Việt trên một số terminal Windows. `hello.py` là đường dẫn tương đối từ
thư mục hiện tại. Nếu `python` không có trong PATH, dùng đường dẫn interpreter
mày đã chọn ở G0, chẳng hạn `D:\vision-education-lms\.venv\Scripts\python.exe`.

Đọc từng phần: `teacher` là dict, `teacher['id']` lấy giá trị ở khóa `id`;
`title.strip()` gọi method của chuỗi và **trả chuỗi mới**. Nó không sửa `title`.
`print` quan sát kết quả, chưa lưu dữ liệu vào đâu. Đổi thành `print(title)` sẽ
vẫn thấy khoảng trắng ngoài nếu thêm dấu `|` hai bên khi in.

**Tự đổi:** thay tên môn và id giáo viên. Viết ra trước kết quả dự đoán, rồi chạy.
**Lỗi để tự sửa:** chạy từ thư mục cha sẽ báo không tìm thấy file; đọc đường dẫn
trong lỗi, kiểm `Get-Location`, rồi `Set-Location` đúng nơi. Cài lại Python
không giải quyết một đường dẫn sai.

## Buổi G3.2 — Một file làm được việc thật

**Đích:** giáo viên tạo lớp, rồi chỉ thấy lớp của mình. Dữ liệu còn trong RAM.

Trước code, viết ba ví dụ:

| Đầu vào | Kết quả cần có | Điều không được xảy ra |
|---|---|---|
| Cô 1, tên `  Python  ` | Lớp 1, tên `Python`, chủ là 1 | Lưu tên còn khoảng trắng ngoài |
| Cô 5 xem danh sách | Không thấy lớp cô 1 | Trả tất cả rồi trông chờ giao diện giấu |
| Học sinh tạo lớp | Báo lỗi | Tăng id hoặc thêm lớp trước khi báo lỗi |

Tạo `singlefile.py`. Gõ trọn bản nhỏ này; đây cũng là nội dung file tham chiếu
[singlefile.py](studio/backend/singlefile.py):

```python
def new_store():
    return {'next_id': 1, 'classes': {}}


def normalize_title(title):
    if not isinstance(title, str):
        raise ValueError('Tên lớp phải là chuỗi')
    normalized = title.strip()
    if not 1 <= len(normalized) <= 200:
        raise ValueError('Tên lớp cần 1–200 ký tự sau khi bỏ khoảng trắng ngoài')
    return normalized


def require_teacher(actor):
    if actor['role'] != 'teacher':
        raise PermissionError('Chỉ giáo viên được thực hiện')


def create_class(store, actor, title):
    require_teacher(actor)
    normalized = normalize_title(title)
    class_id = store['next_id']
    row = {'id': class_id, 'title': normalized, 'teacher_id': actor['id'], 'status': 'active'}
    store['classes'][class_id] = row.copy()
    store['next_id'] += 1
    return row.copy()


def list_classes(store, actor):
    require_teacher(actor)
    return [row.copy() for row in store['classes'].values()
            if row['teacher_id'] == actor['id']]


def main():
    store = new_store()
    teacher = {'id': 1, 'role': 'teacher'}
    created = create_class(store, teacher, '  Python  ')
    print('Đã tạo:', created['id'], created['title'], created['status'])
    print('Số lớp của cô:', len(list_classes(store, teacher)))


if __name__ == '__main__':
    main()
```

Chạy `python -X utf8 singlefile.py`, cần thấy:

```text
Đã tạo: 1 Python active
Số lớp của cô: 1
```

Đây là chương trình nhỏ hoàn chỉnh theo phạm vi vừa chốt. Actor là dict giả
do code học cung cấp; chưa có đăng nhập. Người dùng internet không được tự
gửi `role='teacher'` để trở thành giáo viên. G4 sẽ chỉ ra actor thật đến từ đâu.

Đừng nuốt cả block bằng mắt. Lần theo một lời gọi theo sáu câu:

1. `create_class` do mình định nghĩa, nằm ngay file này.
2. Đầu vào là store, actor và chuỗi title, theo đúng thứ tự tham số.
3. `require_teacher` và `normalize_title` có thể ném lỗi trước khi ghi.
4. Dòng gán `store['classes'][class_id]` mới là chỗ thay dữ liệu.
5. `return row.copy()` trả dict để caller dùng; không phải lệnh in.
6. Nếu bị từ chối trước dòng ghi, cả danh sách và `next_id` giữ nguyên.

`isinstance(title, str)` hỏi giá trị có phải chuỗi; `raise` dừng luồng hiện tại
và ném lỗi lên nơi gọi. `1 <= len(normalized) <= 200` là so sánh nối của Python.
`row.copy()` sao chép dict nông. Bản ghi ở đây chỉ chứa số/chuỗi nên đủ cho bài;
nếu sau này có list/dict lồng thì copy nông không bảo vệ phần bên trong.

List comprehension cuối hàm tương đương:

```python
def list_classes_expanded(store, actor):
    require_teacher(actor)
    result = []
    for row in store['classes'].values():
        if row['teacher_id'] == actor['id']:
            result.append(row.copy())
    return result
```

`.values()` lấy các bản ghi từ dict lớp; `append` thêm một phần tử vào list
kết quả. Dùng phiên bản dài khi chưa đọc quen comprehension. Viết ngắn chưa
phải điều kiện code tốt.

**Tự đổi:** thêm cô 5, tạo lớp `CSS` bằng cô 5 rồi list bằng cô 1. Phải vẫn chỉ
thấy lớp cô 1. **Tự kể:** tại sao hàm không nhận `teacher_id` riêng từ caller?
Vì chủ lớp phải lấy từ actor đã được xác minh ở ranh giới ngoài.

## Buổi G3.3 — Kiểm lỗi bằng dữ liệu, không bằng câu “chạy rồi”

**Đích:** chứng minh bị từ chối thì dữ liệu chưa đổi.

Thêm đoạn sau trong `main`, sau khi tạo lớp đầu:

```python
before = store['next_id']
try:
    create_class(store, teacher, '   ')
except ValueError as error:
    print('Bị từ chối:', str(error))
print('Id giữ nguyên:', store['next_id'] == before)
print('Số lớp giữ nguyên:', len(list_classes(store, teacher)) == 1)
```

Kết quả cần có hai dòng cuối `True`. `try` thử chạy đoạn bên trong; `except
ValueError` chỉ xử lý loại lỗi đã dự kiến. `as error` đặt tên cho object lỗi;
`str(error)` lấy thông điệp. Không dùng `except: pass` để ép chương trình chạy
tiếp, vì như vậy mày không biết mình vừa làm hỏng điều gì.

**Thử có chủ đích:** đổi chỗ tăng `next_id` lên trước validation. Dự đoán test
nào hỏng rồi chạy. Sau đó sửa về. Đây là lý do thứ tự quan trọng: kiểm trước,
ghi sau. Một test chỉ kiểm “có ném ValueError” sẽ bỏ lọt lỗi ăn mất id.

**Bài giảm gợi ý:** viết tình huống học sinh tạo lớp. Không copy nguyên try
trên. Tự chọn loại lỗi và hai dữ liệu cần so trước/sau. Đáp án về ý là bắt
`PermissionError`, số lớp và `next_id` không đổi. Nếu chưa tự chọn được dữ liệu
cần quan sát, chưa chuyển sang việc tách file.

## Buổi G3.4 — Yêu cầu mới làm lộ ra lý do tách

**Đích:** biến “thêm nút lưu trữ” thành quy tắc, rồi tự đặt hàm.

Yêu cầu mới: cô muốn lưu trữ lớp cũ và vẫn đọc lịch sử. Mình chốt bản nhỏ:
chỉ chủ lớp lưu trữ; không xóa record; `active → archived`; gọi lại vẫn trả
cùng lớp. Chưa có mở lại, học sinh hay bài tập trong chương trình thuần này.

Trước khi chia file, thêm hàm trong `singlefile.py` ngay trước `main`:

```python
def archive_class(store, actor, class_id):
    require_teacher(actor)
    row = store['classes'].get(class_id)
    if row is None or row['teacher_id'] != actor['id']:
        raise LookupError('Không thấy lớp trong phạm vi của bạn')
    changed = row.copy()
    changed['status'] = 'archived'
    store['classes'][class_id] = changed.copy()
    return changed.copy()
```

`.get(key)` trả `None` khi không có khóa; `store['classes'][key]` sẽ ném
`KeyError`. `is None` hỏi có đúng giá trị đặc biệt `None` không. Nhờ `or` chạy
vế trái trước, nếu row là None thì Python không đọc `row['teacher_id']` nữa.

Gọi archive sau create, rồi list. Phải giữ nguyên id/title/teacher_id và còn
một lớp, chỉ status đổi. Gọi với cô khác và id 999 đều nhận LookupError theo
policy không lộ lớp ngoài phạm vi. Gọi lại archive không sinh record mới.

Bây giờ đọc code bằng hai mục đích khác nhau:

| Mình muốn sửa gì? | Phần cần tìm | Khi để chung có khó gì? |
|---|---|---|
| Tên tối đa 100 thay vì 200 | normalize_title | Dễ lẫn với phần in hoặc ghi |
| Thay RAM bằng DB | các dòng đọc/ghi dict | Nghiệp vụ đang biết cấu trúc kho |
| Thêm API và vẫn giữ terminal | main/print | Không muốn API chạy main khi import |
| Nhiều thao tác cần chủ lớp | kiểm owner | Dễ copy mỗi nơi một kiểu |

Một file 60 dòng vẫn có thể tốt. Ta tách khi đã chỉ được **lý do thay đổi khác
nhau**, không vì nghe rằng mọi dự án phải có service/repository ngay từ dòng 1.
Ở đây có đủ lý do: rule, cách lưu và cách trình bày bắt đầu thay độc lập.

## Buổi G3.5 — Tách hai file dưới cùng trước, chưa đổi hành vi

**Đích:** biết mình đang chuyển hàm, không viết lại toàn chương trình.

Cây trước:

```text
backend/
  singlefile.py   # rule + thao tác kho + gọi thử/in
```

Cây sau, tạo đúng tên, chưa cần package hay `__init__.py`:

```text
backend/
  domain.py       # quy tắc trên giá trị
  storage.py      # biết store có next_id/classes và cách đọc/ghi
  use_cases.py    # điều phối một hành động
  main.py         # lắp dữ liệu đầu vào và in
  test_use_cases.py
  singlefile.py   # giữ lại bản cũ để so hành vi
```

Trước tiên tạo [domain.py](studio/backend/domain.py), chuyển rule vào:

```python
def normalize_title(title):
    if not isinstance(title, str):
        raise ValueError('Tên lớp phải là chuỗi')
    normalized = title.strip()
    if not 1 <= len(normalized) <= 200:
        raise ValueError('Tên lớp cần 1–200 ký tự sau khi bỏ khoảng trắng ngoài')
    return normalized


def require_teacher(actor):
    if actor['role'] != 'teacher':
        raise PermissionError('Chỉ giáo viên được thực hiện')


def require_owner(actor, classroom):
    require_teacher(actor)
    if classroom is None or classroom['teacher_id'] != actor['id']:
        raise LookupError('Không thấy lớp trong phạm vi của bạn')
```

Nó không cần biết Python chạy từ terminal hay HTTP, không đọc store, không in.
`require_owner` gom rule sẽ dùng lại khi đổi tên/xóa/lưu trữ. Nó không trả
`True`; vượt qua nghĩa là hợp lệ, không hợp lệ thì ném lỗi.

Tạo [storage.py](studio/backend/storage.py):

```python
def new_store():
    return {'next_id': 1, 'classes': {}}


def insert_class(store, title, teacher_id):
    class_id = store['next_id']
    row = {'id': class_id, 'title': title, 'teacher_id': teacher_id, 'status': 'active'}
    store['classes'][class_id] = row.copy()
    store['next_id'] += 1
    return row.copy()


def find_class(store, class_id):
    row = store['classes'].get(class_id)
    return None if row is None else row.copy()


def all_classes(store):
    return [row.copy() for row in store['classes'].values()]


def replace_class(store, row):
    if row['id'] not in store['classes']:
        raise LookupError('Không thể thay lớp chưa tồn tại')
    store['classes'][row['id']] = row.copy()
    return row.copy()
```

`return None if ... else ...` là biểu thức điều kiện; có thể viết thành `if`
và hai `return` nếu dễ đọc hơn. `insert_class` chỉ biết lưu một bản ghi, không
quyết định ai có quyền. Gọi trực tiếp nó trong giao diện sẽ bỏ qua nghiệp vụ;
đường vào có kiểm soát của ứng dụng sẽ là use case ở buổi tiếp.

**Kiểm nhỏ:** trong terminal dùng `python -X utf8 -c "from domain import
normalize_title; print(normalize_title('  A  '))"` trên **một dòng**, kết quả
`A`. `-c` chạy đoạn Python trong chuỗi thay vì đọc file. Nếu lệnh dài khó đọc,
tạo file thử hai dòng `from domain import normalize_title` và `print(...)`.

**Lỗi để sửa:** `ModuleNotFoundError: No module named 'domain'` thường là file
chưa đúng tên/nơi hoặc interpreter chạy script ở nơi khác. Kiểm có vô tình
lưu `domain.py.txt` không. Không cài một gói tên `domain` từ mạng cho lỗi này.

## Buổi G3.6 — Ghép use case và entry, hiểu import thật sự làm gì

Tạo [use_cases.py](studio/backend/use_cases.py):

```python
from domain import normalize_title, require_owner, require_teacher
from storage import all_classes, find_class, insert_class, replace_class


def create_class(store, actor, title):
    require_teacher(actor)
    normalized = normalize_title(title)
    return insert_class(store, normalized, actor['id'])


def list_classes(store, actor):
    require_teacher(actor)
    return [row for row in all_classes(store) if row['teacher_id'] == actor['id']]


def archive_class(store, actor, class_id):
    require_teacher(actor)
    row = find_class(store, class_id)
    require_owner(actor, row)
    row['status'] = 'archived'
    return replace_class(store, row)
```

`from domain import normalize_title` tìm module `domain`, thực thi phần cấp
module của file một lần trong process, rồi lấy tên hàm đã định nghĩa. Nó chưa
gọi hàm. Gọi xảy ra ở `normalize_title(title)`. Nếu viết `print` ở đầu file,
import cũng sẽ in: đấy là tác dụng tại thời điểm import, thường không nên
dùng cho việc chạy một màn hình hoặc tạo dữ liệu.

Tạo [main.py](studio/backend/main.py):

```python
from storage import new_store
from use_cases import archive_class, create_class, list_classes


def main():
    store = new_store()
    teacher = {'id': 1, 'role': 'teacher'}
    other_teacher = {'id': 5, 'role': 'teacher'}
    created = create_class(store, teacher, '  Python  ')
    print('Đã tạo:', created['id'], created['title'], created['status'])
    archived = archive_class(store, teacher, created['id'])
    print('Đã lưu trữ:', archived['status'])
    print('Lịch sử của cô:', len(list_classes(store, teacher)))
    print('Lớp của cô khác:', len(list_classes(store, other_teacher)))


if __name__ == '__main__':
    main()
```

Khi chạy `python -X utf8 main.py`, Python đặt `__name__` của file đang chạy
bằng `'__main__'`; guard gọi `main()`. Khi `import main`, tên là `'main'`,
guard không chạy. Vì vậy test có thể import hàm mà không tự tạo/in lớp.

Kết quả cần thấy:

```text
Đã tạo: 1 Python active
Đã lưu trữ: archived
Lịch sử của cô: 1
Lớp của cô khác: 0
```

Đường phụ thuộc:

```text
main → use_cases → domain
                → storage
main → storage (chỉ để tạo kho ban đầu)
```

`domain` không import `main`; `storage` cũng không gọi giao diện. Nếu `storage`
import `use_cases` để kiểm quyền trong khi use_cases đã import storage, mày tạo
vòng import và trộn hai lý do thay đổi. Đưa rule về domain, để use_cases gọi cả
hai. Đừng chữa bằng cách import ngẫu nhiên ở giữa hàm khi chưa hiểu vòng đó.

**Bài định vị:** tên tối đa đổi sang 100: sửa domain. Đổi lời in: sửa main.
Muốn archive đổi hai bản ghi cùng lúc: điều phối ở use case; storage RAM hiện
chưa có rollback nhiều bước nên không được hứa atomic. G4 cho thấy transaction
database giải quyết phần lưu cùng nhau thế nào.

## Buổi G3.7 — Dùng test để bảo vệ ý nghĩa khi chia file

Mở [test_use_cases.py](studio/backend/test_use_cases.py) sau khi tự thử bằng
`main`. Đừng chỉ nhớ cú pháp assert; tìm dữ liệu nào làm test bác bỏ một lỗi.
Đây là một test hoàn chỉnh mày có thể tạo trước trong `test_my_rules.py`:

```python
from copy import deepcopy
import unittest
from storage import new_store
from use_cases import archive_class, create_class


class MyRulesTests(unittest.TestCase):
    def test_other_teacher_cannot_archive(self):
        store = new_store()
        owner = {'id': 1, 'role': 'teacher'}
        other = {'id': 5, 'role': 'teacher'}
        row = create_class(store, owner, 'Python')
        before = deepcopy(store)
        with self.assertRaises(LookupError):
            archive_class(store, other, row['id'])
        self.assertEqual(store, before)


if __name__ == '__main__':
    unittest.main()
```

`unittest` và `copy` là thư viện chuẩn, không cần pip. Đây là lần đầu gặp class
trong bài: `class MyRulesTests(unittest.TestCase)` khai báo nhóm test theo mẫu
API của unittest; `self` là object test hiện tại do thư viện tạo. `def
test_...` là method mà runner tìm và gọi. Chưa cần dùng kế thừa để thiết kế
ứng dụng. `with self.assertRaises(...)` yêu cầu đoạn bên trong ném đúng loại
lỗi; không ném thì test thất bại. `deepcopy` sao chép cả dict lồng để việc ghi
sai không đồng thời thay luôn “bản trước” của test.

```powershell
python -X utf8 -m unittest discover -s . -p test_my_rules.py -v
python -X utf8 -m unittest discover -s . -p test_use_cases.py -v
```

`-m unittest` chạy module test bằng interpreter đã chọn; `discover` tìm test;
`-s .` bắt đầu ở thư mục hiện tại; `-p` là tên file cần tìm; `-v` in từng test.
File tham chiếu có **9 test**. Chúng kiểm title/quyền/phạm vi/lịch sử/retry,
không đổi store khi bị từ chối, bản trả về không sửa lén kho, và create/list
trước–sau tách giữ hành vi.

**Cố ý làm test đỏ:** bỏ kiểm owner trong domain. Test cô khác phải thất bại.
Sửa lại rồi mới nhận kết quả xanh. Nếu code sai mà test vẫn xanh, test chưa
bảo vệ điều mày nghĩ nó bảo vệ. Chín test này chỉ kiểm chương trình RAM tuần
tự; chưa có HTTP, lưu bền, nhiều request hay MySQL.

## Buổi G3.8 — Giảm gợi ý, rồi thử việc chưa thấy đáp án

Làm ba mức sau theo thứ tự. Ghi quyết định trước khi code, giữ một diff riêng.

**Mẫu đã giải:** create/list/archive ở trên. Tự lần một lời gọi qua các file,
chỉ đúng dòng đầu tiên ghi state và nơi giữ quy tắc chủ lớp. Đóng source, vẽ
lại đường import, rồi mở đối chiếu.

**Giảm gợi ý — đổi tên lớp:** chỉ chủ lớp được đổi tên kể cả đã archive; trim,
1–200 ký tự; từ chối không đổi title/id/status. Mày đã có mọi hàm nhỏ cần dùng.
Tự thêm `rename_class` và ít nhất ba tình huống: đúng chủ, sai chủ, title sai.

Gợi ý tăng dần, chỉ mở nấc tiếp theo nếu đã thử:

1. Viết dữ liệu trước/sau. Field nào thay, field nào bắt buộc giữ?
2. `find_class → require_owner → normalize_title → thay bản copy → replace_class`.
3. Đáp án lõi để đối chiếu sau khi tự làm:

```python
def rename_class(store, actor, class_id, title):
    row = find_class(store, class_id)
    require_owner(actor, row)
    normalized = normalize_title(title)
    row['title'] = normalized
    return replace_class(store, row)
```

**Đề mới — mở lại lớp:** chủ lớp chuyển `archived → active`; lớp active gọi
lại vẫn active; cô khác không được; không đổi id/title và không thêm record.
Lần này tự chọn tên hàm, file, lỗi và test. Không có đáp án code ngay bên cạnh.
Nếu chưa làm được, gợi ý 1: viết bảng hai trạng thái/hai lần gọi. Gợi ý 2:
đối chiếu rule quyền đã có, không tạo thêm một kho riêng cho “lớp mở lại”.
Gợi ý 3: cần đúng một cập nhật status sau khi quyền hợp lệ; giữ cơ chế đọc/copy
và lưu đang có. Nhờ người khác đổi một điều kiện đề sau khi mày hoàn thành.

**Tự chia cấu trúc lần nữa:** thêm tính năng ghi chú theo lớp trên giấy. Một
ghi chú có id, class_id, content, author_id. Chưa code ngay. Trả lời: rule
content đặt đâu; lấy lớp và kiểm chủ ở đâu; danh sách ghi chú lưu đâu; phần in
thuộc đâu. Nếu mọi thứ đang cùng feature nhỏ, có thể giữ bốn file hiện tại.
Khi classes và notes có nhiều use case riêng, mới cân nhắc cây:

```text
backend/
  classes/  # rule/lưu/use case lớp
  notes/    # rule/lưu/use case ghi chú
  main.py   # lắp hai phần
```

Đây là lựa chọn tổ chức, không phải lệnh phải lập tức đổi imports. Dạy package
và relative imports sẽ có ví dụ cụ thể ở G4. Đừng chuyển mọi hàm khó đặt vào
`utils.py`; một file “mọi thứ chung” làm người đọc lại phải đoán nơi có rule.

**Điều kiện qua G3:** từ thư mục trắng tự làm đề mở lại lớp, chạy test, giải
thích vì sao từ chối không đổi dữ liệu, và sửa được yêu cầu “lớp active gọi lại
phải báo lỗi” tại đúng chỗ. Đọc hiểu source mà chưa làm được bước này thì học
lại buổi nhỏ tương ứng, chưa cần nhảy sang framework.
