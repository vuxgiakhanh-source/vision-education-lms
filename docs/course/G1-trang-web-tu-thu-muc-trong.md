# G1 — Tự viết một trang web từ thư mục trống

Mày biết biến/if/for/hàm Python; đã làm phần JavaScript của F0 và biết cách tra
một API ở F2. Giờ ta dựng **Sổ lớp học**: nhập tên → thêm vào danh sách → tìm
theo tên. Tám buổi nhỏ dưới đây tạo cùng một sản phẩm. Mỗi buổi kết thúc bằng
một thứ nhìn được, giải thích được và một lỗi tự sửa. Chưa cần TypeScript/React.

Source cuối ở [vanilla](studio/frontend/vanilla/index.html) để đối chiếu **sau
khi tự làm từng bước**. Không dán toàn bộ source cuối rồi đánh dấu đã học.
Dữ liệu chỉ ở RAM: refresh mất lớp là hành vi đã chọn của bài này. Server Python
phía dưới chỉ đưa file cho browser, chưa phải backend nghiệp vụ hay database.

## Buổi 1 — Từ câu yêu cầu đến ba việc và file đầu tiên

Yêu cầu ban đầu: “Tao muốn ghi lại mấy lớp rồi tìm nhanh”. Tao chưa chọn thư
viện. Tao hỏi dữ liệu nào cần giữ: mỗi lớp có **id** để nhận diện và **title**
để hiển thị. Người dùng làm ba việc: xem, thêm, tìm. Tìm chỉ đổi phần đang nhìn,
không được xóa dữ liệu đã nhập. Tên trống phải báo lỗi. Bài này cho phép tên
trùng; hai lớp trùng tên có hai id khác nhau. Chưa có đăng nhập/lưu lâu dài.

Viết lại thành kiểm tra bằng tay trước khi code:

| Thao tác | Điều phải thấy |
|---|---|
| Mở lần đầu | Chưa có lớp và lời mời thêm |
| Thêm `  Toán 10A  ` | Một lớp tên `Toán 10A`, mã 1 |
| Thêm tên chỉ có khoảng trắng | Có lỗi, số lớp không tăng |
| Tìm `toán` rồi xóa query | Chỉ hiện lớp khớp, rồi hiện lại tất cả |
| Refresh | Trở về danh sách rỗng theo phạm vi bài |

Mở PowerShell. Các lệnh sau tạo **repo học riêng**, chỉ chạy lần đầu. Nếu đã
có thư mục, đi vào và đọc file của mày; không chạy lại lệnh tạo file để ghi đè.

```powershell
Set-Location D:\
New-Item -ItemType Directory -Name so-lop-hoc
Set-Location D:\so-lop-hoc
New-Item -ItemType File -Name index.html
Get-Location
```

Kết quả cuối phải là `D:\so-lop-hoc`. Nếu `Access denied`, tạo thư mục học ở
nơi tài khoản được phép và thay đường dẫn trong những buổi sau. `New-Item`
tạo file/thư mục; nó chưa viết HTML. Mở `index.html` trong editor và tự gõ:

```html
<!doctype html>
<html lang="vi">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Sổ lớp học</title>
  </head>
  <body>
    <main>
      <h1>Sổ lớp học</h1>
      <p>Chưa có lớp. Mình sẽ thêm chức năng sau.</p>
    </main>
  </body>
</html>
```

Python có lệnh chạy; HTML có cây phần tử. `main` chứa nội dung chính, `h1` là
tiêu đề chính, `p` là đoạn văn. `head` chứa thông tin và tài nguyên của trang.
Thuộc tính `lang` mô tả ngôn ngữ. Dấu `</main>` đóng đúng phần tử đã mở.

Chạy từ **D:\so-lop-hoc**:

```powershell
python -m http.server 8018 --bind 127.0.0.1
```

Mở `http://127.0.0.1:8018`. Phải thấy tiêu đề và đoạn văn. Terminal giữ process
server là bình thường; Ctrl+C dừng nó. Mỗi lần sửa, lưu file rồi refresh browser.
Nếu thấy danh sách file hoặc nội dung khác, kiểm `Get-Location` và URL; nếu lỗi
“address already in use”, dừng server học cũ hoặc chọn cổng khác và đổi cả URL.
Chưa thấy chữ thì chưa thêm CSS. Bằng chứng: tự đổi tên tiêu đề và nói được
browser lấy file nào từ thư mục nào. Xem F1 mục1 nếu còn lẫn thẻ/thuộc tính.

