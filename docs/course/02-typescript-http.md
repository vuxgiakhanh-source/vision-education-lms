# 02 — TypeScript, bất đồng bộ và HTTP

## Bài 02.1 — Từ dữ liệu sang kiểu

```typescript
type TaskStatus = 'pending' | 'submitted' | 'graded';

type Task = {
  id: number;
  title: string;
  status: TaskStatus;
  score: number | null;
  teacherNote?: string;
};

function taskLabel(task: Task): string {
  return `${task.title}: ${task.score ?? 'Chưa chấm'}`;
}
```

`type` tạo tên cho kiểu, không tạo object thật. `|` là union: một trong các kiểu
hoặc giá trị. `?` ở thuộc tính cho phép thiếu trường; khi đọc có thể nhận undefined.
`number | null` đòi hỏi trường tồn tại nhưng giá trị có thể null. `: string` sau
tham số là kiểu trả về. `Task[]` là mảng Task. Dùng trạng thái có tập giá trị cố
định để trình biên dịch phát hiện viết sai tên trạng thái.

`interface` cũng mô tả được cấu trúc object; repo dùng cả type và interface.
Theo quy ước hiện có, không đổi qua lại toàn dự án chỉ vì thích cú pháp khác.
`import type` chỉ nhập kiểu, phù hợp cấu hình `verbatimModuleSyntax` của repo.

## Bài 02.2 — Narrowing và vì sao cần unknown

```typescript
function readTitle(value: unknown): string {
  if (typeof value !== 'object' || value === null) {
    throw new Error('Dữ liệu phải là object');
  }
  if (!('title' in value) || typeof value.title !== 'string') {
    throw new Error('Thiếu title hợp lệ');
  }
  return value.title;
}
```

TypeScript thu hẹp kiểu sau điều kiện. `typeof null` là 'object', vì vậy phải
kiểm tra null. `unknown` buộc xác minh trước khi dùng; `any` bỏ bớt kiểm tra.
Không dùng `as Task` hoặc dấu `!` để che lỗi dữ liệu. TypeScript bị loại bỏ khi
build; response từ server vẫn cần hợp đồng và validation khi phù hợp.

Zod trong project có thể kiểm tra ở thời điểm chạy:

```typescript
import { z } from 'zod';

const taskSchema = z.object({
  id: z.number().int().positive(),
  title: z.string().trim().min(1),
  status: z.enum(['pending', 'submitted', 'graded']),
  score: z.number().min(0).max(10).nullable(),
});

type ValidatedTask = z.infer<typeof taskSchema>;
const parsed = taskSchema.safeParse({
  id: 1, title: 'Hàm số', status: 'pending', score: null,
});
if (parsed.success) console.log(parsed.data.title);
else console.log(parsed.error.issues);
```

`z.infer` lấy kiểu từ schema. `parse` ném lỗi nếu sai; `safeParse` trả kết quả
để xử lý hai nhánh. Quy tắc điểm 0–10 ở đây là giả định bài học.

## Bài 02.3 — Generic là kiểu có tham số

```typescript
type Page<T> = { items: T[]; total: number };
function firstOrNull<T>(items: T[]): T | null {
  return items[0] ?? null;
}
const first = firstOrNull([10, 20]);
```

`T` là chỗ đặt kiểu; khi dùng Page<Task>, items là Task[]. Generic bảo toàn mối
quan hệ giữa đầu vào và đầu ra. Không phải cứ viết `<T>` là phần mềm linh hoạt.
Axios `get<Task[]>` giúp kiểm tra code gọi API, không tự xác thực JSON ở runtime.

## Bài 02.4 — Promise và thứ tự chạy

```javascript
console.log('A');
Promise.resolve('B').then(value => console.log(value));
console.log('C');
// A, C, B
```

Promise biểu diễn kết quả có thể hoàn thành sau. `async` khiến hàm trả Promise;
`await` chờ kết quả trong hàm async, không làm toàn bộ trình duyệt ngừng hoạt động.

```typescript
async function loadTitle(url: string): Promise<string> {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  const body: unknown = await response.json();
  return readTitle(body);
}
```

`fetch` không tự throw cho HTTP 400/500; phải kiểm tra `ok`. Axios thường reject
response lỗi HTTP theo cấu hình mặc định. `try/catch/finally`: xử lý thành công,
lỗi, rồi dọn trạng thái dù kết quả nào. Gọi hàm async mà quên await có thể nhận
Promise thay vì dữ liệu và không bắt được lỗi ở nơi dự kiến.

Hai công việc độc lập có thể dùng Promise.all; hai công việc phụ thuộc phải theo
thứ tự. Ví dụ tạo lớp xong mới có id để thêm thành viên. Promise.all không biến
nhiều request thành một transaction database.

## Bài 02.5 — HTTP là hợp đồng giữa hai chương trình

Ví dụ minh họa endpoint tương lai, chưa tồn tại trong repo:

```http
POST /classes/12/assignments
Content-Type: application/json
Authorization: Bearer <access_token>

{"title":"Ôn hàm số","due_at":"2026-11-01T13:00:00Z"}
```

- Method: hành động; path: tài nguyên; path parameter 12: lớp được chọn.
- Query như `?page=1&page_size=20`: lọc/phân trang theo hợp đồng.
- Header: metadata; body: dữ liệu yêu cầu. Mọi dữ liệu client gửi đều phải kiểm tra.
- JSON chỉ có kiểu phù hợp JSON; không mang theo method hoặc class Python.
- 200: thành công; 201: tạo mới; 204: không có body; 400: yêu cầu không hợp lệ
  theo hợp đồng; 401: thiếu/sai xác thực; 403: không đủ quyền; 404: không có tài nguyên;
  409: xung đột trạng thái; 422 thường dùng cho validation FastAPI; 500: lỗi server.

Đây là cách đọc phổ biến, API của từng chức năng phải thống nhất cụ thể. Không
dùng status 200 cho mọi lỗi rồi chỉ đổi chuỗi message. Đừng log body đăng nhập.

## Bài 02.6 — Mô hình trạng thái tránh tổ hợp vô nghĩa

```typescript
type LoadState<T> =
  | { kind: 'loading' }
  | { kind: 'error'; message: string }
  | { kind: 'success'; data: T };

function countLoaded(state: LoadState<string[]>): number | null {
  if (state.kind !== 'success') return null;
  return state.data.length;
}
```

Ở nhánh success mới có data. Kiểu này tránh tình huống vừa loading vừa báo lỗi
cũ ngoài ý muốn. Danh sách rỗng vẫn là success với `data: []`, không phải lỗi mạng.

## Bài tự viết

- **TS1:** type cho bài tập, phân biệt deadline chưa đặt với trường bị thiếu.
- **TS2:** parse một response unknown; thử sai id, thiếu title và score bằng 0.
- **TS3:** tự viết hàm async, cố tình trả HTTP lỗi rồi giải thích nơi catch chạy.
- **TS4:** thiết kế LoadState cho lớp học; không render dữ liệu khi chưa success.
- **TS5:** quan sát request đăng nhập thật trong Network; ghi tên trường, status
  và luồng xử lý, không chép token vào nhật ký.

Tham khảo: [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html),
[Zod basics](https://zod.dev/basics), [MDN Promises](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Using_promises).
