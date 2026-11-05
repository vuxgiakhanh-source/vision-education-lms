# Tra ký hiệu, chọn đúng bài luyện và ghi bằng chứng

## 1. Từ điển ký hiệu cần đọc thành lời

| Ký hiệu | JS/TS/JSX | Python |
|---|---|---|
| `=` | Gán; default param theo ngữ cảnh | Gán; default param |
| `===` / `==` | === nghiêm ngặt; == có coercion | == so giá trị; không có === |
| `()` | Gọi hàm, nhóm biểu thức, danh sách tham số | Gọi hàm, nhóm, tuple theo dấu phẩy |
| `{}` | Object/block/biểu thức JSX tùy vị trí | Dict; set khi có phần tử phù hợp |
| `[]` | Array, index/key động, type array T[] | List, index/slice, generic annotation |
| `.` | Đọc thuộc tính/method | Đọc thuộc tính/method |
| `:` | Field object,annotation TS,nhánh ba ngôi | Mở khối; dict key:value; annotation |
| `=>` | Arrow function | Không dùng; lambda dùng cú pháp riêng |
| `->` | Không dùng cho hàm JS | Annotation kiểu return |
| `...` | Rest/spread tùy vị trí, copy nông | Ellipsis; không phải spread kiểu JS |
| `**` | Lũy thừa JS | Lũy thừa/unpack dict/kwargs tùy vị trí |
| `?` / `?.` / `??` | Optional type/ternary; truy cập nullish; fallback nullish | Không dùng các cú pháp này |
| `!` | Đảo truthiness; TS assertion theo vị trí | Dùng not; != là khác |
| <code>&#124;</code> | Union type hoặc bitwise tùy ngữ cảnh | Union annotation hoặc bitwise |
| `&&` / <code>&#124;&#124;</code> | Short-circuit | and/or |
| `#` | Không phải comment JS; có private field theo ngữ cảnh | Comment |
| `@` | Decorator theo công cụ/phiên bản phù hợp | Decorator; khác email string |
| `${...}` | Nội suy trong template literal | Dùng f-string `{...}` |

Không học ký hiệu tách ngữ cảnh. Cùng `{}` ở arrow body và object literal có
hành vi khác. Khi không hiểu một dòng, chia thành biểu thức nhỏ và chạy với
dữ liệu giả có thể tính tay. Thụt lề phải phản ánh đúng cấu trúc, không che return sai vị trí.

## 2. Chọn công cụ khi gặp lỗi

| Lỗi/triệu chứng | Bắt đầu từ | Kiến thức quay lại |
|---|---|---|
| Cannot find module | Terminal,import,CWD,interpreter | Công cụ/module |
| undefined property | Console,giá trị vào và schema | JS/type/unknown |
| Render lặp | Component/effect/dependency | State và side effect |
| Network không có request | Handler,form validation,Console | Event và callback |
| HTTP422 | Requestbody/schema | Validationboundary |
| HTTP401/403/404 | Token/current user/scope | Auth và quan hệ dữ liệu |
| Data không lưu | Transaction,commit,DB đích | ORM/lifecycle |
| SQL count sai | Fixture nhỏ,JOIN/NULL | SQL và định nghĩa chỉ số |
| Card tràn | Computed/Grid/min-width/content | CSS box/layout |
| Chạy local,host lỗi | Env/build/origin/proxy/deep route | Phát hành |

## 3. Bài luyện nền tảng theo thang khó

| Mã | Có hướng dẫn | Đề trắng | Biến thể sau khi tự làm |
|---|---|---|---|
| JS | Vết đếm task qua for | Search/update/report | Thêm unknownstatus/điểm 0 |
| TS | Type và parser một record | Response phân trang | Optional/null/schema thay đổi |
| UI | Form có label/error | Dashboard hai cột | Nội dung rất dài và zoom |
| React | Filter local | List/create từ API | Request trả ngược và đổi phiên |
| Python | Hàm + unittest | Service + fake | Rule mới, giữ hợp đồng cũ |
| SQL | SELECT fixture | JOIN/aggregate/report | Một quan hệ nhiều hàng gây nhân |
| API | Preview schema | CRUD có scope | PATCH/validation/error contract |
| ORM | Model + Session | Nghiệp vụ nhiều bước | Constraintfail ở bước 2 |
| Auth | Current user | Quyền theo tài nguyên | Thu hồi quyền giữa phiên |
| Ops | Build và chạy | Staging có config/log | Lỗi release và restore |

