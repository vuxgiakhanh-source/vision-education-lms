# Xây từ thư mục trống: lớp học → giao, nộp và chấm bài

> Bản xây lại: đây là bài tổng hợp **sau [G1](G1-trang-web-tu-thu-muc-trong.md) đến [G4](G4-thiet-ke-tinh-nang-xuyen-he-thong.md)**. Nếu chưa tự tạo frontend hoặc chưa hiểu cách tách module, học các bài G trước; chúng dẫn từng file, lệnh, kết quả và lỗi. Xưởng này giảm hướng dẫn để kiểm khả năng làm lại.

Mục tiêu: bạn tự viết từng checkpoint; sau khi chạy được mới mở source tham
chiếu. Lát cắt tham chiếu hiện thực tạo/list/detail/đổi tên lớp có JWT, quyền,
schema, service, repository, SQLAlchemy và UI React. Giao/nộp/chấm là phần bạn
tự phát triển tiếp theo hợp đồng chi tiết chương10; sau khi tự viết, mở thêm
[P0](23-san-pham-hoan-chinh.md) để đối chiếu core loop API/React/DB đã bổ sung.
Không gọi một lát cắt lớp học là toàn bộ LMS đã hoàn thành.

## 0. Chọn nơi thực hành và hợp đồng

Tạo repo học riêng, không ghi đè auth/dashboard sản phẩm. Ghi README gồm mục
tiêu, stack, lệnh chạy, biến môi trường theo tên và các kiểm tra. Dùng Git lưu
checkpoint nhỏ. Giữ UI đơn giản để tập trung đường dữ liệu trước.

Quy tắc bản lớp học: cô tạo lớp của mình; học sinh chỉ đọc lớp có membership;
cô chỉ đổi tên lớp mình. Lớp ngoài phạm vi trả 404 theo policy bài học. Chỉ có
teacher/student trong fixture, chưa có mọi capability admin/trợ giảng. Tạo lớp
không tự thêm học sinh; membership ban đầu do fixture tạo để kiểm quyền.

| API | Input | Output đúng | Lỗi phải kiểm |
|---|---|---|---|
| GET /classes | page>=1,page_size1..100 | array lớp nhìn thấy | 401/403/422 |
| POST /classes | title trim1..200 | 201 lớp mới | 401/403/422 |
| GET /classes/{id} | id>0 | lớp đúng phạm vi | 401/403/404/422 |
| PATCH /classes/{id} | id,title | lớp đã đổi | 401/403/404/422 |

## 1. Viết yêu cầu và fixture trước code

Vẽ users(1 cô,2 An,3 Bình,4 bị khóa), classes(1 do cô 1), memberships(lớp 1,
An 2). Kết quả tính tay: cô 1 list một lớp,An 2 một lớp,Bình 3 rỗng,khóa 4 bị 403.
Nếu bạn không dự đoán được, chưa cần viết SQL hay React.

Ghi entity khác DTO: model Class có teacher_id lấy từ current user, không nhận
teacher_id trong body người dùng. ClassInput chỉ title; ClassOutput chỉ các
field được phép. Nhận teacher_id client gửi sẽ mở khả năng gán chủ tùy ý.

## 2. Tạo project backend và endpoint không DB

Trong thư mục mới, tạo venv và requirements có FastAPI,Uvicorn,SQLAlchemy,
PyMySQL,Pydantic,python-jose theo môi trường đã chốt. Cài ở repo học, không
thêm ngẫu nhiên vào sản phẩm. File main đầu tiên:

```python
from fastapi import FastAPI
app = FastAPI()

@app.get('/health')
def health():
    return {'status': 'ok'}
```

Chạy Uvicorn ở cổng 8001 để không trùng backend sản phẩm. Mở /docs và /health.
Hiểu module:object; khi lỗi import, kiểm CWD/package/interpreter trước endpoint.
Checkpoint: bạn chỉ được đánh dấu khi tự khởi chạy và giải thích HTTP200/body.

## 3. Tạo frontend tĩnh

Tạo project Vite React TypeScript trong repo học (dùng scaffold chính thức hoặc
tự viết index/main/package/config). Đọc scripts trước khi chạy. Dựng trang
hiển thị3 lớp fixture, có label/input tìm, list key=id và empty state.

