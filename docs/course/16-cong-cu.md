# Công cụ thật trong repo: dùng gì, vì sao và quan sát thế nào?

Đối chiếu `frontend/package.json`, `backend/requirements.txt`, config và source
ngày soạn. Không đọc/nhúng nội dung `.env` thật. Một dependency có trong manifest
chưa chứng minh người học đã dùng thành thạo hoặc cả sản phẩm đã tích hợp xong.

## 1. Bốn loại công cụ, bốn công việc

| Công cụ | Làm gì trong repo | Bạn phải hiểu |
|---|---|---|
| Node + npm | Chạy Vite, cài dependency, build frontend | Process, script, manifest, lockfile |
| TypeScript | Kiểm kiểu và mô tả hợp đồng code | Kiểu bị xóa khi chạy; JSON cần validation |
| Vite | Dev server và build tài nguyên | Dev khác production; cổng không phải API |
| React + React DOM | Mô tả/render UI | Component, state, event, effect |
| Tailwind + plugin Vite | Sinh utility CSS | CSS gốc, cascade, breakpoint, box model |
| React Router | Ánh xạ URL sang UI | Điều hướng, nested route, guard trải nghiệm |
| Axios | Gửi HTTP và interceptor | Promise, headers, body, error.response |
| RHF + resolver + Zod | Form và validation frontend | register/submit/errors; parse runtime |
| Lucide React | Icon dạng component | Kích thước, accessible name, không dùng icon thay nhãn |
| ESLint + plugin hooks | Phát hiện một số mẫu code có vấn đề | Lint không chứng minh nghiệp vụ đúng |
| Python + venv + pip | Interpreter và dependency backend | Đúng interpreter, import, môi trường độc lập |
| FastAPI + Uvicorn | Ứng dụng ASGI và server chạy nó | Route, schema, dependency, request lifecycle |
| Pydantic | Schema FastAPI sử dụng | Parse/normalize/validate, response field |
| SQLAlchemy + PyMySQL | ORM/Session và driver MySQL | SQL vẫn tồn tại; transaction/constraints |
| MySQL + Docker Compose | Database và container dev hiện tại | Port, volume, service readiness |
| Alembic | Theo dõi thay đổi schema | Revision, upgrade, review migration |
| bcrypt | Hash/verify mật khẩu | Hash không phải mã hóa giải ngược |
| python-jose | Ký/xác minh JWT | Signature, expiry, algorithm, quyền riêng |
| python-dotenv | Nạp cấu hình từ môi trường | Secret backend khác biến frontend công khai |
| Loguru | Ghi log Python | Ngữ cảnh, mức log, không log secret |
| Git | Lưu lịch sử có thể review | Working tree, staging, commit, branch, diff |
| DevTools | Quan sát trình duyệt | Elements, Computed, Console, Network, Storage |

Pydantic đi cùng FastAPI trong môi trường đã kiểm tra; requirements hiện không
pin đủ dependency. Khi làm môi trường độc lập, cần khai báo/khóa có chủ đích
những gói mình import trực tiếp. Không chép nguyên `pip freeze` chứa công cụ
không liên quan vào runtime mà không review.

## 2. PowerShell: đọc đường dẫn trước khi đọc lỗi

Mở terminal tại `D:\vision-education-lms`. Những lệnh sau chỉ quan sát:

```powershell
Get-Location
Get-ChildItem
Get-Command node, npm, python, git
node --version
npm --version
python --version
git status --short
```

`Get-Location` cho thư mục hiện tại. Đường dẫn tương đối được tính từ đó.
`frontend/src` ở gốc repo khác `frontend/src` khi bạn đã cd vào frontend.
`Get-Command` giúp biết Python/npm nào đang được gọi nếu máy có nhiều bản.

```powershell
Set-Location D:\vision-education-lms\frontend
npm run
npm run dev -- --host 127.0.0.1 --port 5175
```

`npm run` đọc scripts từ package.json ở thư mục phù hợp. `--` chuyển phần sau
cho script Vite. Terminal bị chiếm vì process dev server đang chạy là bình thường.
Ctrl+C dừng process đó; nó không xóa source. Dùng terminal khác cho backend.

Root repo cũng có package.json khác frontend. Trước cài/chạy, tự trả lời mình
đang thao tác manifest nào. Không chạy thêm npm install ở gốc chỉ vì một lệnh
trong frontend thiếu dependency. Đọc import và manifest liên quan trước.

## 3. Dependency, lockfile, devDependency

`package.json` mô tả gói/scripts/khoảng phiên bản. Lockfile giữ đồ thị phiên bản
đã resolve. `node_modules` là kết quả cài; không phải source cần commit.
`npm ci` dùng lockfile tương thích và dựng lại dependency. Nó có thể truy cập
mạng và thay node_modules; dùng khi chuẩn bị môi trường, không cần chạy mỗi lần sửa chữ.

Dependency frontend được Vite xử lý khi build, không phải gói nào cũng chạy
trên server production. `devDependency` chỉ cách phân loại mục đích trong
manifest, không tự bảo đảm dependency đó không lọt vào bundle nếu bạn import.

```powershell
npm run build
npm run lint
npm ls --depth=0
```

Build hiện chạy TypeScript rồi Vite. Lint hiện dùng ESLint và plugin hooks.
Khi lỗi chỉ rõ file/dòng, mở đúng vị trí và hiểu thông báo. Không thêm `any`,
`@ts-ignore` hoặc tắt rule toàn dự án để làm log xanh khi chưa hiểu nguyên nhân.

