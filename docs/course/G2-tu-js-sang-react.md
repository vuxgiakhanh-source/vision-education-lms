# G2 — Giữ bài toán đã hiểu, chuyển từng bước sang TypeScript và React

Học sau khi tự thêm/tìm lớp bằng DOM ở G1. Vẫn **Sổ lớp học** với dữ liệu RAM,
chưa gọi mạng. Tám buổi này không tăng độ khó nghiệp vụ; ta chỉ đổi cách mô
tả kiểu và quản lý giao diện. Nếu JS ở G1 còn chưa tự viết được, sửa phần đó
trước khi học thư viện mới. F0 mục8–10 lúc này mới cần dùng để học TypeScript.

Reference cuối: [App.tsx](studio/frontend/react/App.tsx),
[ClassList.tsx](studio/frontend/react/ClassList.tsx),
[data.ts](studio/frontend/react/data.ts). Mỗi file đi vào bài đúng lúc có lý do;
chưa dùng Axios/Zod/RHF/router/hook tự viết. Những công cụ đó học khi có nhu cầu
thật ở xưởng tiếp theo. Chạy được bản này chưa chứng minh hệ thống có DB/quyền.

## Buổi 1 — Tự tạo môi trường: biết từng file trước lệnh chạy

Với JS thường, browser đọc HTML/CSS/JS trực tiếp. Browser không tự hiểu type
annotation của TS hay JSX. **TypeScript** kiểm kiểu; **Vite** phục vụ và biến
đổi tài nguyên trong lúc dev, build file để phát hành; **React** mô tả UI;
**React DOM** gắn UI vào DOM browser. Node/npm chạy công cụ trên máy, không
thay browser. Không cần chọn stack mới, vì ta nối vào stack của giáo án.

Tạo thư mục mới để vẫn giữ G1 đối chiếu. PowerShell:

```powershell
Set-Location D:\
New-Item -ItemType Directory -Name so-lop-hoc-react
Set-Location D:\so-lop-hoc-react
node --version
npm --version
```

Nếu thư mục tồn tại, đọc nội dung trước khi làm tiếp. Nếu thiếu node/npm,
quay G0/công cụ phần cài môi trường; chưa sửa TS để chữa lỗi command not found.
Tạo **package.json** bằng editor, nguyên nội dung sau:

```json
{
  "name": "classroom-notebook-studio",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite --host 127.0.0.1 --port 5186 --strictPort",
    "build": "tsc --noEmit && vite build"
  },
  "dependencies": { "react": "19.3.1", "react-dom": "19.3.1" },
  "devDependencies": {
    "@types/react": "19.3.0",
    "@types/react-dom": "19.3.0",
    "typescript": "6.0.3",
    "vite": "8.3.4",
    "@vitejs/plugin-react": "6.1.2"
  }
}
```

Các số trên lấy từ **phiên bản thực tế được resolve** trong lockfile xưởng,
không suy từ dấu `^` trong manifest. Gói học chỉ giữ thứ đang dùng. `private`
chặn vô ý publish package; `type:module` dùng module ESM. Scripts đặt tên cho
lệnh; `npm run build` thực hiện tsc trước, thành công mới chạy vite vì có `&&`.
Các @types cung cấp mô tả kiểu của thư viện. JSON dùng nháy kép, không có
comment/trailing comma. Đây là file cấu hình, chưa có component nào chạy.

Tạo **tsconfig.json**, dùng compiler options của xưởng:

```json
{
  "compilerOptions": {
    "target": "ES2023", "lib": ["ES2023", "DOM"], "module": "ESNext",
    "moduleResolution": "bundler", "jsx": "react-jsx", "strict": true,
    "skipLibCheck": true, "noEmit": true, "esModuleInterop": true
  },
  "include": ["*.ts", "*.tsx"]
}
```