Chưa cần token/API. Tự chỉ ra JSX nào render từ props và query nào thuộc state.
Checkpoint: tìm kiếm có hoa/thường, query rỗng và title dài không vỡ layout.
Sau đó thay fixture bằng API ở bước7, không để song song hai nguồn dữ liệu.

## 4. Tạo schema và service trong bộ nhớ

Viết ClassInput trim title trước kiểm length, forbid extra. Thử title rỗng,
khoảng trắng, null, thiếu title, dài 201, teacher_id lạ. Service thuần xác định
teacher mới tạo được. Repository giả giúp thử quy tắc trước DB.

Tại sao schema và service đều kiểm title trong reference? API boundary kiểm
representation; service có thể được gọi ngoài HTTP nên giữ invariant tối thiểu.
Không copy mọi rule vào mọi lớp; xác định một nơi sở hữu và test hợp đồng.

## 5. Từ ERD sang SQLAlchemy

Tạo users,classes,memberships với PK/FK/UNIQUE. Giải thích từng cột,nullable,
index và khóa ghép. Reference dùng Column/declarative_base gần phong cách
repo, select để query; không buộc viết lại auth hiện có theo mapped_column.

Trong lab đầu, dùng SQLite file để thấy reload vẫn còn dữ liệu mà chưa cần
dựng DB service. Đây là công cụ học tạm; hệ thống chính dùng MySQL. Khóa ngoại
SQLite được bật rõ. Không giả định kết quả SQLite thay cho MySQL/concurrency.

Checkpoint: tự tạo session mới và đọc bản ghi vừa commit; không chỉ nhìn object
vẫn nằm trong RAM. Cố ý vi phạm FK/UNIQUE ở DB học rồi rollback đúng.

## 6. Ghép repository → service → router

Đọc trách nhiệm từ [repository.py](workshop/lms_lab/repository.py),
[service.py](workshop/lms_lab/service.py) và [app.py](workshop/lms_lab/app.py)
chỉ sau khi tự viết. Luồng tạo lớp:

```text
POST JSON → ClassInput → current_user → ClassService.create
 → kiểm teacher → Classroom(title,teacher_id từ actor)
 → repository.add → flush → service gọi transaction.commit
 → ClassOutput → 201 JSON
```

Repository giữ db để thao tác, service quyết định commit qua Transaction adapter
cho cả nghiệp vụ. Composition root lắp cả hai bằng cùng Session; xem bài P1.
Try/except ở transaction rollback rồi ném lại, không đổi mọi lỗi DB thành400.
Khi nghiệp vụ có thêm membership/audit, thêm trong cùng transaction nếu cần
atomic; không để repository đầu commit trước bước sau.

Điều tra từng dòng: ai tạo engine? Ai tạo Session? Depends dùng chung get_db
trong một request thế nào? Ai đóng Session? Response còn đọc được field khi
nào? Reference chọn expire_on_commit=False để DTO đọc được field sau commit;
đó là lựa chọn lifecycle phải hiểu, không phải chữa mọi lazy-loading.

## 7. JWT fixture và quyền thật ở server

Reference bỏ qua màn login trong xưởng đầu, dùng token cho user giả để cô lập
bài quyền. Tự đọc lại login thực tế ở bài mẫu để nối bcrypt và credential flow
khi phát triển tiếp. Token fixture không phải người dùng tự khai id để có quyền.
Server xác minh signature/expiry/sub, lấy user hiện tại từ DB, xét active/role.

Subject là string id, không lấy teacher_id trong JSON body. Quyền list được
đưa vào query; quyền detail kiểm quan hệ actor-resource. Không chỉ chặn nút UI.
Token user 3 không thể GET lớp 1 dù biết id; user 2 không thể PATCH dù được đọc.

Checkpoint: đúng/sai signature, hết hạn, thiếu exp,không user,khóa user,
đúng lớp/ngoài lớp,đọc được nhưng không sửa được. Không log JWT.

## 8. Nối React, Axios, Zod và RHF

Mở [class-api.ts](workshop/frontend/class-api.ts): listClasses gửi GET với
Authorization/signal, parse response bằng Zod. createClass POST title rồi
parse lớp trả về. Mỗi hàm trả dữ liệu domain, không buộc component biết mọi
chi tiết AxiosResponse. App sản phẩm tiếp tục tái dùng client ở lib/axios.