## 4. Venv: Python nào thì pip đó

Tại gốc repo:

```powershell
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m pip --version
.\.venv\Scripts\python.exe -m pip list
```

`-m pip` bảo Python đang chọn chạy module pip của môi trường đó. Không cần kích
hoạt venv để dùng đường dẫn interpreter rõ ràng. Nếu chưa có venv, tạo trong
dự án thực hành riêng bằng `python -m venv .venv`, rồi cài requirements đã review.

Backend repo import `app...`, nên chạy từ thư mục backend theo hướng dẫn repo:

```powershell
Set-Location D:\vision-education-lms\backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

`app.main` là module; phần sau `:` là tên object FastAPI. `--reload` phục vụ dev,
không phải cấu hình production. Lỗi import và lỗi thiếu biến môi trường cần
xử lý trước khi kết luận endpoint sai. Không in giá trị secret để debug.

## 5. DevTools: một request cần đọc những gì?

Mở trang → F12 → Network → lọc Fetch/XHR → thực hiện hành động → chọn request.
Không đăng token/password lên báo cáo hoặc ảnh chụp.

| Chỗ xem | Câu hỏi |
|---|---|
| URL/method | Gửi đúng server và đúng endpoint chưa? |
| Request Headers | Content-Type/Authorization theo hợp đồng chưa? |
| Payload | Tên trường và kiểu thực tế là gì? |
| Status | Thành công, validation, quyền, không tồn tại hay lỗi server? |
| Response | Body thực tế khác type khai báo ở đâu? |
| Timing | Đang chờ kết nối, server hay tải tài nguyên? |
| Initiator | Đoạn frontend nào khởi tạo lời gọi? |

Không có request: kiểm event/validation/JS error. Có 422: đối chiếu body/schema.
Có 401/403: kiểm danh tính/quyền, không sửa CSS. Có CORS error: kiểm Console,
preflight và backend origin; không tắt bảo vệ trình duyệt để coi là sửa xong.

Elements/Computed cho kích thước box và CSS thực sự thắng. Thử bỏ một rule ở
DevTools chỉ là thí nghiệm tạm; muốn lưu phải sửa source. Storage có thể chứa
token của repo: chỉ quan sát trên máy, không đưa vào ghi chú của sách.

## 6. Docker Compose hiện chạy cái gì?

Repo hiện có service MySQL 8.0, map 3306:3306 và named volume. File đó chưa chạy
React/FastAPI. Container đang chạy chưa chắc MySQL đã sẵn sàng nhận kết nối.

```powershell
Set-Location D:\vision-education-lms\backend
docker compose ps
docker compose logs --tail 50 mysql
```

Lệnh log có thể chứa thông tin môi trường; xem cục bộ, lọc dữ liệu nhạy cảm
trước khi chia sẻ. Không dùng `docker compose down -v` như mẹo sửa lỗi: `-v`
xóa volume của project. Chương vận hành dạy backup/restore trên DB thực hành.

## 7. Alembic và công cụ SQL

```powershell
..\.venv\Scripts\python.exe -m alembic current
..\.venv\Scripts\python.exe -m alembic history
```

Các lệnh đọc trạng thái vẫn cần cấu hình DB đúng. `revision --autogenerate`
tạo đề xuất migration; cần đọc diff, hiểu rename/drop/default và thử trên DB
học trước `upgrade`. Không chạy migration tùy tiện vào dữ liệu lớp thật.

Bạn có thể học SQL bằng client MySQL CLI hoặc công cụ GUI bạn chọn. Repo không
chứng minh máy có DBeaver/Workbench/Postman, nên giáo án không giả định đã cài.
FastAPI `/docs` và Network đủ để bắt đầu đọc hợp đồng/request. Học client HTTP
khác khi cần lưu collection hoặc tự động hóa; nguyên lý HTTP vẫn giữ nguyên.

## 8. Git: một thay đổi đi qua ba nơi

```text
Source đang sửa → git add có chọn file → staging → git commit → lịch sử local
                                                        → git push → remote
```

```powershell
git status --short
git diff -- frontend/src/App.tsx
git diff --staged
git log -5 --oneline
```

Commit không tự push. Nhánh không phải bản backup cho file chưa commit.
Không dùng reset/clean để “về như cũ” nếu chưa biết sẽ mất gì. Trong repo học
riêng, thử một conflict nhỏ, đọc cả hai phía, sửa nội dung và chạy lại kiểm tra.

## 9. Thực hành có đầu ra

1. Vẽ Node/Vite, trình duyệt, Uvicorn và MySQL thành bốn process; ghi cổng.
2. Tự tạo lỗi import sai trong repo học, đọc lỗi, sửa và giải thích đường dẫn.
3. Dùng Network kể lại request tạo lớp mà không tiết lộ token.
4. Tìm script build/lint thật và giải thích từng phần.
5. Viết một commit nhỏ trong repo học; chỉ rõ phần còn chưa commit.
6. Phân biệt env của shell, dotenv backend và `import.meta.env` của Vite.

Qua bài khi bạn biết mở đúng công cụ để kiểm một giả thuyết, không chạy lệnh
ngẫu nhiên. Tài liệu đối chiếu: [Vite](https://vite.dev/guide/),
[npm ci](https://docs.npmjs.com/cli/commands/npm-ci),
[venv](https://docs.python.org/3/library/venv.html),
[Docker Compose](https://docs.docker.com/compose/), [Git](https://git-scm.com/docs).