`include` chọn các file để kiểm; DOM cung cấp kiểu API browser; jsx cho cách
xử lý JSX; strict bật kiểm kiểu chặt. noEmit để bước TS không xuất JS riêng
trước bước Vite. skipLibCheck bỏ kiểm nội bộ file khai báo thư viện, không tắt
kiểm code của mày. Chưa cần thuộc mọi option; phải biết đây là cấu hình cho
compiler và biết source nào đang được kiểm, không phải dữ liệu runtime.

Tạo **vite.config.ts**:

```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
export default defineConfig({ plugins: [react()] });
```

defineConfig là helper cấu hình; plugin-react xử lý tích hợp React của Vite.
Đây là code công cụ chạy trong môi trường Node, không phải component browser.
`export default` là export mặc định của module cấu hình, khác named export
ở data.js G1. Tạo **assets.d.ts** ghi `declare module '*.css';`: dòng khai báo
cho compiler nhận import CSS; nó không tự áp CSS lên trang.

Cài trong **D:\so-lop-hoc-react**:

```powershell
Get-Location
npm install
npm run
```

Lần cài đầu cần mạng; kết quả có node_modules và package-lock.json. Đọc scripts
thấy dev/build đúng manifest này. Giữ package-lock của repo học; lần dựng sạch
sau dùng npm ci. Không copy lock xưởng vào một package.json khác rồi mong khớp.

Tạo thêm **.gitignore** trong thư mục project, ghi hai dòng sau để khi dùng Git
không đưa dependency đã cài và bản build vào source history:

```text
node_modules/
dist/
```

Giữ package.json, package-lock.json, cấu hình và source trong lịch sử; các file
đó mô tả cách dựng lại dependency và bundle. G4 sẽ dẫn git init/status khi cần
so thay đổi và áp đáp án trên bản copy riêng. .gitignore không xóa file đã có.

Nếu npm báo JSON parse, sửa dấu/nháy ở file, không cài lại Node. Buổi này chưa
chạy dev vì entry HTML/component sẽ tạo ở buổi2.

## Buổi 2 — Đường chạy entry: HTML → main.tsx → component

Tạo **index.html**:

```html
<!doctype html>
<html lang="vi">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Sổ lớp học · React</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/main.tsx"></script>
  </body>
</html>
```

Tạo **App.tsx**:

```tsx
export function App() {
  return <main className="page">
    <h1>Sổ lớp học</h1>
    <p>Mình đang học cùng bài toán ở bản React.</p>
  </main>;
}
```

App vẫn là hàm. Thứ nó return là JSX mô tả giao diện. Tên component viết hoa
để `<App />` là component, còn `<main>` là phần tử HTML. `.tsx` cho phép viết
TS cùng JSX; `.ts` ở buổi3 chỉ có TS. `className` của JSX đóng vai trò class
HTML. Hai node nằm trong một main để hàm trả một cây. JSX không phải chuỗi
HTML: không bọc toàn bộ bằng nháy, không ghi if trực tiếp vào giữa thẻ.

Tạo **style.css** bằng cách giữ CSS G1. Có thể copy file mình đã tự viết:

```powershell
Copy-Item -LiteralPath D:\so-lop-hoc\style.css -Destination D:\so-lop-hoc-react\style.css
```

Tạo **main.tsx**:

```tsx
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { App } from './App';
import './style.css';

const root = document.getElementById('root');
if (!root) throw new Error('Không tìm thấy #root trong index.html');
createRoot(root).render(<StrictMode><App /></StrictMode>);
```

Đi từng dòng: import lấy API/component; CSS import yêu cầu Vite tải stylesheet.
getElementById tìm vùng gắn UI. Guard xử lý null. createRoot nhận node DOM và
trả root của React; render yêu cầu hiển thị cây App trong vùng đó. StrictMode
giúp phát hiện một số vấn đề trong lúc phát triển; không phải đăng nhập hoặc
validation nghiệp vụ. Tới đây **main.tsx lắp ứng dụng**, App.tsx mô tả màn hình.
Vite xử lý đường import TS không ghi đuôi theo config bundler, khác browser
module `.js` ở G1. Đừng bê quy tắc Node/browser/Vite qua nhau máy móc.

Trong **D:\so-lop-hoc-react**, chạy:

```powershell
npm run dev
```

