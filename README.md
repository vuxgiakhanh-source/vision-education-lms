# Vision Education LMS

Ứng dụng quản lý học toán và luyện tập. Frontend: React, TypeScript, Vite,
Tailwind CSS. Backend: FastAPI, SQLAlchemy, MySQL, Alembic.

Nghiệp vụ đã chốt và điểm dừng hiện tại nằm trong [hồ sơ dự án](PROJECT_CONTEXT.md).
Phạm vi dự kiến nằm trong [roadmap sản phẩm](PROJECT_ROADMAP.md).

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
