# Vision Education LMS

Vision Education LMS là ứng dụng quản lý học tập cho trung tâm Toán khối 10–12. Học sinh có thể xem lịch theo khối trước khi được xếp lớp. Dự án đang phát triển luồng xem lịch tuần, nhận diện ca đã đăng ký và đổi ca học.

## Tình trạng dự án

| Tính năng | Hiện trạng |
| --- | --- |
| Tài khoản | Đăng nhập bằng số điện thoại, đổi mật khẩu và lấy hồ sơ qua API. |
| Trang chủ học sinh | Lấy tên từ hồ sơ. Điểm số, bài tập, tài liệu và lịch mini dùng dữ liệu mẫu. |
| Lịch học | Có giao diện lưới tuần và bản xem trước với dữ liệu mẫu. API lịch tuần, đổi ca và điểm danh đang nằm trong phạm vi phát triển. |

## Công nghệ

| Thành phần | Công nghệ |
| --- | --- |
| Giao diện | Next.js App Router, React, TypeScript, Tailwind CSS và Axios |
| API | Python, FastAPI, Uvicorn và Pydantic |
| Dữ liệu | MySQL 8, SQLAlchemy và Alembic |
| Xác thực | JWT Bearer và bcrypt |
| Môi trường cục bộ | Docker Compose cho MySQL |

## Xem giao diện

Các lệnh bên dưới dùng PowerShell trên Windows. Để chạy frontend, dùng Node.js 24 và npm. Từ thư mục gốc của repo:

```powershell
npm --prefix frontend ci
npm --prefix frontend run dev
```

