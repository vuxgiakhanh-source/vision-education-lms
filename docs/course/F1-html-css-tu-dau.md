# F1 — HTML/CSS từ đầu cho người biết Python

HTML/CSS không phải Python viết bằng dấu ngoặc khác. HTML mô tả nội dung và
cấu trúc; CSS chọn phần tử rồi đặt quy tắc trình bày. Logic tương tác học bằng
JavaScript sau khi đã thấy một trang tĩnh được dựng thế nào.

## 1. Một trang nhỏ trước dashboard

Tạo file index.html trong thư mục học riêng, không ghi đè frontend sản phẩm:

```html
<!doctype html>
<html lang="vi">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Trang học đầu tiên</title>
    <link rel="stylesheet" href="style.css">
  </head>
  <body>
    <section class="card">
      <h1>Bài tập của An</h1>
      <p>Còn 3 bài chưa nộp.</p>
      <button type="button">Xem bài</button>
    </section>
  </body>
</html>
```

Mở file bằng browser: thấy nội dung trước khi thêm CSS. Nút hiện được chưa có
nghĩa nó đã có chức năng. `<...>` mở một thẻ; `</...>` đóng thẻ đó. h1 là tiêu
đề chính, p là đoạn văn, button là nút; section nhóm nội dung có ý nghĩa.

`class="card"` gắn nhãn để CSS chọn, không gọi hàm Python nào. head chứa thông
tin trang/tài nguyên, body chứa nội dung chính. Link trỏ file CSS cùng thư mục;
sai tên/đường dẫn thì stylesheet không được tải. Meta viewport giúp cách bố trí
trên màn hẹp phù hợp kích thước thiết bị, chưa tự làm layout responsive.

## 2. Một luật CSS, đọc từng mảnh

Tạo style.css cạnh HTML:

```css
.card {
  background-color: white;
  color: #20332a;
  padding: 16px;
  border: 1px solid #cbd6ce;
}
```

| Phần | Nghĩa |
|---|---|
| .card | Chọn phần tử có class card; dấu . thuộc cú pháp selector |
| { và } | Bao các khai báo áp cho phần tử được chọn |
| padding | Tên thuộc tính CSS |
| : | Ngăn tên thuộc tính với giá trị |
| 16px | Giá trị khoảng đệm, đơn vị CSS pixel |
| ; | Kết thúc một khai báo |

Đừng viết `.card` vào class HTML: HTML dùng `class="card"`, CSS mới dùng dấu
chấm để chọn class. CSS `color` đổi màu chữ; `background-color` đổi nền.

## 3. Selector: đang sửa đúng phần tử chưa?

| Viết | Chọn gì? |
|---|---|
| p | Mọi thẻ p trong phạm vi stylesheet |
| .card | Phần tử có class card |
| #search | Phần tử có id search; id cần duy nhất trong trang |
| .card p | Những p nằm bên trong card |
| .card > p | p là con trực tiếp của card |

Ở đây `.` là cú pháp chọn class, không phải dấu đọc thuộc tính của JS. Dấu
`>` ở selector là quan hệ con trực tiếp, không phải phép so sánh lớn hơn.
Một ký hiệu đổi nghĩa theo ngôn ngữ/ngữ cảnh; đọc cả câu luật CSS.

## 4. Padding, border, margin và gap khác nhau ở đâu?

```text
margin (ngoài hộp)
  border (viền hộp)
    padding (đệm bên trong)
      content (chữ/nội dung)
```

Padding tạo khoảng thở giữa nội dung với viền chính nó. Margin đẩy hộp ra xa
hộp khác. Gap là khoảng cách giữa các item của container dùng flex/grid,
không phải cách đặt đệm cho mọi loại display.

Trong sách mở **Thử CSS từ đầu**, chỉ đổi padding rồi đổi gap; quan sát cái gì
di chuyển. Nếu display:block, gap không tách các block thông thường trong lab.
Đổi display:flex rồi thử lại: thấy sự khác nhau thay vì chỉ nhớ định nghĩa.

## 5. Width và box-sizing: tính một hộp cụ thể

```css
.card {
  box-sizing: border-box;
  width: 300px;
  max-width: 100%;
  padding: 16px;
  border: 2px solid #cbd6ce;
}
```

