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
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt

if (-not (Test-Path backend\.env)) { Copy-Item backend\.env.example backend\.env }
if (-not (Test-Path frontend\.env)) { Copy-Item frontend\.env.example frontend\.env }
```

- Trong `backend/.env`, điền các giá trị `MYSQL_*` và `SECRET_KEY`. Cấu hình `ALLOWED_ORIGINS=http://localhost:5173` để khớp với địa chỉ frontend ở trên.
- Trong `frontend/.env`, đặt `NEXT_PUBLIC_API_URL=http://127.0.0.1:8000`. Đổi tên biến nếu đang dùng `VITE_API_URL` từ phiên bản cũ, rồi khởi động lại frontend.

Với cơ sở dữ liệu phát triển mới, chạy các lệnh sau trong terminal backend:

```powershell
Set-Location backend
docker compose up -d mysql

# Sau khi MySQL sẵn sàng, tạo bảng tài khoản và thêm tài khoản thử.
..\.venv\Scripts\python.exe -m alembic upgrade 2bc85ebdd106
..\.venv\Scripts\python.exe -m scripts.seed_users
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Dùng tài khoản trong [script seed](backend/scripts/seed_users.py) để thử đăng nhập. Chạy seed một lần trên cơ sở dữ liệu mới vì script sẽ chèn thêm bản ghi mỗi lần chạy. Mốc migration ở trên tạo bảng `users` cho luồng tài khoản. Các migration lịch hiện vẫn chưa tạo bảng `students` và chưa có đủ cột nội dung buổi học.

### API hiện có

Tài liệu tương tác nằm tại [Swagger UI](http://127.0.0.1:8000/docs).

| Endpoint | Chức năng |
| --- | --- |
| `POST /login` | Xác thực số điện thoại và mật khẩu, cấp JWT. |
| `GET /me` | Lấy hồ sơ từ JWT Bearer. |
| `PUT /change-password` | Đổi mật khẩu cho tài khoản đã xác thực. |

## Cấu trúc repo

| Thư mục | Nội dung |
| --- | --- |
| [`frontend/src/app`](frontend/src/app) | Route và layout của Next.js App Router. |
| [`frontend/src/features`](frontend/src/features) | Đăng nhập, dashboard học sinh và Lịch học. |
| [`backend/app/modules`](backend/app/modules) | Router, service, schema và repository theo tính năng. |
| [`backend/app/models`](backend/app/models) | Model SQLAlchemy cho dữ liệu tài khoản, học sinh, lớp và buổi học. |
| [`backend/alembic/versions`](backend/alembic/versions) | Lịch sử migration cơ sở dữ liệu. |

Để kiểm tra frontend từ thư mục gốc:

```powershell
npm --prefix frontend run lint
npm --prefix frontend run build
```

Xem [hồ sơ dự án](PROJECT_CONTEXT.md) để biết nghiệp vụ đã chốt và [roadmap](PROJECT_ROADMAP.md) để theo dõi phạm vi phát triển. Dự án dùng [giấy phép MIT](LICENSE).