## Buổi 2 — Một card: hiểu từng luật CSS trước khi làm layout

Ở buổi1, cấu trúc đủ để đọc. Muốn card có nền/viền/khoảng đệm, ta giữ nội dung
HTML và thêm quy tắc trình bày. Tạo `style.css` trong **D:\so-lop-hoc**, thêm
trong `head` sau `title`:

```html
<link rel="stylesheet" href="./style.css">
```

Đổi `main` thành `<main class="page">`; bên trong giữ h1 rồi thay đoạn p bằng:

```html
<section class="panel">
  <h2>Thêm lớp</h2>
  <p>Tên lớp sẽ được nhập ở đây.</p>
</section>
```

Viết đầy đủ CSS đầu tiên:

```css
* { box-sizing: border-box; }
body { margin: 0; font-family: system-ui, sans-serif; background: #eef3ef; color: #20362a; }
.page { max-width: 56rem; margin-inline: auto; padding: 24px; }
.panel { margin-top: 24px; padding: 20px; border: 1px solid #c8d7cd; background: white; }
```

Đọc `.panel`: chọn phần tử có `class="panel"`. Giữa `{}` là các khai báo
`thuộc-tính: giá-trị;`. `padding` tạo khoảng bên trong viền; `margin-top` tạo
khoảng bên ngoài phía trên; `border` viết gọn độ dày, kiểu nét, màu. `*` chọn
mọi phần tử; border-box tính padding/border vào width thay vì cộng ra ngoài.
`56rem` dựa trên cỡ chữ gốc; `max-width` là giới hạn, không ép rộng cố định.
`margin-inline:auto` chia khoảng dư hai bên. `system-ui` dùng font hệ thống.

Vẫn chạy server buổi1 ở cùng CWD; lưu cả hai file, refresh cùng URL. Phải thấy
card trắng có viền. Nếu chỉ có chữ trần, F12 → Network → refresh → chọn
`style.css`: status phải200. 404 nghĩa đường dẫn/tên sai. Trong Elements chọn
section → Styles: phải thấy `.panel`; bỏ dấu chấm sẽ đổi thành chọn thẻ panel.

**Điền:** giữ padding20px, đổi margin-top thành40px rồi mô tả thứ gì di chuyển.
Sau đó đặt margin lại24px và padding thành40px. Không thay hai giá trị cùng lúc.

<details><summary>Đối chiếu sau khi thử</summary>

Margin40px đẩy cả card xa nội dung trước nó; padding40px đẩy chữ xa viền của
chính card. Dùng box model trong Elements để đọc hai khoảng khác nhau. Nếu
không thấy đổi, kiểm file đã lưu và rule nào đang thắng trước khi tăng tiếp.

</details>

Qua buổi khi tự gõ lại `.panel` và chỉ được selector/property/value. Không phải
thuộc tên màu. Nếu tính kích thước còn rối, mở F1 mục4–5 đúng lúc này.

## Buổi 3 — Toolbar: HTML giữ ý nghĩa, flex bố trí các con

Ta cần ô nhập có label và nút. Hai thứ thuộc cùng hành động thêm lớp nên ở
chung form. Trong panel, giữ h2; thay đoạn p bằng:

```html
<form id="create-form" novalidate>
  <label for="class-title">Tên lớp</label>
  <div class="toolbar">
    <input id="class-title" name="title">
    <button type="submit">Thêm lớp</button>
  </div>
  <p id="title-error" role="alert"></p>
</form>
```

`for` của label khớp `id` input, nên bấm label đưa focus vào ô. `name` là tên
field khi form được gửi/serialize; `id` nhận diện phần tử ở trang. `novalidate`
tạm để JS của ta tự hiển thị lỗi đã định, chưa có chức năng đó ở buổi này.
Nút submit còn có thể làm trang reload; đó là hành vi mặc định, sửa ở buổi5.

Thêm lần lượt vào CSS, refresh sau từng nhóm:

