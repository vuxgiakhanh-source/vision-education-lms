# 04 — React: từ dữ liệu đến màn hình có hành vi

> Chuyên đề đào sâu. [G2](G2-tu-js-sang-react.md) dẫn tạo project, entry, state và component từ thư mục trống trước. Dùng các mục dưới để tra khi thêm form/API/router; không cần học cả chương cùng lúc để làm trang React đầu.

## Bài 04.1 — Render là mô tả giao diện từ dữ liệu

```tsx
type LessonProps = { title: string; completed: boolean };

export function LessonRow({ title, completed }: LessonProps) {
  return <p>{title} — {completed ? 'Đã học' : 'Chưa học'}</p>;
}
```

Component là hàm nhận props và trả JSX. `{}` đưa biểu thức vào JSX; không đặt
vòng lặp for hoặc câu lệnh if trực tiếp trong ngoặc biểu thức. Có thể tính trước
return, dùng map hoặc biểu thức điều kiện. Component gọi API/ghi storage trong
render sẽ tạo side effect khó kiểm soát; giữ render thuần.

## Bài 04.2 — State là dữ liệu React cần nhớ giữa các lần render

```tsx
import { useState } from 'react';

export function Counter() {
  const [count, setCount] = useState(0);
  function addTwo() {
    setCount(previous => previous + 1);
    setCount(previous => previous + 1);
  }
  return <button type="button" onClick={addTwo}>{count}</button>;
}
```

`useState` trả cặp giá trị và hàm cập nhật. Setter đề nghị lần render mới;
không làm biến count trong handler hiện tại đổi ngay. Hai lần `setCount(count+1)`
cùng đọc snapshot cũ nên không tương đương updater ở trên.
`onClick={addTwo}` truyền hàm; `onClick={addTwo()}` gọi ngay khi render.
Hook ở đầu component/custom hook, không đặt sau return có điều kiện hoặc trong vòng lặp.

## Bài 04.3 — State tối thiểu và luồng dữ liệu

```tsx
import { useState } from 'react';
type Task = { id: number; title: string };
type Props = { tasks: Task[]; onOpen: (id: number) => void };

export function TaskSearch({ tasks, onOpen }: Props) {
  const [query, setQuery] = useState('');
  const normalized = query.trim().toLowerCase();
  const visible = tasks.filter(task => task.title.toLowerCase().includes(normalized));
  return (
    <section>
      <label htmlFor="task-search">Tìm bài</label>
      <input id="task-search" value={query} onChange={event => setQuery(event.target.value)} />
      <p>{visible.length} bài</p>
      <ul>
        {visible.map(task => (
          <li key={task.id}>
            <button type="button" onClick={() => onOpen(task.id)}>{task.title}</button>
          </li>
        ))}
      </ul>
    </section>
  );
}
```

Query cần state; visible tính được từ props/query nên không cần thêm state.
Props đi xuống, callback báo hành động lên. Key là id ổn định, không dùng index
cho danh sách có thể thêm/xóa/sắp xếp. Nếu hai component cần cùng dữ liệu, cân
nhắc đưa state lên cha chung trước khi thêm công cụ quản lý state toàn cục.

## Bài 04.4 — Effect đồng bộ với hệ thống bên ngoài

Ví dụ hoàn chỉnh cho một endpoint trả `{title: string}`. Endpoint này là bài học,
không phải endpoint đã có trong repo.

```tsx
import { useEffect, useState } from 'react';
type State =
  | { kind: 'loading' }
  | { kind: 'error'; message: string }
  | { kind: 'success'; title: string };

export function RemoteTitle({ url }: { url: string }) {
  const [state, setState] = useState<State>({ kind: 'loading' });
  useEffect(() => {
    const controller = new AbortController();
    let active = true;
    setState({ kind: 'loading' });
    async function load() {
      try {
        const response = await fetch(url, { signal: controller.signal });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const body: unknown = await response.json();
        if (typeof body !== 'object' || body === null ||
            !('title' in body) || typeof body.title !== 'string') {
          throw new Error('Response sai hợp đồng');
        }
        if (active) setState({ kind: 'success', title: body.title });
      } catch (error) {
        if (active) setState({
          kind: 'error', message: error instanceof Error ? error.message : 'Không tải được',
        });
      }
    }
    void load();
    return () => { active = false; controller.abort(); };
  }, [url]);
  if (state.kind === 'loading') return <p>Đang tải…</p>;
  if (state.kind === 'error') return <p role="alert">{state.message}</p>;
  return <h2>{state.title}</h2>;
}
```

