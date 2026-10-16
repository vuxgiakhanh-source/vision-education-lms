# 00 — Cách học, đọc code và tìm lỗi

## Bài 00.1 — Biết mình đang đứng ở đâu

Viết câu trả lời trước khi đọc CODE_GUIDE:

1. Khi bấm đăng nhập, hàm nào chạy đầu tiên?
2. `phoneNumber` được đổi thành `phone_number` ở đâu?
3. Ai quyết định mật khẩu đúng? Ai tạo token? Ai điều hướng?
4. `User` khác `LoginRequest` ở điểm nào?
5. Tại sao tên Gia Khánh vẫn hiện dù chưa gọi `/me`?
6. Một nút có giao diện nhưng chưa có callback thì đã hoàn thành chức năng chưa?

Chấm từng câu: 0 = chưa biết, 1 = giải thích được, 2 = tự tìm được code và kiểm tra.
Nếu chưa chắc câu nào, ghi tên kiến thức cần học thay vì tự kết luận mình kém.

## Bài 00.2 — Bốn nơi chạy code khác nhau

| Nơi | Chạy gì? | Nhìn lỗi ở đâu? |
|---|---|---|
| Trình duyệt | React/JavaScript, giao diện, HTTP client | Console và Network |
| Vite/TypeScript | Dev server, chuyển đổi/build, kiểm tra kiểu | Terminal frontend |
| FastAPI/Python | Endpoint và nghiệp vụ backend | Terminal/log backend |
| MySQL | Lưu dữ liệu và ràng buộc | Công cụ SQL, lỗi DB từ backend |

React component gọi một hàm Python trực tiếp là mô hình sai cho kiến trúc hiện tại.
Trình duyệt gửi HTTP; FastAPI nhận HTTP rồi mới gọi Python. Network là cầu nối
để quan sát hai phía. JSX không được MySQL đọc; SQL không chạy trong React.

## Bài 00.3 — Thuật toán trước cú pháp

Với yêu cầu đếm bài chưa nộp, viết bằng lời:

```text
Đầu vào: danh sách bài, mỗi bài có trạng thái.
Đầu ra: số nguyên không âm.
Khởi tạo tổng = 0.
Duyệt từng bài.
Nếu trạng thái chưa nộp, tăng tổng.
Trả tổng.
```

Sau đó mới quyết định dùng vòng lặp hay `filter`. Nếu đầu vào có trạng thái lạ,
phải biết cách xử lý; không thể mong cú pháp tự quyết định quy tắc sản phẩm.

Mẫu phân tích cho mọi bài:

```text
Người thực hiện:
Đầu vào và nguồn dữ liệu:
Đầu ra và tác động:
Quyền cần có:
Quy tắc:
Trạng thái trước/sau:
Tình huống biên:
Ví dụ đúng, ví dụ sai:
Cách chứng minh:
```

## Bài 00.4 — Đọc một file có chủ đích

Mở `frontend/src/features/auth/login/components/LoginForm.tsx` ở repo.
Tìm `onSubmit`, bỏ qua phần màu và icon ở lượt đọc đầu.
Đánh dấu lời gọi `authService.login`, nơi ghi localStorage và hai nhánh navigate.
Sau đó lần theo lớp gọi API và backend login. Mỗi bước ghi đúng một câu:
đầu vào → kiểm tra/thay đổi → đầu ra. Đối chiếu sơ đồ trong CODE_GUIDE.

Đừng lấy số lượng file đã đọc làm số kiến thức đã hiểu. Tự kể lại một luồng
và sửa được một biến thể là bằng chứng tốt hơn.

## Bài 00.5 — Debug theo giả thuyết

Ví dụ bấm nộp bài nhưng danh sách cô không đổi:

1. Có event chạy không? Đặt breakpoint ở handler.
2. Network có request không? Nếu không, xem handler/validation frontend.
3. URL, method, payload, header có đúng không?
4. Response là lỗi hay thành công? Đọc status và body.
5. Backend có tới service và query không? Quan sát bằng debugger/log phù hợp.
6. DB có bản ghi sau commit không?
7. DB đã đúng nhưng UI sai? Kiểm tra dữ liệu trang, cache/refetch và điều kiện render.

Mỗi lần đổi một nguyên nhân rồi thử lại. Không thay cùng lúc tên field, URL,
schema và kiểu dữ liệu rồi kết luận không biết sửa nào đã có tác dụng.
Không log mật khẩu, token hoặc toàn bộ dữ liệu cá nhân để tìm lỗi.

## Bài 00.6 — Git để giữ trí nhớ

Chạy từ gốc repo:

```powershell
git status --short
git diff --stat
git diff -- frontend/src/features/auth/login/components/LoginForm.tsx
git log -5 --oneline
```

- `status`: file nào thay đổi/chưa được theo dõi.
- `diff`: nội dung thay đổi chưa stage; không đồng nghĩa toàn bộ lịch sử.
- `log`: các commit đã lưu. Thay đổi chưa commit không xuất hiện trong log.
- Một commit nên mô tả một việc có nghĩa, ví dụ `auth: handle expired sessions`.

Đọc diff trước khi stage. Chọn file liên quan; không dùng `git add .` theo thói quen
khi có thay đổi khác đang dở. Khóa và cấu hình riêng không được đưa vào commit.
Giáo án không thực hiện commit hay khôi phục file thay bạn.

## Bài viết tay và điều kiện qua chương

- A: vẽ luồng đăng nhập trên giấy, chỉ đúng các file trong repo.
- B: tự tìm vì sao `/forgot-password` chưa có trang tương ứng.
- C: mô tả cách chứng minh dashboard đang dùng mock mà không dựa vào phỏng đoán.
- D: viết báo cáo lỗi 5 dòng: môi trường, bước tái hiện, mong đợi, thực tế, bằng chứng.

Qua chương khi tự trả lời sáu câu khảo sát và phân biệt được lỗi trình duyệt,
API, database, cấu hình. Ghi điều chưa biết vào WORKLOG để chọn chương kế tiếp.
