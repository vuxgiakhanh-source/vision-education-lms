# 04 — React: từ dữ liệu đến màn hình có hành vi

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