```css
label { display: block; margin-bottom: 6px; }
input, button { font: inherit; padding: 10px 12px; }
input { min-width: 0; width: 100%; }
.toolbar { display: flex; gap: 12px; align-items: start; }
.toolbar input { flex: 1; }
.toolbar button { flex-shrink: 0; }
```

`label` block chiếm dòng riêng. `.toolbar` là **cha flex**; input và button là
hai con trực tiếp. `gap12px` đặt khoảng giữa chúng. `flex:1` cho input nhận
không gian còn lại; `flex-shrink:0` giữ nút không bị co ngang. `min-width:0`
cho input được co khi không gian hẹp. Các giá trị này có lý do riêng, không
phải cả bộ “thần chú căn hàng”. `font:inherit` dùng font từ phần tử cha.

CWD/server vẫn như buổi1; sau refresh phải thấy label trên, input và nút cùng
hàng. Thử Tab: phải đi tới input rồi nút. Trong Elements bật/tắt display:flex:
thứ thay đổi là cách các con xếp, nội dung không bị viết lại.

**Điền:** thử đặt `padding:12px` lên toolbar và bỏ gap. Hai input/nút còn cách
nhau như trước không? Sau khi quan sát khôi phục gap. Nếu nút tràn ở màn hẹp,
ghi lỗi này; buổi4 sẽ thêm quy tắc theo độ rộng, chưa ép font nhỏ để giấu nó.

## Buổi 4 — Danh sách card rồi mới responsive

Thêm section thứ hai **sau section thêm lớp**, vẫn trong main:

```html
<section class="panel">
  <h2>Các lớp của mình</h2>
  <label for="class-query">Tìm theo tên lớp</label>
  <input id="class-query" type="search" name="query">
  <p id="summary">Hiện 2 / 2 lớp</p>
  <ul id="class-list" class="class-list">
    <li class="class-card"><h3>Toán 10A</h3><p>Mã lớp: 1</p></li>
    <li class="class-card"><h3>Văn 10B</h3><p>Mã lớp: 2</p></li>
  </ul>
  <p id="empty-message"></p>
</section>
```

Đây là **fixture hiển thị**, chưa có dữ liệu JS. `ul/li` nói đây là danh sách;
h3 nằm dưới h2, không chọn heading theo cỡ chữ. Thêm CSS:

```css
.class-list { list-style: none; padding: 0; display: flex; flex-wrap: wrap; gap: 12px; }
.class-card { flex: 1 1 240px; min-width: 0; padding: 16px; background: #f3f8f4; border: 1px solid #c8d7cd; }
.class-card h3 { overflow-wrap: anywhere; }
@media (max-width: 600px) {
  .page { padding: 16px; }
  .toolbar { flex-direction: column; }
  .toolbar button { width: 100%; }
}
```

`flex-wrap:wrap` cho card xuống dòng. `flex:1 1 240px` lần lượt là có thể lớn
ra, có thể co lại, kích thước cơ sở240px. Đây không phải width tối thiểu240px.
`overflow-wrap:anywhere` cho từ rất dài ngắt khi cần, không cắt mất chữ.
`@media` chỉ áp nhóm rule khi viewport không quá600 CSSpx. Đổi toolbar sang
column thì trục chính chuyển dọc; không cần viết HTML thứ hai cho điện thoại.

Lưu/refresh tại URL đang chạy. Kéo browser rộng rồi hẹp; ở320px input/nút phải
xếp cột, card vẫn đọc được. Thay tên một lớp bằng một chuỗi không có khoảng
trắng rất dài rồi thử zoom200%. F12 → Elements → Computed đọc width thực tế.
Đừng thêm overflow:hidden để che chữ tràn.

**Điền:** cho card nền khác mà không đổi nền panel. **Tự dựng:** thêm card thứ
ba tên của mày, giữ bố cục tự xuống dòng. **Tự sửa lỗi:** cố ý gõ
`class="class-listt"`, đoán rule nào mất rồi dùng Styles tìm lại. Bằng chứng
buổi này là HTML/CSS tự gõ và hai ảnh rộng/hẹp cùng giải thích cha/con.

## Buổi 5 — JavaScript nhận event: máy chưa tự biết nút phải làm gì

Tạo `app.js` cạnh HTML và CSS. Cuối body, trước `</body>`, thêm:

```html
<script type="module" src="./app.js"></script>
```