Với border-box, tổng ngang hộp là300px nếu cha cho phép; nội dung còn
300−16×2−2×2=264px. Margin nằm ngoài con số này. max-width:100% giúp giới hạn
theo cha; không bảo đảm mọi chuỗi dài bên trong đều tự xử lý đúng.

Với content-box, width đặt cho phần nội dung; padding/border cộng thêm ra ngoài.
Trước sửa một hộp bị tràn, xem box model trong DevTools thay vì giảm font ngẫu nhiên.

## 6. Block trước, flex sau

HTML cho thử hai mục:

```html
<section class="row">
  <div class="item">An</div>
  <div class="item">Bình</div>
</section>
```

div/section ở ví dụ thường là các hộp block, xếp theo dòng khối. Thêm CSS:

```css
.row {
  display: flex;
  flex-direction: row;
  gap: 12px;
}
```

display:flex đặt cách bố trí **các con trực tiếp** của row. Direction row xếp
theo trục hàng, column xếp theo trục cột. Gap tách các con; padding của row
tạo đệm quanh cả nhóm. Đổi từng thuộc tính trong lab để nhìn rõ trách nhiệm.

## 7. Căn theo trục: đừng thuộc “center là ở giữa” chung chung

```css
.row {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
}
```

Với row, trục chính theo hàng: justify-content phân bố trên trục này; align-items
căn trên trục còn lại. Khi đổi thành column, ý nghĩa trục quay theo direction.
Không thấy space-between khác? Kiểm container có phần không gian dư để phân bố.
Không suy ra rằng cứ thêm align-items:center là căn toàn trang vào giữa.

## 8. Khi nhiều luật cùng nhắm một chữ

```css
p { color: black; }
.card p { color: green; }
```

P trong card nhận màu xanh vì selector .card p có độ ưu tiên cao hơn trong
ví dụ cùng nguồn/layer bình thường này. Khi mức ưu tiên tương đương, thứ tự
có thể quyết định. Ngoài đời còn có layer, important và inheritance; đừng lấy
hai dòng này thành quy tắc “luật ở cuối luôn thắng”.

Trong Elements chọn đúng p, xem Styles luật nào bị gạch và Computed màu cuối.
Đây là cách tra nguyên nhân, không thêm !important liên tục để ép cho xong.

## 9. Responsive: quy tắc theo không gian còn lại

```css
.row { display: flex; gap: 12px; }
@media (max-width: 600px) {
  .row { flex-direction: column; }
}
```

@media đặt điều kiện để áp nhóm luật bên trong. Trong ví dụ, khi viewport không
quá600px, các con xếp cột. CSS pixel/viewport không đồng nghĩa số inch màn hình.
Thử kéo browser, text dài và zoom; không chỉ chọn một tên điện thoại.

## 10. Tailwind và JSX học sau CSS cơ bản

`p-4`, `flex`, `gap-3` là tên utility để sinh CSS theo cấu hình Tailwind. Đừng
học chúng như một ngôn ngữ trình bày tách khỏi padding/display/gap.

Trong HTML dùng class. Trong JSX của React dùng className để chỉ CSS class.
`className="..."` không phải cú pháp class Python; đó là thuộc tính của phần
tử UI. Học chương03 rồi React sau khi tự dựng được hộp/form cơ bản.

## 11. Bài tự dựng từ trang trắng

Làm card có tiêu đề, đoạn mô tả và hai nút. Tạo HTML trước, rồi CSS theo thứ tự:
màu/viền → padding → sắp hai nút bằng flex/gap → màn hẹp đổi cột. Mỗi bước
đổi một thuộc tính và giải thích bằng lời nó tác động lên cha hay con.

Thử xóa dấu chấm selector, đổi tên class lệch nhau, sai đường dẫn stylesheet
và chuỗi tiêu đề dài. Dùng Elements/Computed tìm chỗ sai. Nộp HTML/CSS tự viết
và một ảnh ở màn rộng/hẹp; nút demo chưa nối API phải ghi rõ.

Nguồn tra khi cần: [MDN HTML](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Structuring_content),
[CSS box model](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Box_model/Introduction),
[Flexbox](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_flexible_box_layout/Basic_concepts_of_flexbox).