Mở `http://127.0.0.1:5186`. Phải thấy h1 và câu của App. Terminal thứ hai tại
**cùng thư mục** chạy `npm run build`: phải qua kiểm kiểu và có dist. Nếu id
root sai, Console báo thông điệp mình đặt; sai import App sẽ báo không tìm
module/export. Chưa thấy h1 thì chưa thêm state. Đổi câu trong App rồi lưu,
quan sát dev server cập nhật. Đây là hot reload lúc dev, không phải save dữ
liệu lớp. Source entry tham chiếu: [main.tsx](studio/frontend/react/main.tsx).

## Buổi 3 — Thêm kiểu vào hàm JS đã hiểu

Tạo **data.ts**. Ta giữ thuật toán for/if ở G1 và chỉ mô tả hình dạng dữ liệu:

```typescript
export type Classroom = { id: number; title: string };

export function titleError(title: string): string {
  if (title.length === 0) return 'Nhập tên lớp.';
  if (title.length > 100) return 'Tên lớp tối đa 100 ký tự JS.';
  return '';
}

export function findClasses(classes: Classroom[], query: string): Classroom[] {
  const normalized = query.trim().toLowerCase();
  const result: Classroom[] = [];
  for (const classroom of classes) {
    if (classroom.title.toLowerCase().includes(normalized)) result.push(classroom);
  }
  return result;
}
```

So Python: tham số có thể có type hint; ở đây `title: string` yêu cầu chuỗi.
`: string` sau `)` mô tả kết quả. Classroom là **tên kiểu**, không phải object
lớp OOP hay bản ghi thật. Classroom[] là array các object đúng hình. Dấu `:`
trong type mô tả kiểu, trong `{id:1,title:'Toán'}` gán giá trị dữ liệu. Kiểu
bị xóa khi chạy; không tự đổi `'1'` thành1 và không kiểm JSON server cho mình.
Ta chưa nhận JSON nên runtime parser chưa có việc để làm ở bài này.

**Điền:** tạm thêm dòng dưới vào data.ts rồi chạy build ở terminal thứ hai:

```typescript
const wrongClass: Classroom = { id: '1', title: 'Toán' };
```

Compiler phải chỉ ra string không gán được cho number. Thay id bằng1 rồi
build phải qua; xóa dòng thử sau khi ghi lại lỗi. Nếu build vẫn xanh với id
chuỗi, kiểm đang chạy manifest nào và file có nằm trong include không.
Đừng dùng any hoặc ép as để im lỗi này. Bằng chứng: tự viết thêm hàm nhận
Classroom trả title rồi giải thích phần nào là giá trị/phần nào chỉ là kiểu.

<details><summary>Lời giải hàm nhỏ sau khi tự thử</summary>

```typescript
export function classTitle(classroom: Classroom): string {
  return classroom.title;
}
```

Không cần class, constructor hay generic cho hàm này. Sai field
`classroom.name` phải bị kiểm kiểu bắt được. Xem F0 mục8–10 nếu còn lẫn dấu kiểu.

</details>

## Buổi 4 — State: vì sao đổi biến chưa làm giao diện cập nhật

Ở G1 ta push dữ liệu rồi tự render. React cần một tín hiệu để biết phải gọi
component lại. Dữ liệu UI cần nhớ qua các lần render đặt vào **state**. Chưa
thêm form; trước hết có fixture và ô tìm. Thay App.tsx bằng bản nhỏ hoàn chỉnh:

```tsx
import { useState } from 'react';
import { findClasses } from './data';
import type { Classroom } from './data';

const fixture: Classroom[] = [
  { id: 1, title: 'Toán 10A' },
  { id: 2, title: 'Văn 10B' },
];

export function App() {
  const [query, setQuery] = useState('');
  const visible = findClasses(fixture, query);
  return <main className="page">
    <h1>Sổ lớp học</h1>
    <label htmlFor="class-query">Tìm theo tên lớp</label>
    <input id="class-query" value={query}
      onChange={event => setQuery(event.target.value)} />
    <p>Hiện {visible.length} / {fixture.length} lớp</p>
    <ul className="class-list">
      {visible.map(classroom => <li className="class-card" key={classroom.id}>
        <h3>{classroom.title}</h3>
      </li>)}
    </ul>
  </main>;
}
```