Mỗi bài cần đầu vào,đầu ra,quy tắc,ít nhất một trường hợp rỗng/biên và một
trường hợp từ chối khi liên quan. Test dựa trên hành vi, không sao chép if của
implementation. Giữ một phiên bản sai để tự kiểm test có bắt được hay không.

## 4. Phiếu thiết kế một chức năng bất kỳ

```text
Tên hành động và người dùng:
Vấn đề cần giải quyết:
Điều kiện trước / trạng thái sau:
Input / output / lỗi:
Actor-action-resource và phạm vi:
Bảng / field / PK-FK-UNIQUE-index:
Endpoint / method / status / schema:
Service giữ rule gì? Repository giữ việc gì?
Transaction bắt đầu/kết thúc ở đâu?
UI state / lỗi / loading / refresh:
Retry / concurrency / thời gian:
Tests đúng-sai-biên và dữ liệu sau lỗi:
Log / file ngoài DB / vận hành:
Giới hạn bản đầu:
```

Không phải chức năng nào cũng cần mọi cơ chế. Ghi “không áp dụng vì…” với lý
do cụ thể thay vì thêm abstraction vô mục đích. Ví dụ nút đổi theme không cần
transaction DB nếu chỉ lưu preference cục bộ, nhưng cần kiểm storage/theme UI.

## 5. Học cách tra tài liệu

Xác định thư viện/phiên bản từ manifest/môi trường → tìm API trong tài liệu
chính thức → đọc input/output/lifecycle/error → chạy ví dụ nhỏ trong repo học
→ áp dụng vào hợp đồng → viết test. Nếu tutorial khác phiên bản, so release
note/API hiện có, không copy config cũ rồi cài thêm package để ép chạy.

Nguồn theo nhóm: [JavaScript](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide),
[TypeScript](https://www.typescriptlang.org/docs/handbook/intro.html),
[React](https://react.dev/learn), [React Router](https://reactrouter.com/start/declarative/installation),
[Tailwind](https://tailwindcss.com/docs), [Axios](https://axios-http.com/docs/intro),
[RHF](https://react-hook-form.com/get-started), [Zod](https://zod.dev/basics),
[Python](https://docs.python.org/3/tutorial/), [FastAPI](https://fastapi.tiangolo.com/tutorial/),
[SQLAlchemy](https://docs.sqlalchemy.org/en/20/orm/quickstart.html),
[Alembic](https://alembic.sqlalchemy.org/en/latest/tutorial.html),
[MySQL](https://dev.mysql.com/doc/refman/8.0/en/),
[Uvicorn](https://www.uvicorn.org/settings/), [Loguru](https://loguru.readthedocs.io/en/stable/).

## 6. Chu trình một buổi học và ôn

Mở lỗi/bài cũ, tự dự đoán và viết lại một đoạn; học một ý mới; làm một bài
không nhìn lời giải; test và giải thích; ghi một bước tiếp. Buổi sau đổi dữ
liệu hoặc rule để tránh nhớ hình dạng đáp án. Không dùng thời lượng đọc hoặc
số checkbox xanh làm bằng chứng duy nhất về năng lực.

Khi nhờ AI: gửi đề,giả thuyết,đoạn bạn đã viết và lỗi đã làm sạch secret;
xin gợi ý theo mức. Sau review, tự sửa và viết một biến thể. Trong bài đánh
giá cuối, giữ lịch sử phần hỗ trợ để nói đúng phần mình tự làm.
