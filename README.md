# Vision Education LMS

Ứng dụng quản lý học toán và luyện tập. Frontend: React, TypeScript, Vite,
Tailwind CSS. Backend: FastAPI, SQLAlchemy, MySQL, Alembic.

## Mở lại dự án: bắt đầu ở đây

1. Đọc [điểm dừng và nhật ký](docs/WORKLOG.md).
2. Dùng [bản đồ code](docs/CODE_GUIDE.md) để tìm đúng file.
3. Làm một việc nhỏ trong [lộ trình học và thực hành](docs/LEARNING_ROADMAP.md).
4. Trước khi nghỉ, cập nhật nhật ký: đã làm gì, kiểm tra gì, tiếp theo làm gì.

[Roadmap sản phẩm ban đầu](PROJECT_ROADMAP.md) chứa các ý tưởng tương lai;
không dùng danh sách đó để kết luận chức năng đã hoàn thành.

## Hiện trạng đã đọc từ code — 17/10/2026

| Phần | Trạng thái |
|---|---|
| Đăng nhập, đổi mật khẩu, `/me` | Có backend và lớp gọi API frontend; cần chạy lại toàn luồng để xác nhận với database hiện tại |
| Dashboard học sinh | Có giao diện responsive; dữ liệu nghiệp vụ vẫn là mock |
| Phân quyền | Có enum 4 vai trò; chưa có cơ chế đầy đủ giới hạn quyền theo lớp |
| Lớp học, giao/nộp/chấm bài, luyện thi | Chưa thấy module nghiệp vụ tương ứng trong backend |
| Kiểm tra frontend | Có lệnh build và lint; chưa thấy bộ kiểm thử tự động/CI trong repo đã rà |

Chi tiết và các nút chưa nối chức năng: [bản đồ code](docs/CODE_GUIDE.md).

## Chạy frontend

Trong terminal ở thư mục gốc:

```powershell
cd frontend
npm ci
npm run dev -- --host 127.0.0.1 --port 5175
```

- Trang chính: `http://127.0.0.1:5175/dashboard`.
- Bộ xem responsive: `http://127.0.0.1:5175/dashboard-preview/index.html`.
- Kiểm tra code tại `frontend`: `npm run build` và `npm run lint`.

## Chuẩn bị và chạy backend

Thực hiện khi cần chạy backend; tài liệu được viết theo cấu trúc Windows hiện tại.
Nếu chưa có môi trường Python, tạo ở gốc bằng `python -m venv .venv`, sau đó:

```powershell
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
cd backend
```

Chuẩn bị `.env` từ `.env.example` nếu chưa có; giữ file cấu hình đang dùng nếu đã có.
Điền thông tin MySQL và khóa JWT tại máy, không ghi giá trị thật vào tài liệu.
Nếu dùng Docker Compose của repo, khởi động MySQL bằng `docker compose up -d`.
Backend hiện kết nối MySQL ở `localhost:3306`.

Trong terminal tại `backend`, với database đã cấu hình:

```powershell
..\.venv\Scripts\python.exe -m alembic upgrade head
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- API docs: `http://127.0.0.1:8000/docs`.
- Với frontend ở trên, CORS phải cho phép `http://127.0.0.1:5175`;
  cấu hình mẫu hiện còn dùng các port khác.
- Frontend đọc `VITE_API_URL`; khi không có, Axios mặc định dùng `http://localhost:8000`.
- Script seed hiện chỉ thêm một tài khoản học sinh mẫu và không kiểm tra trùng;
  đọc script trước khi dùng, không chạy lại tùy tiện trên dữ liệu có sẵn.
- Các bước cài đặt/database này được đối chiếu từ source; chưa được chạy lại trong lần lập tài liệu.
