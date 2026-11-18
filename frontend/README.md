# Frontend Vision Education LMS

Frontend dùng Next.js App Router. Route nằm trong `src/app/`, còn trang và component nghiệp vụ nằm trong `src/features/`. Axios gọi API FastAPI theo `NEXT_PUBLIC_API_URL` trong `.env`.

Chạy từ thư mục này:

```powershell
npm ci
npm run dev
```

Mở [Lịch học mẫu](http://localhost:5173/schedule-preview) hoặc [Đăng nhập](http://localhost:5173/login). Hướng dẫn chạy API và kiểm tra frontend nằm trong [README của dự án](../README.md).