`useState('')` nhận giá trị ban đầu, trả cặp `[giá trị, hàm cập nhật]`; array
destructuring đặt tên query/setQuery cho hai mục. Đây là API hook của React,
không phải cú pháp mới để gán hai biến. Gọi hook ở đầu component, không trong
if/for. Setter yêu cầu lần render sau; không sửa ngay biến query trong handler
hiện tại. `value={query}` giữ ô nhập theo state; onChange đọc chữ mới và đặt
state, nên gọi là controlled input. `htmlFor` của JSX tương ứng for của label.

map gọi callback cho từng classroom và trả array li. `{...}` trong JSX đưa
biểu thức vào giao diện; không phải block của Python/JS. Callback này trả JSX,
khác callback G1 tạo DOM. key=id giúp React nhận diện từng item ổn định; không
dùng title vì tên có thể trùng. Render tính visible từ fixture/query, **không
cần state thứ hai cho visible**, cũng không cần useEffect để tìm local array.

Dev server vẫn chạy5186; build ở terminal thứ hai. Gõ `  tOÁn  ` phải còn một
card, xóa query thấy hai. Đổi `onChange={event => setQuery(event.target.value)}`
thành `onChange={() => {}}`: input value không đổi khi gõ. Khôi phục và giải
thích vì sao. Đừng querySelector/textContent để sửa vùng DOM React đang sở hữu.
Lúc này React đã thay phần render DOM thủ công, chưa thay nghiệp vụ tìm.

## Buổi 5 — Form tạo lớp: dữ liệu nào phải nhớ, thứ tự xử lý nào giữ đúng

Ta thêm form nhưng giữ cách nghĩ G1. Cần nhớ classes, id kế, title đang gõ,
query, error, thông báo. Mỗi dữ liệu có lý do hiển thị/nhớ riêng. Trong App,
thay fixture bằng state; xóa const fixture ngoài App. Thêm các import cần dùng:

```tsx
import { useState } from 'react';
import type { FormEvent } from 'react';
import type { Classroom } from './data';
import { findClasses, titleError } from './data';
```

Chỉ có một import useState, không thêm trùng dòng cũ. Đầu function App, đặt:

```tsx
const [classes, setClasses] = useState<Classroom[]>([]);
const [nextId, setNextId] = useState(1);
const [title, setTitle] = useState('');
const [query, setQuery] = useState('');
const [error, setError] = useState('');
const [notice, setNotice] = useState('');
const visible = findClasses(classes, query);
```

`useState<Classroom[]>([])`: đầu vào [] chưa có phần tử để suy ra hình dữ
liệu; phần `<Classroom[]>` nói state sẽ giữ array Classroom. Đây là lần dùng
generic đầu tiên ở bài: tham số **kiểu**, không phải thẻ JSX hay dữ liệu truyền
vào hàm. Mỗi lần App render, React trả lại state đã giữ; không reset thành[]
chỉ vì function chạy lại. Khi refresh cả ứng dụng khởi động lại nên state mất.

Trước return của App, thêm:

```tsx
function handleSubmit(event: FormEvent<HTMLFormElement>) {
  event.preventDefault();
  const normalized = title.trim();
  const message = titleError(normalized);
  setError(message);
  setNotice('');
  if (message !== '') return;
  const classroom = { id: nextId, title: normalized };
  setClasses(previous => [...previous, classroom]);
  setNextId(previous => previous + 1);
  setTitle('');
  setNotice(`Đã thêm lớp ${normalized}. Nếu đang tìm kiếm, lớp có thể bị bộ lọc ẩn.`);
}
```

