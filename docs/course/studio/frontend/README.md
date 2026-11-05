# Sổ lớp học — source để đối chiếu sau khi tự viết

Học theo `../../G1-trang-web-tu-thu-muc-trong.md`, rồi
`../../G2-tu-js-sang-react.md`. Hai bản có cùng nghiệp vụ: thêm lớp, list và tìm
tên; dữ liệu chỉ ở RAM, refresh sẽ mất. Chưa có tài khoản, API hay DB.

## JavaScript thường

```powershell
Set-Location D:\vision-education-lms\docs\course\studio\frontend\vanilla
python -m http.server 8018 --bind 127.0.0.1
```

Mở `http://127.0.0.1:8018`. Server này chỉ phục vụ file tĩnh.

## React/TypeScript

```powershell
Set-Location D:\vision-education-lms\docs\course\studio\frontend\react
npm install
npm run dev
```

Mở `http://127.0.0.1:5186`; terminal khác trong cùng thư mục chạy `npm run build`.
Gói được ghim theo phiên bản thực tế trong lockfile xưởng tại thời điểm viết.
Cấu hình compiler/plugin giữ như xưởng. Chỉ đưa các gói thực sự dùng vào bản này.
Sau lần cài đầu, giữ lockfile mới trong repo học và dùng `npm ci` khi dựng lại.

## Đối chiếu thao tác

1. Mới mở: 0/0 và lời mời tạo lớp.
2. Submit tên chỉ có khoảng trắng: lỗi, vẫn 0/0.
3. Thêm `  Toán 10A  ` rồi `Văn 10B`: hai mã 1/2, tên đã trim.
4. Tìm `  tOÁn  `: một kết quả; không xóa lớp Văn khỏi dữ liệu gốc.
5. Tìm không khớp: 0/2 và thông báo rỗng khác với chưa có dữ liệu.
6. Thêm `<img src=x>`: hiển thị như chữ, không tạo thẻ ảnh.
7. Thử tên dài 100 và 101 đơn vị UTF-16; mẫu quy ước `string.length` của JS,
   chưa phải số ký tự người đọc nhìn thấy hoặc policy tiêu đề ở backend xưởng.
8. Refresh: lớp vừa thêm biến mất theo phạm vi bài học.
9. Thử 320px và zoom 200%: input/nút xuống cột, tiêu đề dài không làm tràn trang.

## Kiểm tra khi máy đã có dependency xưởng

Không cần cài mạng chỉ để kiểm bản tham chiếu. Có thể tạo junction `node_modules`
trong `react` trỏ đến `../../../workshop/frontend/node_modules` đã có. Đích trên
filesystem được tính từ thư mục `react`; kiểm đường dẫn tuyệt đối trước khi tạo.
Đây chỉ là cách tái sử dụng môi trường để kiểm, không phải bước học bắt buộc.
Lệnh PowerShell với đường dẫn cụ thể nằm trong G2. Chưa chạy ở browser/MySQL thì
không được ghi rằng đã kiểm các môi trường đó.