| Đường dẫn | Nội dung |
| --- | --- |
| [Xem trước Lịch học](http://localhost:5173/schedule-preview) | Xem lịch mẫu và chuyển giữa các phương án giao diện khi chỉ chạy frontend. |
| [Kiểm tra responsive](http://localhost:5173/dashboard-preview/index.html) | Xem bố cục dashboard ở nhiều kích thước màn hình. |
| [Đăng nhập](http://localhost:5173/login) | Điểm vào luồng đăng nhập khi API và MySQL đang chạy. |

## Chạy API và đăng nhập

Cần Python 3.12 và Docker Compose. Mở terminal thứ hai ở thư mục gốc:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements-dev.txt -c backend\constraints.txt

if (-not (Test-Path backend\.env)) { Copy-Item backend\.env.example backend\.env }
if (-not (Test-Path frontend\.env)) { Copy-Item frontend\.env.example frontend\.env }
```

- Trong `backend/.env`, điền các giá trị `MYSQL_*` và `SECRET_KEY` (tối thiểu 32 ký tự, ngắn hơn thì ứng dụng không khởi động). Các biến tùy chọn như `DB_POOL_SIZE`, `ENVIRONMENT`, `LOG_DIR` có giải thích trong `backend/.env.example`. Cấu hình `ALLOWED_ORIGINS=http://localhost:5173` để khớp với địa chỉ frontend ở trên.
- Trong `frontend/.env`, đặt `NEXT_PUBLIC_API_URL=http://127.0.0.1:8000`. Đổi tên biến nếu đang dùng `VITE_API_URL` từ phiên bản cũ, rồi khởi động lại frontend.

Với cơ sở dữ liệu phát triển mới, chạy các lệnh sau trong terminal backend:

```powershell
Set-Location backend
docker compose up -d mysql

# Sau khi MySQL sẵn sàng, áp dụng toàn bộ migration và tạo tài khoản thử.
..\.venv\Scripts\python.exe -m alembic upgrade head
..\.venv\Scripts\python.exe -m scripts.seed_users
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Dùng số điện thoại và mật khẩu khởi tạo in trên terminal để đăng nhập lần đầu. [Script seed](backend/scripts/seed_users.py) tạo tài khoản thử và hồ sơ học sinh khối 12, đồng thời yêu cầu đổi mật khẩu ở lần đăng nhập đầu tiên. Mật khẩu khởi tạo được sinh ngẫu nhiên và chỉ in khi tạo tài khoản. Chạy lại seed vẫn giữ mật khẩu của tài khoản đã có.

Nếu MySQL có tài khoản trùng số điện thoại, migration sẽ dừng. Xử lý từng trường hợp trùng trước khi chạy lại `alembic upgrade head`.

### API hiện có

Tài liệu tương tác nằm tại [Swagger UI](http://127.0.0.1:8000/docs). Khi đặt `ENVIRONMENT=production`, `/docs`, `/redoc` và `/openapi.json` bị tắt.

| Endpoint | Chức năng |
| --- | --- |
| `POST /login` | Xác thực số điện thoại và mật khẩu, cấp JWT. |
| `GET /me` | Lấy hồ sơ từ JWT Bearer. |
| `PUT /change-password` | Đổi mật khẩu cho tài khoản đã xác thực. |
| `GET /health` | Tiến trình còn sống, không đụng DB. |
| `GET /health/ready` | Truy vấn được MySQL, trả `503` nếu không. |

`POST /login` giới hạn theo tài khoản: sai 10 lần liên tiếp thì chỉ được thử lại mỗi 60 giây (`429`, header `Retry-After`).

## Cấu trúc repo

| Thư mục | Nội dung |
| --- | --- |
| [`frontend/src/app`](frontend/src/app) | Route và layout của Next.js App Router. |
| [`frontend/src/features`](frontend/src/features) | Đăng nhập, dashboard học sinh và Lịch học. |
| [`backend/app/modules`](backend/app/modules) | Router, service, schema và repository theo tính năng. |
| [`backend/app/models`](backend/app/models) | Model SQLAlchemy cho dữ liệu tài khoản, học sinh, lớp và buổi học. |
| [`backend/alembic/versions`](backend/alembic/versions) | Lịch sử migration cơ sở dữ liệu. |
| [`deploy`](deploy) | Mẫu Nginx và systemd cho VPS (chưa chạy thử). |

## Kiểm thử backend

Mặc định `pytest` chỉ chạy test SQLite. Các test MySQL (tranh chấp, khóa dòng) bị ẩn sau `SCHEDULE_MYSQL_TESTS=1` và **chỉ được chạy trên DB có chữ `test` trong tên**, vì chúng ghi và xóa dữ liệu. `conftest.py` từ chối chạy nếu trỏ vào DB dev.

```powershell
Set-Location backend
..\.venv\Scripts\python.exe -m pytest

# Một lần: tạo DB test riêng trong container MySQL (thay <MYSQL_USER> bằng giá trị trong backend/.env)
docker exec -it lms_mysql mysql -uroot -p -e "CREATE DATABASE IF NOT EXISTS vision_education_lms_test; GRANT ALL ON vision_education_lms_test.* TO '<MYSQL_USER>'@'%';"
$env:MYSQL_DATABASE = "vision_education_lms_test"
..\.venv\Scripts\python.exe -m alembic upgrade head
Remove-Item Env:MYSQL_DATABASE

# Mỗi lần chạy đủ bộ test, gồm cả ca MySQL
$env:LMS_TEST_MYSQL_DATABASE = "vision_education_lms_test"; $env:SCHEDULE_MYSQL_TESTS = "1"
..\.venv\Scripts\python.exe -m pytest
```

Workflow [CI](.github/workflows/ci.yml) chạy cùng bộ test này với MySQL thật, cộng `alembic check` và build frontend.

### Cập nhật thư viện backend

Phiên bản được ghim trong `requirements.txt`, còn `constraints.txt` giữ toàn bộ thư viện gián tiếp. Khi nâng cấp có chủ đích: đổi số trong `requirements.txt`, cài lại, chạy đủ test, rồi sinh lại `constraints.txt` bằng `pip freeze`.

## Kiểm tra frontend

Từ thư mục gốc:

```powershell
npm --prefix frontend run lint
npm --prefix frontend run build   # cần NEXT_PUBLIC_API_URL, thiếu thì build dừng với thông báo rõ
```

Xem [hồ sơ dự án](PROJECT_CONTEXT.md) để biết nghiệp vụ đã chốt và [roadmap](PROJECT_ROADMAP.md) để theo dõi phạm vi phát triển. Dự án dùng [giấy phép MIT](LICENSE).