`FormEvent<HTMLFormElement>` là kiểu event của form trong React; import type
chỉ phục vụ compiler. `preventDefault` vẫn chặn submit mặc định. Vì state
title giữ chữ nhập, không cần đọc DOM. `previous => [...previous,classroom]`
nhận state trước và trả **array mới** chứa mục cũ cộng mục mới; không dùng
classes.push rồi trả nguyên array. Updater phải tính dữ liệu thuần: không gọi
API hoặc tăng biến global trong đó. React có thể gọi updater thêm lần trong
StrictMode dev để kiểm tính thuần. `setTitle('')` làm input rỗng ở render kế.

Trong JSX, đặt form dưới h1, trước vùng tìm:

```tsx
<>
<form onSubmit={handleSubmit} noValidate>
  <label htmlFor="class-title">Tên lớp</label>
  <div className="toolbar">
    <input id="class-title" value={title}
      onChange={event => setTitle(event.target.value)}
      aria-invalid={error !== ''} aria-describedby="title-error" />
    <button type="submit">Thêm lớp</button>
  </div>
  <p id="title-error" role="alert">{error}</p>
</form>
<p role="status">{notice}</p>
</>
```

Đặt cả đoạn trong main đã có. Cặp <> và </> là Fragment: nhóm các node JSX
mà không tạo thêm thẻ DOM. Một biểu thức JSX cần một gốc bao ngoài; Fragment
giúp ghép form và thông báo thành một biểu thức. Trong summary thay
fixture.length bằng classes.length. Cuối main thêm hai nhánh:

```tsx
<>
{classes.length === 0 && <p>Chưa có lớp. Thêm lớp đầu tiên ở trên.</p>}
{classes.length > 0 && visible.length === 0 && <p>Không có lớp khớp từ tìm kiếm.</p>}
</>
```

Điều kiện boolean && JSX chỉ đưa nhánh phù hợp vào cây. Phân biệt chưa có
dữ liệu với có dữ liệu nhưng lọc rỗng. Build phải qua; dev phải thêm được hai
lớp như G1. Test lỗi tên trống, whitespace,100/101 đơn vị UTF-16, query không
khớp, tên giống HTML; thêm khi đang tìm phải tăng tổng dù card bị bộ lọc ẩn.
Nếu tổng tăng mà UI không đổi, kiểm có mutate state không; nếu render lặp,
kiểm đang truyền handleSubmit hay gọi ngay handleSubmit(...).

## Buổi 6 — Props và tách component: đưa dữ liệu xuống, để chủ dữ liệu quyết định

App hiện giữ dữ liệu và điều phối form/tìm. Đoạn list chỉ nhận các lớp để
trình bày; đó là lý do tách được. Chưa cần tách mỗi label thành một file.
Tạo **ClassList.tsx**:

```tsx
import type { Classroom } from './data';

export function ClassList({ items }: { items: Classroom[] }) {
  return <ul className="class-list">
    {items.map(classroom => <li className="class-card" key={classroom.id}>
      <h3>{classroom.title}</h3>
      <p>Mã lớp: {classroom.id}</p>
    </li>)}
  </ul>;
}
```

Đọc chữ ký từng phần. React đưa object props vào hàm. `{items}` là
destructuring object để lấy field items; phần `: {items:Classroom[]}` mô tả
kiểu của **cả object props**, không tạo dữ liệu. Có thể viết dài hơn để hiểu:

```tsx
import type { Classroom } from './data';
export function ClassListLong(props: { items: Classroom[] }) {
  const items = props.items;
  return <p>{items.length} lớp được truyền từ cha</p>;
}
```

Hai cách minh họa độc lập; không thay reference list bằng component Long nếu
muốn giữ card. Trong App import ClassList rồi thay **toàn bộ ul cũ** bằng:

```tsx
<ClassList items={visible} />
```

App sở hữu classes/query nên tính visible và truyền xuống. Con không có bản
sao state của items; cha đổi props thì con mô tả lại list. data.ts không import
React/App; ClassList chỉ import kiểu; App import các phần cần dùng; main lắp
App. Cây file được suy ra từ trách nhiệm đang có, không bắt đầu bằng đoán tên
folder “chuẩn enterprise”. Khi nhiều màn/mô-đun xuất hiện, G3 mới xét ranh giới
lớn hơn. Source cuối thêm panel, help text và focus CSS, không đổi nghiệp vụ.