Effect không được khai báo trực tiếp `async` vì React cần cleanup, không cần
Promise làm giá trị trả về. Dependency url đảm bảo tải lại đúng khi url đổi;
cleanup chặn response cũ cập nhật trang mới. StrictMode của repo có thể chạy thêm
chu kỳ setup/cleanup trong phát triển để phát hiện lỗi; không tắt nó để giấu effect lỗi.
Hành động nộp bài do người dùng bấm thuộc event handler, không tự đưa vào effect.

Đây là ví dụ học cơ chế fetch thủ công. Khi dùng Axios thật, tái sử dụng `api`
của repo và cách kiểm tra lỗi Axios; không viết thêm client HTTP riêng cho từng trang.

## Bài 04.5 — Form thủ công rồi mới dùng thư viện

Trước hết tự làm một input controlled: state giữ giá trị, onChange cập nhật,
onSubmit preventDefault và gọi hàm xử lý. Sau đó đọc form hiện tại sử dụng
React Hook Form: register nối trường, handleSubmit xử lý trước khi gọi onSubmit,
errors chứa lỗi và isSubmitting phản ánh Promise submit đang chờ.

```tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const schema = z.object({ title: z.string().trim().min(1, 'Nhập tên lớp') });
type Values = z.infer<typeof schema>;

export function ClassForm({ onCreate }: { onCreate: (title: string) => Promise<void> }) {
  const { register, handleSubmit, setError, formState: { errors, isSubmitting } } =
    useForm<Values>({ resolver: zodResolver(schema), defaultValues: { title: '' } });
  async function submit(values: Values) {
    try { await onCreate(values.title); }
    catch { setError('root', { message: 'Không tạo được lớp. Hãy thử lại.' }); }
  }
  return (
    <form onSubmit={handleSubmit(submit)}>
      <label htmlFor="class-title">Tên lớp</label>
      <input id="class-title" {...register('title')} aria-invalid={!!errors.title} />
      {errors.title && <p role="alert">{errors.title.message}</p>}
      {errors.root && <p role="alert">{errors.root.message}</p>}
      <button disabled={isSubmitting} type="submit">
        {isSubmitting ? 'Đang tạo…' : 'Tạo lớp'}
      </button>
    </form>
  );
}
```

Validation frontend phục vụ trải nghiệm; backend vẫn kiểm tra. Error chi tiết
theo trường nên ánh xạ theo hợp đồng API, không hiện raw stack trace cho học sinh.

## Bài 04.6 — Router, custom hook và phạm vi trách nhiệm

Trong repo, `App.tsx` khai báo Route. `Link` phù hợp điều hướng; `useNavigate`
cho điều hướng sau hành động. Guard frontend điều khiển trải nghiệm; backend
vẫn quyết định quyền. Custom hook gom logic React tái sử dụng, không tự tạo
một state dùng chung giữa mọi nơi gọi. Hai component gọi cùng custom hook vẫn
có state riêng nếu không dùng một nguồn state chung.

Chỉ cân nhắc useMemo/useCallback sau khi có lý do về tính toán hoặc tham chiếu;
chúng không sửa được luồng state thiết kế sai.

## Bài tự viết

- **R1:** trang nhiệm vụ có tìm kiếm, số kết quả, rỗng; không lưu visible bằng state.
- **R2:** mở bài bằng callback id; đọc TaskListCard hiện tại và chỉ ra vì sao nút chưa mở trang thật.
- **R3:** tải danh sách theo classId; chuyển lớp nhanh không hiển thị response lớp cũ.
- **R4:** form tạo lớp: lỗi frontend, lỗi API, disable submit trong lúc xử lý.
- **R5:** tự giải thích một effect thừa và bỏ nó bằng dữ liệu tính trực tiếp.

Qua chương khi tự tạo được component, mô tả dữ liệu thuộc cha/con nào, giải thích
dependency và cleanup, kiểm tra bàn phím và refresh trang.

