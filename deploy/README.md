# Mẫu triển khai lên VPS

**Trạng thái: mẫu viết theo kế hoạch, chưa chạy thử trên VPS thật.** Kiểm từng bước và đo lại ở mốc M3 trước khi tin vào các con số.

Kiến trúc: Nginx (443) → Next.js `127.0.0.1:5173` và FastAPI `127.0.0.1:8000`; MySQL chỉ nghe `127.0.0.1`.

| File | Việc |
| --- | --- |
| `nginx/lms.conf` | Proxy `/api/` tới FastAPI, trang web tới Next, thư mục `internal` để Nginx tự gửi tệp đề |
| `systemd/lms-api.service` | Chạy uvicorn nhiều worker, tự khởi động lại |
| `systemd/lms-web.service` | Chạy `npm run start` |

Thứ tự gợi ý:

1. Tạo user `lms`, chép mã vào `/opt/lms`, `python -m venv .venv`, rồi `pip install -r backend/requirements.txt -c backend/constraints.txt`.
2. `backend/.env`: đặt `ENVIRONMENT=production`, `ALLOWED_ORIGINS=https://<tên miền>`, mật khẩu MySQL mạnh, `SECRET_KEY` mới (`openssl rand -hex 32`).
3. `alembic upgrade head` trong `backend/`.
4. `frontend/.env`: `NEXT_PUBLIC_API_URL=https://<tên miền>/api`, rồi `npm ci && npm run build` (thiếu biến này build sẽ dừng).
5. Chép hai file systemd, `systemctl enable --now lms-api lms-web`.
6. Chép `nginx/lms.conf`, `certbot` lấy chứng chỉ, `nginx -t` rồi `systemctl reload nginx`.
7. Kiểm: `curl https://<tên miền>/api/health/ready`, mở `/docs` phải ra 404.
8. Đặt `MYSQL_BUFFER_POOL_SIZE`, `MYSQL_MAX_CONNECTIONS` theo RAM của VPS (xem `backend/docker-compose.yml`) nếu MySQL chạy bằng Docker.
