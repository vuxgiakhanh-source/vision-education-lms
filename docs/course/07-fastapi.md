# 07 — FastAPI, Pydantic và hợp đồng API

## Bài 07.1 — Endpoint, schema và kiểm tra đầu vào

Ví dụ học độc lập: endpoint chỉ chuẩn hóa và trả dữ liệu, chưa lưu DB hay kiểm
tra quyền. Không thêm trực tiếp endpoint này vào ứng dụng thật để giao bài.

```python
from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field

app = FastAPI()

class PreviewRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    title: str = Field(min_length=1, max_length=200)
    class_id: int = Field(gt=0)

class PreviewResponse(BaseModel):
    title: str
    class_id: int

@app.post('/learning/preview', response_model=PreviewResponse)
def preview(payload: PreviewRequest):
    return PreviewResponse(title=payload.title.strip(), class_id=payload.class_id)
```

Decorator đăng ký method/path. Pydantic đọc JSON thành model và kiểm tra trường.
`extra='forbid'` từ chối trường lạ ở ví dụ này. Min length trước `.strip()` vẫn
cho chuỗi toàn khoảng trắng đi qua: bài tiếp theo sửa đúng ở schema, không tưởng
validation hiện tại đã đủ.

## Bài 07.2 — Chuẩn hóa có chủ đích

```python
from pydantic import BaseModel, Field, field_validator

class ClassCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)

    @field_validator('title', mode='before')
    @classmethod
    def strip_title(cls, value):
        return value.strip() if isinstance(value, str) else value
```

`mode='before'` chạy trước kiểm tra chính nên chuỗi rỗng sau trim bị từ chối.
`cls` là class, khác self của instance. Validation hình dạng/giới hạn ở schema;
quyền tạo lớp hoặc lớp đã đóng thuộc service vì cần ngữ cảnh và dữ liệu DB.
Pydantic có thể chuyển đổi một số kiểu; nếu yêu cầu strict, khai báo có chủ đích
và test giá trị chuỗi/số/null. Cấm field không thay thế kiểm tra quyền.

## Bài 07.3 — Path, query, body và response

Trong một router tương lai, có thể nhận `class_id` từ path, page/page_size từ
query, nội dung tạo mới từ body. Dùng `Field`, `Query` hoặc `Path` để đặt giới hạn
theo đúng nguồn. Path id hợp lệ về kiểu chưa có nghĩa bản ghi tồn tại.

Response schema phải riêng với model chứa hashed_password. Không trả cả `user`
dưới dạng dict tùy tiện. Response được chọn field rõ còn giúp frontend có hợp đồng ổn định.
404 với tài nguyên ngoài phạm vi hoặc 403 phải được chốt nhất quán để hạn chế
lộ sự tồn tại; không chọn tùy hứng ở mỗi endpoint.

## Bài 07.4 — Depends là cách lắp thành phần

```python
from fastapi import Depends

class ExampleRepository:
    def count(self) -> int:
        return 0

def get_example_repository():
    return ExampleRepository()

@app.get('/learning/count')
def count_items(repository: ExampleRepository = Depends(get_example_repository)):
    return {'count': repository.count()}
```

FastAPI gọi provider để lấy đối tượng. Trong repo, get_db yield một Session,
provider tạo repository từ Session và service từ repository. `yield` cho phép
cleanup sau khi xử lý. Khi gọi hàm Python trực tiếp ngoài FastAPI, Depends không
tự chạy như một phép màu: bạn phải cung cấp dependency thật hoặc dùng HTTP test client.

## Bài 07.5 — Router/service/repository và lỗi

Trình tự đề xuất phù hợp repo:

1. Router đọc request và current user qua dependency.
2. Service kiểm tra quyền, trạng thái và quy tắc, gọi repository.
3. Repository truy vấn/lưu; transaction boundary thống nhất ở service cho nghiệp vụ nhiều bước.
4. Router đổi exception nghiệp vụ đã biết thành HTTP response.
5. Lỗi không dự kiến được ghi log có mã tham chiếu; không trả stack trace hoặc SQL cho người dùng.

Không để mọi endpoint có truy vấn SQL riêng rồi copy kiểm tra quyền. Không catch
mọi Exception và đổi thành 400 vì lỗi lập trình/DB không phải lúc nào cũng do client.
Mô hình lỗi có thể dùng `code`, `message`, `field_errors`, nhưng cần thống nhất
với Axios và form trước khi đưa vào sản phẩm.

## Bài 07.6 — def, async def và tác vụ đồng bộ

Repo hiện dùng SQLAlchemy Session đồng bộ. Endpoint `def` có thể phù hợp cách
dùng đó. Viết `async def` rồi gọi DB đồng bộ không tự biến DB thành bất đồng bộ;
có thể chặn event loop. Chỉ chuyển stack async sau khi hiểu driver, Session và
đường đi của từng lời gọi. Không tăng độ phức tạp chỉ vì async nghe hiện đại.

CORS là quy tắc trình duyệt cho phép đọc response từ origin khác; nó không phải
cơ chế xác thực hoặc phân quyền. Backend vẫn phải kiểm tra mọi request dù client
không phải trình duyệt.

## Bài tự viết

- **API1:** sửa preview để từ chối chuỗi toàn khoảng trắng, thử cả missing/null/số.
- **API2:** mô tả request/response/error của API tạo lớp trước khi viết endpoint.
- **API3:** endpoint danh sách lớp với page >= 1, page_size có giới hạn và response rõ.
- **API4:** đổi dependency sang fake trong test, chứng minh router không buộc dùng DB thật.
- **API5:** kiểm tra OpenAPI docs và một client HTTP, giải thích 401/403/404/409/422.

Qua chương khi tự viết một endpoint và giải thích từng dependency, validation,
exception và dữ liệu trả về. Endpoint lưu thật phải có quyền, không dùng ví dụ preview làm production.

Tham khảo: [FastAPI tutorial](https://fastapi.tiangolo.com/tutorial/),
[Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/),
[Pydantic validators](https://docs.pydantic.dev/latest/concepts/validators/).