Tham khảo: [React Learn](https://react.dev/learn),
[useEffect](https://react.dev/reference/react/useEffect),
[React Hook Form](https://react-hook-form.com/get-started), [Zod](https://zod.dev/basics).

## Xưởng — Xây theo thứ tự, không bắt đầu bằng effect

1. Vẽ component tree: ClassPage → Search + ClassList → ClassRow.
2. Tạo type dữ liệu và fixture 3 hàng, render tĩnh bằng props.
3. Thêm query state; tính visible ngay trong render.
4. Thêm controlled form bằng state trước RHF.
5. Thêm API service và load state; thay fixture bằng response.
6. Thêm create, chờ server trả bản ghi thật rồi cập nhật/reload đúng danh sách.
7. Thử error/empty/retry/chuyển tài khoản và refresh.

Ở bước 2, component chưa có tương tác nhưng bạn đã kiểm được cấu trúc; ở bước3
mới có state tối thiểu. Cách chia này giúp biết lỗi UI, state hay network.

## Xưởng — Form thủ công từng ký hiệu

```tsx
import { useState } from 'react';
import type { FormEvent } from 'react';

export function ManualClassForm({ onCreate }: {
  onCreate: (title: string) => Promise<void>;
}) {
  const [title, setTitle] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const normalized = title.trim();
    if (!normalized) { setError('Nhập tên lớp'); return; }
    setBusy(true); setError('');
    try { await onCreate(normalized); setTitle(''); }
    catch { setError('Không tạo được lớp'); }
    finally { setBusy(false); }
  }
  return <form onSubmit={submit}>
    <label htmlFor="manual-title">Tên lớp</label>
    <input id="manual-title" value={title}
      onChange={event => setTitle(event.target.value)} />
    {error && <p role="alert">{error}</p>}
    <button type="submit" disabled={busy}>{busy ? 'Đang lưu' : 'Tạo lớp'}</button>
  </form>;
}
```

Props có callback Promise<void>: con gửi ý định, cha/API quyết định lưu. Event
type mô tả phần tử form. preventDefault ngăn browser submit/navigation mặc định.
Value+onChange giữ input controlled. setTitle đặt lần render sau, không sửa
props. Finally dọn busy dù success hay error. Nút disabled là UX; backend vẫn
phải chống tác dụng trùng khi người dùng/client khác gửi request.

Sau khi tự viết được, so register/handleSubmit/errors/isSubmitting của RHF
với các việc mình vừa làm. Resolver nối Zod validation vào form. Type infer
được từ schema không thay validation ở server.

## Xưởng — Đặt state và chia trách nhiệm

| Dữ liệu | Nơi đầu tiên nên giữ | Lý do |
|---|---|---|
| Input đang gõ | Form hoặc cha cần dùng | Chưa phải bản ghi đã lưu |
| Filter query | Page/toolbar chung | List cần dùng nó |
| Kết quả filter | Tính từ items/query | Không tạo bản sao state phải đồng bộ |
| Lớp từ server | Page/hook quản lý tải | Server là nguồn dữ liệu bền |
| Token/current user | Nguồn phiên thống nhất | Phải xóa cache riêng khi đổi phiên |
| Toggle một menu | Component gần nhất | Không đưa global nếu không cần |

Context truyền dependency/state qua cây; không tự tạo cache server hoặc sửa
mọi re-render. Custom hook tái sử dụng logic, không tự dùng chung cùng state.
Ref giữ giá trị qua render mà đổi nó không yêu cầu render; dùng cho DOM hoặc
giá trị imperative phù hợp, không thay state cho dữ liệu cần hiển thị.

## Xưởng — Router theo cấu trúc repo

Đọc App.tsx: BrowserRouter chứa Routes/Route; path chọn element. Link cho
điều hướng, navigate sau hành động; Outlet cho route con. Guard chỉ kiểm token
tồn tại của repo chưa chứng minh token hợp lệ hoặc quyền theo lớp. Trang chi
tiết lấy id từ route rồi gọi API; server vẫn kiểm actor-resource.

Ở server production, refresh `/classes/7` phải phục vụ entry frontend phù hợp
thay vì404 file; không rewrite API sai thành index.html. Giữ fallback/frontend
và routing backend tách rõ trong cấu hình host.

## Xưởng — Ba bài để chứng minh tự làm

**Điền:** thêm lỗi theo trường cho form ở trên; không xóa nội dung khi server lỗi.

**Trắng:** trang lớp có list/tìm/tạo/loading/error/empty; không copy TaskSearch.
Tự viết type/service/component, giải thích nơi gọi effect và callback.

**Sửa lỗi:** hai request A/B, B về trước rồi A ghi đè. Tái hiện bằng delay
fixture, sửa cancel/ignore với lifecycle đúng, thử cả đổi token và unmount.

Đối chiếu [Thinking in React](https://react.dev/learn/thinking-in-react) cho
quy trình component → UI tĩnh → state tối thiểu → vị trí state → data flow.

## Xưởng đọc LoginForm — bóc từng lớp cú pháp

Đích ở đây là **tự đọc được source thật**, không dựng lại nguyên form mẫu.
Mở [LoginForm](../../frontend/src/features/auth/login/components/LoginForm.tsx)
và lần theo import. useForm thuộc react-hook-form, zodResolver thuộc gói
resolver, useNavigate thuộc router; chúng không phải từ khóa TypeScript.

### Lấy hai giá trị theo vị trí

```tsx
const [showPassword, setShowPassword] = useState(false);
```

Cú pháp `[a, b]` là array destructuring. useState trả tuple theo hợp đồng
React: snapshot giá trị ở vị trí đầu, setter ở vị trí sau. Tên do mình đặt;
đổi tên không đổi hợp đồng. false là boolean runtime. Hook phải được gọi theo
quy tắc hook ở đầu component/custom hook, không tùy tiện trong if hay loop.

**Tự viết:** tạo component chỉ có một nút và một boolean đang mở. Tự chọn tên,
hiện chữ Mở/Đóng theo state. **Tự kiểm:** bấm hai lần phải về trạng thái đầu;
giải thích vì sao gán thẳng biến không thay việc gọi setter.

### Lấy thuộc tính và lấy tiếp thuộc tính lồng

```tsx
const { register, formState: { errors, isSubmitting } } = form;
```

Đây là dòng minh họa phép lấy từ object form, không phải toàn bộ lời gọi
useForm. register lấy thuộc tính register; `formState: { ... }` đi vào
form.formState rồi lấy hai tên bên trong. Nó **không tự tạo biến formState**.
Ở source thật, phía phải là `useForm<LoginFormData>({...})` thay cho form.

**Tự viết:** tạo object settings có user và ui lồng; tự lấy user.name và
ui.compact mà không khai báo dư tên. **Tự kiểm:** nói rõ hai dấu hai chấm
ở destructuring khác annotation kiểu `name: string` thế nào.

### Một lời gọi trả hàm, rồi hàm đó mới xử lý sự kiện

Dòng cần đọc: `<form onSubmit={handleSubmit(onSubmit)}>`.

Đây là fragment JSX để đọc prop, không phải component độc lập đã đóng thẻ.
`handleSubmit(onSubmit)` được gọi để tạo handler có kiểm form. Nó nhận
**hàm onSubmit**, không gọi `onSubmit()` ngay. Handler trả về mới được gắn
vào sự kiện submit. Khi submit hợp lệ, thư viện gọi callback với data.

**Tự vẽ:** render → tạo handler → người dùng submit → validate → callback.
**Tự kiểm:** validation thất bại thì onSubmit nghiệp vụ có chạy không? Đọc
hợp đồng hook form trước khi trả lời; không suy từ tên hàm.

### Spread trong JSX và kết quả lời gọi

```tsx
<input {...register('phoneNumber')} />
```

Đọc từ trong ra: gọi register với tên field → nhận object theo hợp đồng
thư viện → JSX spread các props vào input. Dấu ... ở đây không phải rest
parameter. Chưa hiểu register trả gì thì chưa thể hiểu cả dòng; mở kiểu
return hoặc phiếu API, quan sát name/ref/các event handler mà nó cung cấp.

**Tự phân tích:** tách thành một biến tạm giữ kết quả register rồi diễn đạt
lại ý nghĩa. **Tự kiểm:** xóa spread, chỉ giữ name thì input còn được đăng ký
đầy đủ với thư viện không? Nêu phần liên kết đã mất thay vì chỉ đoán giao diện.

### JSX: phần nào là chữ, phần nào là biểu thức?

```tsx
<p>{showPassword ? 'Đang hiện' : 'Đang ẩn'}</p>
```

Thẻ p thuộc cây UI. `{...}` chuyển vào biểu thức JS. `điều kiện ? A : B`
chọn một trong hai giá trị, khác optional property `note?: string` trong type.
`errors.phoneNumber && (...)` dùng short-circuit để chỉ dựng phần báo lỗi
khi giá trị phía trái truthy. Với số, `0 && ...` còn cho 0: phải chọn điều
kiện rõ nếu không muốn số 0 xuất hiện trên UI.

Trong JSX dùng `className` cho class CSS và `htmlFor` cho label theo hợp
đồng React DOM. `className="p-8 ..."` là chuỗi class Tailwind, không phải
cú pháp TS mới. Muốn tự bố cục phải biết padding/flex/grid ở CSS trước.

> [!TASK]
> Đóng LoginForm. Tự dựng một form tên lớp nhỏ bằng state hoặc thư viện đã
> học: label, input, submit, thông báo tên trắng, trạng thái đang gửi.
> Viết bằng HTML/CSS rõ trước; sau đó mới chuyển một vài luật sang Tailwind.

> [!CHECK]
> Với mỗi dấu {}, (), [], ..., =>, : trong bài tự viết, nêu ngữ cảnh và vai
> trò. Nếu chỉ biết “code thường viết thế”, tách riêng dòng đó để thử lại.