Mở [ClassroomPractice.tsx](workshop/frontend/ClassroomPractice.tsx): effect tải
list theo token/reload, cleanup chặn response cũ; query là state, visible là
dữ liệu tính được. Form RHF giữ field/errors/isSubmitting; resolver dùng Zod.
Submit thành công mới reset input và yêu cầu list mới. Lỗi giữ input để sửa.

```text
Gõ title → RHF giữ giá trị
Submit → Zod trim/check → submit(values)
→ createClass(token,title) → server validate/quyền/commit
→ parse response → reset form → tăng reload
→ effect tải list → UI render success
```

Không tự append object dùng id ngẫu nhiên rồi coi đã lưu. Mất mạng sau commit
có thể khiến client không biết kết quả; retry create cần idempotency contract
nếu muốn bảo đảm một tác dụng. Reference lớp học chưa có idempotency create,
nên người học phải ghi giới hạn và bổ sung khi yêu cầu cần.

Đọc [main.tsx](workshop/frontend/main.tsx): đổi token remount vùng dữ liệu bằng
key, giữ token mẫu trong RAM. Đây là UI học request, chưa có quản lý phiên,
refresh token hay recovery production. Không nhầm nút “Áp dụng tài khoản” với login.

## 9. Chạy bản tham chiếu và tự quan sát

Lệnh chi tiết ở [README xưởng](workshop/README.md). Tạo secret ngẫu nhiên cho
lab, init SQLite, tạo token fixture, chạy API 8001 và frontend 5173. Không dùng
.env/DB/token của sản phẩm. CLI không reset DB có dữ liệu.

Trong DevTools, tự xem URL/method/header/body/status/response. Không chụp token.
Thử token 1 tạo lớp,refresh vẫn có;token 2 thấy đúng lớp seeded;token 3 không thấy;
token 2 tạo lớp nhận 403 và không sinh hàng mới. Chuyển token không giữ list cũ.

## 10. Kiểm tra trước khi gọi là xong lát cắt

Chạy [test_workshop.py](workshop/test_workshop.py). Tests gọi ASGI trực tiếp
và SQLite tạm để kiểm route/schema/JWT/quyền/lưu dữ liệu. Không dùng TestClient
vì môi trường hiện chưa có httpx; học TestClient/pytest sau khi khai báo dependency.
Đây không phải test browser hoặc MySQL thật.

Bạn phải viết thêm: cô khác lớp,FK/UNIQUE,rollback sau lỗi,phân trang nhiều
bản ghi,CORS từ origin được phép/không phép,UI error/retry, refresh deep link.
Ghi kiểm tra nào đã chạy và kiểm tra nào mới là kế hoạch.

Hợp đồng độ dài title trong xưởng là Unicode code point sau trim, không phải
số ký tự nhìn thấy trên màn hình. Python len và phép đếm `[...value].length`
ở frontend phù hợp cho hợp đồng này; JS string.length/Zod max mặc định dùng
UTF-16 code unit có thể đếm khác với emoji. Test200/201codepoint và khoảng
trắng. Nếu cần giới hạn grapheme cluster, đó là hợp đồng khác phải triển khai
nhất quán ở các phía.

## Tra toàn bộ source tham chiếu theo thứ tự tự viết

Chỉ mở file của checkpoint đang học. Mỗi file đều được nhúng trong sách HTML
để tra offline; khi chạy cần lưu các file vào đúng cây thư mục của repo học.

