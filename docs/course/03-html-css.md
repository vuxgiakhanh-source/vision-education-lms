# 03 — HTML, CSS, responsive và khả năng sử dụng

Mục tiêu: giải thích được bố cục mình viết, không sửa bằng thử số ngẫu nhiên.

## Bài 03.1 — HTML có nghĩa và form đúng

```html
<main>
  <h1>Bài tập của tôi</h1>
  <form>
    <label for="search">Tìm bài tập</label>
    <input id="search" name="search" type="search" />
    <button type="submit">Tìm kiếm</button>
  </form>
</main>
```

`label` gắn với input qua id; placeholder không thay label. Dùng button cho hành
động và link cho điều hướng. Trong form, button mặc định thường submit; các nút
mở hộp thoại/ẩn mật khẩu nên khai báo `type="button"`.
Giữ thứ tự heading có nghĩa, dùng list/table khi dữ liệu đúng dạng đó.
Trong JSX: dùng `htmlFor`, `className`; event là hàm, không phải chuỗi JavaScript.

## Bài 03.2 — Box model và phép tính kích thước

```css
* { box-sizing: border-box; }
.card {
  width: 300px;
  padding: 24px;
  border: 1px solid #e2e8f0;
}
```

Với border-box, tổng chiều rộng card là 300px, phần nội dung còn 250px. Margin
ở ngoài box. Với content-box, padding và border làm tổng rộng hơn width đã đặt.
Trước khi nói card bị lệch, xem computed width, padding, border, margin trong DevTools.

`px` là CSS pixel, không phải một điểm ảnh vật lý cố định. `rem` dựa vào cỡ chữ
gốc; `%` phụ thuộc containing block. `vw` theo viewport. Inch màn hình không đủ
để suy ra viewport vì còn độ phân giải, OS scale, zoom và giao diện trình duyệt.

## Bài 03.3 — Flexbox và Grid giải quyết bài khác nhau

```css
.toolbar { display: flex; align-items: center; gap: 12px; }
.toolbar input { flex: 1; min-width: 0; }
.dashboard {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 360px;
  gap: 24px;
  align-items: start;
}
@media (max-width: 1000px) {
  .dashboard { grid-template-columns: minmax(0, 1fr); }
}
```

Flex thường phù hợp hàng/cột một chiều, Grid phù hợp các vùng có hàng và cột.
`min-width: 0` cho phép flex/grid item co dưới độ rộng nội dung mặc định;
`minmax(0, 1fr)` tránh nội dung dài tự đẩy cả cột. `gap` là khoảng cách giữa item.
`align-items: start` giúp card không bị kéo cao bằng hàng ngoài ý muốn.

`height: 100%` cần hiểu chiều cao cha. Đặt height cố định cho văn bản có thể làm
cắt chữ khi zoom hoặc dịch ngôn ngữ. Dùng min-height khi chiều cao có thể tăng.

## Bài 03.4 — Ảnh banner là bài toán tỉ lệ

- `object-fit: cover`: lấp khung và có thể cắt một chiều.
- `contain`: giữ toàn ảnh nhưng có thể để khoảng trống.
- `object-position`: chọn vị trí ảnh trong khung; không tự bảo vệ mọi chi tiết.
- Ảnh nền có chữ nằm trong bitmap sẽ khó responsive hơn chữ HTML.

Trước khi sửa, tính tỉ lệ ảnh nguồn và khung hiển thị. Nếu ảnh có mũ bên phải,
hãy thử khung ngắn/rộng và kiểm tra vùng quan trọng, độ tương phản, chữ xuống dòng.
Đừng hứa vừa lấp mọi khung, vừa không cắt, vừa không méo với cùng một bitmap có
tỉ lệ khác khung; cần lựa chọn crop, khoảng trống hoặc bố cục khác.

Trong repo hiện tại, `index.css` chứa các biến và breakpoint, `WelcomeBanner`
hiển thị artwork gốc. Xem chúng cùng nhau. Giữ các mốc nhỏ đã duyệt khi sửa ultrawide.

## Bài 03.5 — Tailwind vẫn là CSS

```tsx
export function ExampleCard() {
  return (
    <section className="min-w-0 rounded-2xl border border-slate-200 bg-white p-4 sm:p-6">
      <h2 className="text-lg font-semibold">Việc cần làm</h2>
      <p className="mt-2 break-words text-slate-600">Nội dung dài có thể xuống dòng.</p>
    </section>
  );
}
```

`p-4` đặt padding, `sm:p-6` áp dụng từ breakpoint sm trở lên. Nó không có nghĩa
chỉ áp dụng trên một dòng điện thoại cụ thể. `wide` và `ultrawide` là breakpoint
tùy chỉnh của repo. Không ghép tên utility bằng chuỗi động mà build không thấy
được toàn tên; dùng mapping chuỗi class đầy đủ.

## Bài 03.6 — Hoàn thiện giao diện bằng hành vi

Một modal cần: tên rõ, focus vào nơi phù hợp, giới hạn focus khi mở, Escape đóng
khi hợp lý và trả focus về nút mở. Thư viện có thể hỗ trợ nhưng vẫn phải thử bàn phím.
Nút icon cần accessible name; trạng thái lỗi phải có chữ, không chỉ màu đỏ.
Loading phải ngăn thao tác trùng theo nhu cầu, lỗi có đường thử lại; dữ liệu rỗng
có hướng dẫn phù hợp. Không xóa outline mà bỏ luôn dấu hiệu focus.

## Bài tự viết và kiểm tra

- **UI1:** form tạo lớp với label, lỗi theo trường, nút submit và trạng thái xử lý.
- **UI2:** hai cột xuống một cột; thử tiêu đề dài, số lượng 0, 1000 và viewport 320px.
- **UI3:** giải thích bằng phép tính vì sao một card tràn ngang; sửa nguyên nhân.
- **UI4:** kiểm tra bằng Tab/Shift+Tab/Enter, zoom 200%, không chỉ nhìn ảnh 100%.
- **UI5:** chụp trước/sau ở cùng viewport; ghi kích thước CSS, không chỉ ghi inch.

Qua chương khi tự dựng được layout và giải thích computed styles. Không coi
`overflow: hidden` là cách sửa chung cho mọi trường hợp tràn chữ.

Tham khảo: [MDN CSS](https://developer.mozilla.org/en-US/docs/Web/CSS),
[Tailwind responsive design](https://tailwindcss.com/docs/responsive-design).