Lưu/refresh/build: hành vi phải giữ như buổi5. Cố ý gọi `<ClassList />` thiếu
items: TS phải báo lỗi props; truyền `items={query}` cũng sai kiểu. Khôi phục
và nói được dữ liệu gốc nằm ở đâu. Chụp sơ đồ main → App → ClassList cùng
data.ts, mỗi mũi tên ghi là import hay props; hai quan hệ không đồng nghĩa.

## Buổi 7 — Tự tìm lỗi, kiểm từng tầng trước khi thêm thư viện

CWD là **D:\so-lop-hoc-react**; terminal1 chạy dev, terminal2 chạy build. Dùng
bản cuối [reference](studio/frontend/react/App.tsx) chỉ để đối chiếu sau khi
tự khoanh lỗi. Thử mỗi lỗi trong repo học rồi sửa trước khi chuyển lỗi tiếp:

| Lỗi cố ý | Bằng chứng cần xem | Sửa nguyên nhân |
|---|---|---|
| import `./ClasList` | Terminal/overlay module not found | Đúng đường dẫn và tên file |
| Bỏ onChange nhưng giữ value | Input không nhận chữ; Console có thể nhắc | Nối state setter qua event |
| Push vào classes, không gọi setter | Dữ liệu JS đổi, UI không được yêu cầu render | Trả array mới bằng setter |
| Dùng title làm key, thêm tên trùng | Console key trùng, nhận diện item không tin cậy | Dùng id ổn định |
| Sai className | UI chạy nhưng style không khớp | Elements/Styles, sửa selector/class |
| Refresh mất lớp | State tạo lại theo initial[] | Đúng giới hạn RAM; DB là bài sau |

Đừng thêm useEffect để đồng bộ visible với classes/query: visible đã tính
được ngay từ hai đầu vào đó. Đừng thêm localStorage để “sửa” refresh trước
khi chốt yêu cầu lưu: nó không tạo tài khoản/quyền hay chia sẻ giữa nhiều máy.
Đừng dùng any/ts-ignore để bỏ lỗi import/props. Các lỗi khác tầng có công cụ
quan sát khác nhau: compiler cho kiểu, Console cho runtime, Elements cho CSS.

**Điền:** lỗi tên quá dài phải giữ nguyên nội dung input để người dùng sửa.
Đã làm được chưa? **Tự sửa:** nếu form xóa title trước khi validate, trả việc
xóa về sau thành công. **Đề trắng:** đóng mẫu, từ HTML root tự viết lại ô tìm
và list hai lớp fixture với state/props trong một buổi; đổi tên class/type tùy
mày nhưng giữ hợp đồng. Có thể tra docs, chưa nhờ AI sinh nguyên component.

**Bằng chứng qua buổi:** một lỗi có bước tái hiện → giả thuyết → nơi quan sát →
diff sửa → kiểm lại trường hợp đúng. Test/build source tham chiếu của người
viết sách không chấm được code mày tự viết. Nếu chưa tự khoanh được lỗi, dừng
một bước nhỏ và hỏi giải thích API cụ thể bằng phiếu F2, không mở cả đồ án.

## Buổi 8 — Một yêu cầu mới để kiểm khả năng tự phân chia

Yêu cầu: mỗi card có nút “Xóa”. Cha sở hữu classes, con trình bày card; vậy
ai được sửa classes? Mày phải trả lời và vẽ đường event trước khi viết. Đề
thêm: hai lớp cùng tên chỉ xóa đúng id, xóa lúc tìm vẫn giữ các lớp khác, xóa
hết trở lại empty ban đầu. Tự làm trước; lời giải dưới đây dạy callback props,
không đẩy state lên global chỉ để một nút ở con dùng được.

<details><summary>Lời giải và lý do chọn ranh giới</summary>

data.ts thêm hàm pure:

```typescript
export function removeClass(classes: Classroom[], id: number): Classroom[] {
  return classes.filter(classroom => classroom.id !== id);
}
```

