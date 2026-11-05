# F2 — Biết cú pháp nhưng gặp hàm/tool lạ: đọc thế nào?

Biết viết def/if/for chưa đồng nghĩa biết mọi method của str, Pydantic hay
SQLAlchemy. Đó là hai phần kiến thức khác nhau. Không cần học thuộc hết API;
cần biết nhận diện thứ đang gọi, đọc hợp đồng và thử một ví dụ nhỏ đúng chỗ.

## 1. Phân loại trước khi tra

| Thứ đang nhìn | Nó là gì? | Tra ở đâu trước? |
|---|---|---|
| if, return, function | Cú pháp/từ khóa ngôn ngữ | Bài cú pháp, tài liệu ngôn ngữ |
| len, str.strip | Hàm/method có sẵn của Python | Python docs, help |
| normalize_answer | Có thể là hàm người viết tự đặt | Tìm định nghĩa trong repo |
| BaseModel, Depends, Session | API của thư viện/framework | Import, version và docs thư viện |
| npm run dev, alembic upgrade | Lệnh của công cụ | Script/manifest/config và terminal help |
| padding, display, gap | Thuộc tính CSS | CSS docs + Computed trong browser |
| p-4, flex, gap-3 | Utility class Tailwind | CSS tương ứng + config/version Tailwind |

Đừng tìm một hàm của project trên Google trước khi xem import/định nghĩa. Đừng
coi mọi dấu chấm là lời gọi: `scores.length` đọc giá trị, `.map(...)` gọi method.

## 2. Một phiếu bắt buộc cho mỗi API mới

```text
Tên đầy đủ / import từ đâu / version:
Dùng để làm gì, khi nào cần:
Cách gọi (signature):
Từng đầu vào là gì, bắt buộc/tùy chọn/default nào:
Kết quả trả về là gì, có cần await không:
Có sửa dữ liệu/ghi file/gửi mạng/ghi DB không:
Lỗi nào có thể xảy ra:
Ví dụ nhỏ và output mong đợi:
Nguồn tra và chỗ dùng thật trong repo:
```

Nút **Tra hàm/tool** trong sách có các phiếu đầu tiên. Đây là bộ tra chọn lọc,
không phải danh mục mọi API. Gặp tên chưa có, tự điền phiếu này với docs đúng
phiên bản và một phép thử; không đoán chỉ từ tên “create”, “add” hay “parse”.

## 3. Ví dụ Python quen cú pháp nhưng chưa biết method

```python
raw = '  An  '
cleaned = raw.strip()
print(raw)
print(cleaned)
```

Đọc `raw.strip()`: raw là string đang nhận thao tác; strip là method của string;
`()` gọi không truyền đối số rõ. Nó trả chuỗi mới bỏ whitespace hai đầu theo
mặc định, không xóa mọi khoảng trắng bên trong và không sửa raw.

Thử với `'  An Bình  '`: giữ khoảng cách giữa An/Bình. Đừng suy ra strip luôn
nghĩa “xóa một prefix nguyên văn”; đối số chars có hợp đồng khác cần đọc riêng.

Khi biết cú pháp mà chưa biết `.strip`, chỗ thiếu là hợp đồng method này, không
phải phải học lại biến hay vòng lặp.

## 4. Đọc signature Python đúng phần tham số

Ví dụ tài liệu hiển thị `text.strip(chars=None, /)`:

- chars tùy chọn, mặc định None; gọi không truyền nó là hợp lệ.
- `/` trong signature đánh dấu nhóm positional-only; không phải ký tự cần
  gõ vào lời gọi. Đọc quy tắc signature thay vì sao chép cả dòng như code gọi.
- Dấu `*` phân tách keyword-only ở các signature khác; `*args`, `**kwargs`
  lại mô tả thu gom đối số. Không áp một nghĩa cho mọi dấu sao.

Trong môi trường Python học, thử:

```python
from inspect import signature
from pathlib import Path

print(signature(Path.read_text))
help(Path.read_text)
```

Signature/help hỗ trợ tìm tham số và mô tả, nhưng không thay ví dụ, điều kiện
biên và docs. Một số callable native/dynamic có thể không lấy được signature;
lúc đó đọc docs/source phù hợp, không kết luận nó không nhận đối số.

Không gọi thử method xóa file/ghi DB chỉ để xem “nó trả gì”. Kiểm tác dụng trước;
dùng dữ liệu giả, thư mục học hoặc test fixture khi cần thực hành tác dụng đó.

## 5. Tìm định nghĩa/import trong code thật