HTML yêu cầu browser tải file JS; `type="module"` cho phép import/export khi
ta cần ở buổi8. Chạy qua HTTP server để module được tải đúng; đừng mở file
bằng URL `file:///`. Trong app.js viết một hành vi nhỏ trước:

```javascript
const form = document.querySelector('#create-form');
const input = document.querySelector('#class-title');
const error = document.querySelector('#title-error');
if (!form || !input || !error) throw new Error('Kiểm tra id của form/input/error');

function handleSubmit(event) {
  event.preventDefault();
  error.textContent = `Mày vừa nhập: ${input.value}`;
}
form.addEventListener('submit', handleSubmit);
```

Đọc theo thứ tự: `document` là tài liệu browser đang giữ; `querySelector`
nhận chuỗi selector, trả phần tử đầu khớp hoặc null. `#class-title` chọn id.
`if` dừng sớm để báo lỗi dễ hiểu khi HTML không khớp. `addEventListener` nhận
tên event và một **hàm**, chưa gọi hàm ngay. Browser gọi nó khi submit và đưa
event vào tham số. `preventDefault()` chặn gửi form/navigation mặc định.
`input.value` đọc chữ; `textContent` đặt chữ. Template string dùng dấu backtick
và `${...}` để đưa giá trị vào chuỗi; không phải chuỗi nháy đơn.

Lưu/refresh rồi gõ tên và Enter: URL không đổi, dưới form có chữ vừa nhập.
F12 → Console phải không có lỗi. Cố ý đổi selector thành `#class-titl`: phải
gặp lỗi mình đặt. Sửa id lại. Nếu nút làm reload, kiểm script404 hoặc lỗi JS
xảy ra trước khi listener được đăng ký. Không sửa CSS để chữa lỗi event.

**Điền:** thêm `.trim()` sau input.value, thử khoảng trắng đầu/cuối. Nói rõ
trim trả chuỗi mới, chưa sửa ô nhập. Tới đây mới có event và chữ, chưa thêm
lớp thật vào danh sách. Xem F2 mục3 và6 để đọc hợp đồng API tương tự.

## Buổi 6 — Dữ liệu trước, render sau: một nguồn để dựng danh sách

Danh sách HTML fixture có thể nhìn được nhưng JS chưa quản lý nó. Ta cần array
với object, gần list/dict Python. **Thay toàn bộ nội dung app.js của buổi5**
bằng đoạn dưới; chưa thêm form handler ở bước này:

```javascript
const list = document.querySelector('#class-list');
const summary = document.querySelector('#summary');
if (!list || !summary) throw new Error('Kiểm tra id của list/summary');
let classes = [
  { id: 1, title: 'Toán 10A' },
  { id: 2, title: 'Văn 10B' },
];

function render() {
  list.replaceChildren();
  for (const classroom of classes) {
    const item = document.createElement('li');
    item.className = 'class-card';
    const title = document.createElement('h3');
    title.textContent = classroom.title;
    const description = document.createElement('p');
    description.textContent = `Mã lớp: ${classroom.id}`;
    item.append(title, description);
    list.append(item);
  }
  summary.textContent = `Hiện ${classes.length} / ${classes.length} lớp`;
}
render();
```

Xóa hai li fixture ở HTML, giữ ul rỗng. Tao làm vậy vì từ giờ **classes là
nguồn dữ liệu**, HTML được dựng từ nó. Không giữ cả danh sách hard-code và
danh sách JS rồi không biết sửa bản nào. `createElement` tạo node chưa gắn
vào trang; `append` gắn các node con; `className` đặt class; `replaceChildren`
xóa node con cũ để render lại không bị nhân đôi. `textContent` xem tên là chữ,
nên tên giống thẻ HTML vẫn hiển thị như chữ, không tự chạy markup người nhập.

| Lượt | classroom | Node tạo ra | Số li trong list |
|---|---|---|---|
| Trước for | Chưa có | replaceChildren làm rỗng | 0 |
| 1 | `{id:1,title:'Toán 10A'}` | li chứa h3/p | 1 |
| 2 | `{id:2,title:'Văn 10B'}` | li chứa h3/p | 2 |