filter giữ mục có id khác; callback trả boolean. Trong App import removeClass
cùng findClasses/titleError. Bên trong App, trước return, thêm:

```tsx
function handleRemove(id: number) {
  setClasses(previous => removeClass(previous, id));
}
```

Ở JSX App thay lời gọi con bằng:

```tsx
<ClassList items={visible} onRemove={handleRemove} />
```

Thay file ClassList.tsx bằng bản sau:

```tsx
import type { Classroom } from './data';

type ClassListProps = {
  items: Classroom[];
  onRemove: (id: number) => void;
};

export function ClassList({ items, onRemove }: ClassListProps) {
  return <ul className="class-list">
    {items.map(classroom => <li className="class-card" key={classroom.id}>
      <h3>{classroom.title}</h3>
      <p>Mã lớp: {classroom.id}</p>
      <button type="button" onClick={() => onRemove(classroom.id)}>Xóa</button>
    </li>)}
  </ul>;
}
```

`onRemove:(id:number)=>void` là kiểu hàm props, không phải định nghĩa handler
thật; void nói caller không dùng kết quả trả về. `() => onRemove(id)` là hàm
thật chạy khi click, giữ id card. Viết `onClick={onRemove(id)}` sẽ gọi ngay
khi render và đưa void làm handler. Con gửi ý định lên, cha dùng setter đổi
dữ liệu, rồi props đi xuống. Không có mutation props, không import App vào con.

Build và kiểm bốn tình huống đề bài; chỉ sửa một nơi sở hữu classes. Focus
sau khi nút bị xóa cần thiết kế riêng khi hoàn thiện trải nghiệm; lỗi này là
câu hỏi mở có thật để không lẫn “xóa chạy được” với UI đã hoàn thiện hết.

</details>

**Đề tiếp theo không có code mẫu:** thêm thống kê số lớp có tên chứa “Toán”,
không phụ thuộc query đang tìm. Tự quyết nó là state mới hay dữ liệu tính
được, tự nêu input/output và kiểm chứng bằng hai tên trùng. Xin review theo
bốn câu: đúng hợp đồng? một nguồn dữ liệu? giải thích được handler/props?
đổi yêu cầu có biết nơi sửa? Đây là bằng chứng hiểu, không phải chỉ nhớ JSX.

Sau G2, mày phải tự chạy được từ terminal, giải thích entry/main/App/data/List,
tự dựng list/form/search và sửa một lỗi. Sau đó học G3 về phân tích/cấu trúc;
khi nối backend ở G4–G6, xưởng sẽ thêm HTTP/JSON/quyền/lưu DB vào đúng những
đường đã hiểu. Chưa nhảy thẳng sang 100 dòng effect/token/ORM.

Tác giả kiểm bản tham chiếu bằng dependency xưởng cục bộ. Nếu đang có sẵn
`docs/course/workshop/frontend/node_modules`, có thể copy để kiểm offline thay
vì cài mạng; source vẫn nằm riêng. Lệnh sau **chỉ cho repo giáo án**, không
thay lệnh npm install của dự án học ở D:\so-lop-hoc-react:

```powershell
Set-Location D:\vision-education-lms\docs\course\studio\frontend\react
Copy-Item -LiteralPath ../../../workshop/frontend/node_modules -Destination ./node_modules -Recurse
npm run build
```

Chỉ copy khi đích node_modules chưa có, tránh trộn hai lần cài. Đường dẫn được
tính từ CWD ghi trên; nếu không có dependency xưởng thì bỏ bước này. Những gì
đã chạy thật được ghi ở báo cáo kiểm tra của đợt soạn, không coi lệnh viết trong
sách là kết quả đã thành công trên máy người học.

Nguồn tra đúng API: [React component](https://react.dev/learn/your-first-component),
[event](https://react.dev/learn/responding-to-events),
[state](https://react.dev/learn/state-a-components-memory). Khi gặp API khác,
điền phiếu F2 thay vì mặc định nó giống tên hàm Python quen thuộc.
