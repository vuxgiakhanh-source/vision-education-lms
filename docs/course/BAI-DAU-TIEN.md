# Bài học mẫu: tự đọc lại luồng đăng nhập của chính mình

Mục tiêu: hiểu một đoạn code hiện có đến mức tự giải thích từng ký hiệu và đường
đi dữ liệu. Bài này không yêu cầu thay code. Mở CODE_GUIDE khi cần tìm file.

## Phần 1 — Đọc một hàm từ ngoài vào trong

Trích cấu trúc rút gọn từ LoginForm hiện tại, các dependency lấy ở phần trên
component. Đây không phải file độc lập để chạy bằng Node:

```tsx
async function onSubmit(data: LoginFormData) {
  try {
    const res = await authService.login(data);
    localStorage.setItem('access_token', res.access_token);
    if (res.must_change_password) {
      navigate('/change-password');
    } else {
      navigate('/dashboard');
    }
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Đăng nhập thất bại';
    setError('root', { message });
  }
}
```

| Ký hiệu/đoạn | Nghĩa và câu hỏi cần tự trả lời |
|---|---|
| async | Hàm trả Promise; ai đang đợi kết quả của nó? |
| function onSubmit | Khai báo hàm, chưa gọi hàm. Tìm nơi handleSubmit nhận hàm này |
| data | Biến tham số cho giá trị form đã đi qua xử lý form |
| : LoginFormData | Kiểu TypeScript, không tự kiểm tra JSON ở backend |
| `{ ... }` sau hàm | Khối thân hàm; khác object literal trong setError |
| try | Phạm vi bắt các lỗi được ném/reject khi await trong khối |
| const res | Biến giữ kết quả trả về; không phải giá trị trước khi Promise xong |
| authService.login(data) | Lấy method login trên object authService và gọi với data |
| await | Chờ kết quả Promise tại đây; không khóa toàn bộ trình duyệt |
| res.access_token | Đọc thuộc tính kết quả, không phải gọi hàm |
| localStorage.setItem | Ghi một chuỗi vào storage của origin hiện tại |
| if/else | Chọn đường đi theo cờ backend trả về |
| navigate | Thay route frontend; không tự cấp quyền server |
| catch (error) | Nhận lỗi; với strict TypeScript cần thu hẹp trước khi đọc message |
| instanceof Error | Một cách kiểm tra error là instance phù hợp |
| `? ... : ...` | Chọn một giá trị bằng điều kiện |
| `{ message }` | Object shorthand, tương đương `{ message: message }` |

Không cần thuộc cả bảng trong lần đầu. Che cột nghĩa và tự kể bằng lời mình.

## Phần 2 — Bảng theo dõi dữ liệu

Giả định form có một số điện thoại hợp lệ và mật khẩu do người dùng nhập; không
ghi giá trị mật khẩu/token thật vào nhật ký.

| Bước | Dữ liệu/hiệu ứng |
|---|---|
| register + resolver | Form lấy giá trị và chạy schema frontend |
| onSubmit | Nhận object có phoneNumber, password |
| authService.login | Đổi phoneNumber thành phone_number theo hợp đồng API |
| api.post | Axios gửi POST /login đến baseURL |
| router backend | Nhận LoginRequest, gọi LoginService.login |
| repository | Query User theo phone_number |
| service | Kiểm tồn tại, mật khẩu, is_active; tạo response/token khi hợp lệ |
| authService return | Trả `res.data`, không trả nguyên AxiosResponse |
| form sau await | Vì vậy res ở form là LoginResponse với access_token và cờ đổi mật khẩu |
| lưu và điều hướng | localStorage nhận token; navigate theo cờ |

Hai biến cùng tên res ở hai hàm khác nhau không phải cùng biến. Đây là scope:
res trong lớp gọi API là AxiosResponse, res trong form là data mà hàm đó return.

## Phần 3 — Đọc truy vấn Python từng bước

Đoạn rút gọn repository hiện tại, phụ thuộc self.db và model User đã có:

```python
def find_user_by_phone_number(self, phone_number: str):
    return (
        self.db.query(User)
        .filter(User.phone_number == phone_number)
        .first()
    )
```

- def khai báo hàm; dấu `:` mở khối và indentation xác định thân.
- self là instance LoginRepository, db là Session được truyền vào constructor.
- User là model ORM; User.phone_number là biểu diễn cột, không phải số của một user cụ thể.
- Ở đây `==` tạo điều kiện query qua SQLAlchemy, không đơn giản là so hai chuỗi Python.
- filter nhận điều kiện; first thực hiện lấy kết quả đầu hoặc None.
- Dấu ngoặc ngoài giúp viết biểu thức nhiều dòng; dấu chấm tiếp nối lời gọi method.
- Return đưa User/None về service; repository không điều hướng trang hay tạo JWT.

Tự viết SQL tương đương bằng lời: chọn một người dùng có số điện thoại phù hợp.
Sau đó hỏi nếu DB có hai hàng trùng số thì sao? Tìm ràng buộc migration hiện tại,
ghi điều chưa có/đã có, không suy ra tự động vì form không cho nhập sai.

## Phần 4 — Theo dõi ba đường đi

### A: Thành công và không bắt đổi mật khẩu

Service trả token, cờ false → storage được ghi → frontend tới dashboard. Hiện
dashboard vẫn hiển thị mock nên việc tới trang không chứng minh đã lấy hồ sơ thật.

### B: Thành công nhưng phải đổi mật khẩu

Cờ true → tới change-password. Đọc repository đổi mật khẩu để tìm nơi đặt cờ
về false. Sau đó tự hỏi truy cập thẳng dashboard có bị chặn không; đối chiếu App.tsx.

### C: Sai mật khẩu

Service ném lỗi nghiệp vụ → router đổi thành HTTP 401 → Axios reject → form
catch/setError. Quan sát message hiện tại: form chưa tự động lấy mọi detail từ
backend. Muốn cải thiện thông báo cần thống nhất mapping lỗi, không đổi backend
để trả 200 cho tiện.

## Phần 5 — Bài làm của bạn

1. Viết sơ đồ đăng nhập mà không nhìn bảng.
2. Định nghĩa 8 từ: tham số, return, Promise, object, method, dependency, schema, Session.
3. Chỉ nơi kiểm tra số điện thoại ở frontend và backend; so sánh điều kiện thực tế.
4. Phân biệt password người dùng nhập với hashed_password lấy từ DB.
5. Giải thích vì sao không tin cờ role do người dùng tự gửi.
6. Tìm cách xác nhận request thành công bằng Network mà không chép token ra tài liệu.
7. Viết một test case đăng nhập sai với mong đợi cụ thể, ghi chưa chạy nếu môi trường chưa sẵn sàng.
8. Ghi điểm dừng: câu nào chưa hiểu, mở file nào lần sau, bài học nền nào cần ôn.

**Điều kiện qua:** tự kể được đường đi và một nhánh lỗi, không cần nhớ từng dòng
Tailwind. Sau đó làm một thay đổi nhỏ ở bài thực hành riêng để chứng minh mình
hiểu, không sửa đồng loạt code sản phẩm khi chưa có mục tiêu và cách kiểm tra.