Lưu/refresh; vẫn thấy hai card dù HTML không còn hai li. Trong app.js đổi
classes thành `[]`, refresh: danh sách rỗng, summary0/0. Đây là biến trong JS,
không phải SQL. Thêm lại object của mày rồi giải thích một vòng render từ
array tới DOM. **Điền:** bỏ replaceChildren và gọi render hai lần; đoán/trực
tiếp thấy nhân đôi. Khôi phục trước khi sang bước tiếp.

## Buổi 7 — Tạo và tìm lớp, mỗi hành động chỉ đổi dữ liệu cần đổi

Giữ render buổi6. Đổi classes thành `[]` và thêm `let nextId = 1;`. Ở đầu
app.js lấy thêm bốn phần tử; giữ kiểm tra null cho cả chúng:

```javascript
const form = document.querySelector('#create-form');
const titleInput = document.querySelector('#class-title');
const queryInput = document.querySelector('#class-query');
const error = document.querySelector('#title-error');
const empty = document.querySelector('#empty-message');
if (!form || !titleInput || !queryInput || !error || !empty) {
  throw new Error('Kiểm tra các id form/title/query/error/empty');
}
```

Thêm hàm pure dưới khai báo dữ liệu. Pure ở đây là chỉ nhận/trả dữ liệu, không
đụng DOM hoặc đổi array gốc; ta có thể thử nó mà không bấm browser:

```javascript
function findClasses(classes, query) {
  const normalized = query.trim().toLowerCase();
  const result = [];
  for (const classroom of classes) {
    if (classroom.title.toLowerCase().includes(normalized)) result.push(classroom);
  }
  return result;
}
```

`toLowerCase` trả chuỗi chữ thường; `includes` hỏi chuỗi con có xuất hiện
không; `push` thêm cuối array. Query rỗng khớp mọi tên theo hợp đồng includes.
Hàm vẫn giữ nguyên dấu tiếng Việt, chưa có tìm kiếm bỏ dấu. Thay phần đầu
render thành `const visible = findClasses(classes, queryInput.value);`, rồi
replaceChildren; vòng for duyệt visible thay classes. Đổi summary và thêm
empty-message ở cuối render:

```javascript
summary.textContent = `Hiện ${visible.length} / ${classes.length} lớp`;
if (classes.length === 0) empty.textContent = 'Chưa có lớp. Thêm lớp đầu tiên ở trên.';
else if (visible.length === 0) empty.textContent = 'Không có lớp khớp từ tìm kiếm.';
else empty.textContent = '';
```

Thêm handler trước lời gọi render cuối file:

```javascript
function handleSubmit(event) {
  event.preventDefault();
  const title = titleInput.value.trim();
  if (title.length === 0) { error.textContent = 'Nhập tên lớp.'; return; }
  if (title.length > 100) { error.textContent = 'Tên lớp tối đa 100 ký tự JS.'; return; }
  error.textContent = '';
  classes.push({ id: nextId, title });
  nextId = nextId + 1;
  titleInput.value = '';
  render();
}
form.addEventListener('submit', handleSubmit);
queryInput.addEventListener('input', render);
```

`{id:nextId,title}` là viết gọn `{id:nextId,title:title}`; chưa có class OOP.
Submit đổi **dữ liệu gốc**, rồi render. Input tìm kiếm chỉ gọi render theo
query mới, không gán classes bằng kết quả tìm kiếm. Nếu gán
`classes = findClasses(classes, query)`, xóa query cũng không cứu lớp đã mất.
Id tăng trong tab, không phải id DB. `string.length` đếm đơn vị UTF-16; giới
hạn100 ở đây là quy ước JS tạm, không thay hợp đồng code point ở xưởng backend.

Lưu/refresh, chạy lại bảng buổi1; thêm lớp khi query không khớp thì tổng tăng
nhưng lớp bị bộ lọc ẩn. Xóa query để thấy lại. **Điền:** thêm `aria-invalid`
đúng/sai theo lỗi bằng setAttribute; gợi ý ở reference. **Tự sửa lỗi:** cố ý
bỏ preventDefault rồi quan sát reload làm dữ liệu RAM biến mất, sau đó sửa.
Chỉ qua buổi khi tự giải thích được từng thay đổi classes/nextId/query/DOM.

## Buổi 8 — Tách file vì trách nhiệm, rồi tự thêm một tính năng

