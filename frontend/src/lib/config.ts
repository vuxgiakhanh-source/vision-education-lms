// NEXT_PUBLIC_* được Next.js nhúng cứng vào mã lúc build, không đọc lại khi chạy.
// Vì vậy phải kiểm tra ngay lúc build: nếu thiếu mà vẫn build thì trình duyệt của học sinh
// sẽ gọi http://localhost:8000, tức chính máy của các em.
const apiUrl = process.env.NEXT_PUBLIC_API_URL

if (!apiUrl && process.env.NODE_ENV === 'production') {
    throw new Error('Thiếu NEXT_PUBLIC_API_URL khi build production. Đặt địa chỉ API trong frontend/.env hoặc biến môi trường.')
}

export const env = {
    API_URL: apiUrl ?? 'http://localhost:8000',
}