Ví dụ `authService.login(data)`:

1. Tìm authService được import từ đâu trong component.
2. Mở file định nghĩa login, xem tham số và dòng return.
3. Nếu nó gọi api.post, mở nơi tạo api để biết baseURL/interceptor.
4. Theo docs Axios để biết response của post; theo return để biết caller nhận gì.
5. Ghi kết quả thực tế, không kết luận từ tên biến res.

Source sản phẩm: `frontend/src/features/auth/login/services/loginService.ts`
và `frontend/src/lib/axios.ts`. Trong sách mở source đã nhúng qua bản đồ code.
Đó là snapshot; khi repo đổi, đọc lại source hiện tại.

## 6. Ví dụ Axios: kết quả của thư viện khác kết quả wrapper

Giả định API lab trả JSON `{id: 1, title: 'Lớp học'}`:

```typescript
import axios from 'axios';

const api = axios.create({ baseURL: 'http://127.0.0.1:8001' });
async function loadClass() {
  const response = await api.get('/classes/1');
  return response.data;
}
```

create nhận config, trả client; get nhận URL/config, trả Promise của response.
await lấy response khi thành công; `.data` là body. loadClass return data nên
caller nhận body sau await, không phải nguyên response kèm status/headers.

Chưa cần chạy HTTP ở buổi đầu JS. Đây là mẫu đọc hợp đồng cho lúc học API;
đừng chạy vào endpoint sản phẩm hoặc thêm token thật chỉ để hiểu kiểu trả về.
Lỗi mạng/HTTP thường đi vào catch theo config; response shape sai là vấn đề
validation riêng. Ghi `<Classroom>` trên get không tự kiểm JSON runtime.

## 7. Ví dụ FastAPI Depends: ai là người gọi hàm?

Nhìn `db: Session = Depends(get_db)` rồi hỏi bốn việc:

- Depends được import từ FastAPI, không phải hàm của SQLAlchemy.
- `get_db` được truyền vào như một callable; không gọi sớm thành get_db().
- Khi xử lý request, FastAPI giải dependency rồi truyền giá trị nhận được vào db.
- Nếu gọi hàm Python trực tiếp ngoài FastAPI, dependency không tự được resolve.

Khi get_db dùng yield, cần học thêm phần cấp tài nguyên và cleanup ở chương07.
Chưa cần thuộc mọi cơ chế DI để đọc được việc framework nhận hàm và gọi giúp.
Đừng đoán rằng Depends tạo một database hoặc tự commit dữ liệu.

## 8. Ví dụ SQLAlchemy: add, flush, commit không cùng một việc

Session.add theo dõi object cần ghi; flush gửi SQL trong transaction; commit
xác nhận transaction. Giá trị return của add không phải bản ghi mới chứa id.
Repository dùng chung Session theo request; không thử commit trên DB thật khi
chỉ đang tra method. Các tác dụng này có lab ở chương08/P0.

Đọc tên giống nhau giữa thư viện không đảm bảo hợp đồng giống nhau: append
của list, add của Session và create của Axios là ba thao tác khác.

## 9. Từ lời giải mẫu sang tự dùng được API

Sau khi tra một hàm, đóng ví dụ rồi tự đổi một đầu vào. Ghi output trước khi
chạy; thử một input lỗi trong môi trường học. Sau đó dùng hàm trong một nhiệm
vụ nhỏ do mình viết, giải thích vì sao cần nó thay vì chép nguyên cả chức năng.

Ví dụ strip: tên có whitespace ở hai đầu; map: tăng mỗi số trong danh sách;
CSS padding: nới bên trong hộp; Axios: chỉ khi đã dựng API học phù hợp. Không
cần cài thêm thư viện khi standard library/phép thử hiện có đã đủ.

## 10. Điều kiện qua bài

Tự chọn ba tên chưa quen: một của Python, một của JS/TS/thư viện và một thuộc
tính CSS. Mỗi tên có phiếu đầu vào/đầu ra/tác dụng/lỗi, ví dụ và một biến thể.
Reviewer chỉ bất kỳ dòng nào, mày nói được tên đó từ đâu và tra tiếp ở đâu.

Nguồn: [Python inspect 3.12](https://docs.python.org/3.12/library/inspect.html#inspect.signature),
[Python string methods](https://docs.python.org/3.12/library/stdtypes.html#string-methods),
[Axios response](https://axios-http.com/docs/res_schema),
[FastAPI dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/),
[SQLAlchemy Session](https://docs.sqlalchemy.org/en/21/orm/session_basics.html).