Tới đây một app.js vẫn dùng được. Ta có lý do tách: `findClasses` và kiểm tên
không cần document; phần còn lại lấy input và cập nhật DOM. Chưa cần service,
repository hay năm tầng class cho trang RAM nhỏ này. Tạo data.js và chuyển
findClasses sang đó, thêm export trước function. Tách kiểm tên thành:

```javascript
export function titleError(title) {
  if (title.length === 0) return 'Nhập tên lớp.';
  if (title.length > 100) return 'Tên lớp tối đa 100 ký tự JS.';
  return '';
}
```

Trong app.js thêm dòng đầu:

```javascript
import { findClasses, titleError } from './data.js';
```

Xóa định nghĩa findClasses cũ để không trùng tên. Handler gọi titleError(title),
hiện message, return khi message khác rỗng; logic thêm lớp giữ nguyên. Named
export mở tên cho file khác; named import phải đúng tên. `./` tính từ app.js;
browser JS module dùng đường dẫn có đuôi `.js`. Import không gọi findClasses,
chỉ lấy hàm để lúc render mới gọi. Browser bắt đầu ở index.html → app.js →
data.js; data.js không import ngược app.js.

```text
so-lop-hoc/
  index.html     cấu trúc, id và file entry
  style.css      trình bày và responsive
  app.js         event, dữ liệu RAM, dựng DOM
  data.js        tìm kiếm và quy tắc tên, không phụ thuộc DOM
```

Lưu/refresh vẫn phải qua bảng kiểm buổi1. Trong Network thấy app.js và data.js
đều200. Cố ý ghi sai tên export để thấy lỗi “does not provide an export”; sai
đường dẫn tạo404. Mở đúng file/chính tả để sửa, không cài thêm package.
Source cuối bổ sung status, aria-invalid, style focus và null guard đầy đủ:
[app.js](studio/frontend/vanilla/app.js), [data.js](studio/frontend/vanilla/data.js),
[HTML](studio/frontend/vanilla/index.html), [CSS](studio/frontend/vanilla/style.css).
Đối chiếu chỗ khác nhau và nói vì sao thêm, đừng chép lại không hiểu.

**Đề mới:** thêm nút “Xóa” cho mỗi card. Xóa đúng id; hai lớp cùng tên không
xóa nhầm nhau. Tìm kiếm vẫn giữ được dữ liệu của các lớp còn lại. Tự viết
thuật toán bằng lời và làm trước khi mở dưới đây.

<details><summary>Lời giải và cách ghép sau khi đã thử</summary>

Thêm vào data.js:

```javascript
export function removeClass(classes, id) {
  const result = [];
  for (const classroom of classes) {
    if (classroom.id !== id) result.push(classroom);
  }
  return result;
}
```

Import thêm removeClass ở dòng import hiện có của app.js. Trong vòng for của
render, **sau** khi có item/title/description, **trước** list.append(item), thêm:

```javascript
const removeButton = document.createElement('button');
removeButton.type = 'button';
removeButton.textContent = 'Xóa';
removeButton.addEventListener('click', function () {
  classes = removeClass(classes, classroom.id);
  render();
});
item.append(removeButton);
```

Callback giữ id của classroom ở lượt tạo card, chỉ xóa khi click. Duyệt lấy
các id khác thành array mới; không lấy title làm khóa. Đây là tính năng mới,
nên có thêm kiểm: tạo hai tên trùng, xóa một, tổng giảm một; xóa lúc tìm;
xóa hết; refresh. Thử bàn phím sau xóa: focus của nút bị xóa cần thiết kế
tiếp nếu thành sản phẩm; không khẳng định đầy đủ accessibility chỉ từ giao
diện này. Không cần viết một repository để xóa array trong RAM.

</details>

Kết buổi bằng cách đóng lời giải, tự thêm hai lớp khác và vẽ đường
submit → đọc input → kiểm tên → thêm array → render → DOM. Giải thích nơi
đặt tính năng xóa và vì sao. Nếu còn phải hỏi đặt mỗi dòng ở đâu, quay lại
buổi tương ứng và làm biến thể; G2 sẽ dùng lại chính luồng này với React.

Nguồn khi cần tra tiếp: [MDN JavaScript modules](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules),
[MDN DOM](https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model/Introduction).