| File | Vai trò và câu hỏi cần tự trả lời |
|---|---|
| [models.py](workshop/lms_lab/models.py) | Bảng/Column/FK/UNIQUE: invariant nào giữ ở DB? |
| [database.py](workshop/lms_lab/database.py) | Engine/factory/Session: vì sao không chia một Session global? |
| [schemas.py](workshop/lms_lab/schemas.py) | Normalize/validate/output: field nào không nhận từ client? |
| [repository.py](workshop/lms_lab/repository.py) | Query có scope,flush: vì sao không commit riêng? |
| [service.py](workshop/lms_lab/service.py) | Rule/transaction: exception nào giữ dữ liệu không đổi? |
| [app.py](workshop/lms_lab/app.py) | Factory/dependency/route/JWT: ai lắp các object? |
| [main.py](workshop/lms_lab/main.py) | Đọc cấu hình và tạo app cho Uvicorn: lúc import xảy ra gì? |
| [CLI fixture](workshop/lms_lab/__main__.py) | Init/token giả: vì sao không tự seed DB sản phẩm? |
| [requirements](workshop/requirements.txt) | Dependency trực tiếp quan sát được; phần nào chưa là lock? |
| [test_workshop.py](workshop/test_workshop.py) | Fixture tạm,ASGI và assert DB: chứng minh được gì? |
| [package.json](workshop/frontend/package.json) | Scripts/runtime/dev dependencies: npm chạy ở đâu? |
| [tsconfig](workshop/frontend/tsconfig.json) | Compiler kiểm kiểu thế nào; không sửa JSON runtime |
| [vite.config](workshop/frontend/vite.config.ts) | Plugin React nối vào Vite ở đâu? |
| [index.html](workshop/frontend/index.html) | Root và module entry của browser |
| [main.tsx](workshop/frontend/main.tsx) | Entry,fixture token trong RAM,remount khi đổi phiên |
| [class-api.ts](workshop/frontend/class-api.ts) | HTTP,headers,response parser và lỗi |
| [ClassroomPractice.tsx](workshop/frontend/ClassroomPractice.tsx) | Effect/form/list/state/cleanup và RHF/Zod |
| [style.css](workshop/frontend/style.css) | Box model,flow,focus,wrap và kích thước |
| [CSS declaration](workshop/frontend/assets.d.ts) | Khai báo module CSS cho compiler,không chạy CSS bằng TS |

## 11. Chuyển sang MySQL và Alembic bằng thao tác có thể giải thích

Trong DB học riêng, tạo database và account quyền phù hợp. Dùng URL MySQL từ
cấu hình lab, không dùng DB sản phẩm. URL chứa password phải được tạo/encode
đúng và không in ra log. Không ghi credential vào file reference.

Khởi tạo Alembic trong repo học; env.py đọc URL an toàn và import Base.metadata.
Tạo revision cho ba bảng, đọc upgrade/downgrade. Chạy upgrade ở DB rỗng, so
schema,seedfixture được review rồi test read/create/rename bằng request thật.
CLI initreference cố ý chỉ hỗ trợ SQLite để tránh tự tạo bảng vào MySQL.

Thử UNIQUE membership,FK,rollback,collation tên lớp,index teacher_id và EXPLAIN
query. Thử hai request song song cho bài nộp ở bước tiếp. Không nói đã kiểm
MySQL chỉ vì đổi connection string mà chưa chạy.

## 12. Tự mở rộng giao → nộp → chấm

| Checkpoint | Bạn tự viết | Điều kiện hoàn thành |
|---|---|---|
| A | Membership API theo quyền | Cô khác lớp không thêm người; trùng có policy |
| B | Assignment nháp/công bố | Đúng lớp nhìn thấy sau công bố/reload |
| C | Submission | Deadline/content/member/retry/UNIQUE đồng thời |
| D | Grade và công bố | Điểm0 hợp lệ; chưa công bố không lộ response |
| E | Dashboard thật | Chỉ số lấy cùng dữ liệu, đúng mẫu số/phạm vi |
| F | Tài liệu/lịch/điểm danh | Quyền theo lớp, dữ liệu bền và lỗi nhất quán |
| G | Staging và phục hồi | Người khác chạy được và restore được DB học |

Dùng [chương10](10-lat-cat-hoan-chinh.md) làm hợp đồng A–E, chương11 cho lượt
thi/điểm, chương14 cho F và chương bàn giao cho G. Với mỗi checkpoint viết
đặc tả,ERD,API,test trước implementation; sau đó tự bảo vệ thiết kế.

## 13. Bài thay đổi yêu cầu để chứng minh hiểu

Thêm “lưu trữ lớp”: học sinh đọc lịch sử nhưng không nộp bài mới; cô không tạo
bài mới trong lớp lưu trữ. Không xóa lớp/membership/bài nộp. Tự chọn field,
state transition,endpoint,query filter,UI,tests và migration. Đừng chỉ thêm một
boolean vào component; mọi đường ghi liên quan phải xét invariant server.

Nếu tự xử lý được thay đổi này, sau đó chuyển sang đề thư viện và giải bài
mới. Nếu còn phải hỏi chính xác đặt từng dòng ở đâu, quay lại checkpoint nhỏ
đó và làm thêm biến thể trước khi mở module khác.
