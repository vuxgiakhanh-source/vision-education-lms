# 02 — TypeScript, bất đồng bộ và HTTP

Học sau JavaScript; không dùng type để che một hàm bạn chưa hiểu lúc chạy.
Đọc từng request như hợp đồng giữa hai process, không như lời gọi hàm local.

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

## Xưởng — Đọc đủ một hợp đồng HTTP

```http
POST /classes HTTP/1.1
Content-Type: application/json
Authorization: Bearer [token đã ẩn]

{"title":"Đại số"}
```

Request line nói hành động/đường dẫn; header mô tả representation và credential;
body là chuỗi JSON trên dây. GET danh sách dùng query `?page=1&page_size=20`;
GET chi tiết dùng path `/classes/7`. Request ID là dữ liệu client cung cấp,
không phải bằng chứng người gửi có quyền với id7.

```http
HTTP/1.1 201 Created
Content-Type: application/json

{"id":7,"title":"Đại số","teacher_id":1}
```

201 khác200 theo hợp đồng tạo mới. 204 thường không có body: đừng luôn gọi
response.json cho mọi status. 422 do schema có thể khác409 xung đột nghiệp vụ;
401 liên quan xác thực,403 quyền,404 tài nguyên không được tìm thấy trong phạm
vi hợp đồng,500 lỗi server. Quyết định HTTP không được thay bằng toast thành công.

DNS/TCP/TLS giúp đưa request đến server; HTTPS bảo vệ trên đường truyền,
không thay kiểm quyền. Origin gồm scheme, host và port. localhost và127.0.0.1
có thể là origin khác; :5175 và:8000 cũng khác. CORS được trình duyệt áp dụng;
một client ngoài trình duyệt vẫn phải chịu auth/quyền backend.

## Xưởng — Type từ giá trị đến biến thể có giới hạn

```typescript
type Classroom = { id: number; title: string; teacher_id: number };
type LoadState =
  | { kind: 'idle' }
  | { kind: 'loading' }
  | { kind: 'success'; items: Classroom[] }
  | { kind: 'error'; message: string };

function describe(state: LoadState): string {
  if (state.kind === 'success') return `${state.items.length} lớp`;
  if (state.kind === 'error') return state.message;
  return state.kind === 'loading' ? 'Đang tải' : 'Chưa tải';
}
```

`type` đặt tên kiểu; `{}` mô tả field; `[]` là array; `|` chọn một biến thể.
Field kind giúp narrowing: chỉ sau kiểm success mới có items. Property optional
`score?: number` cho phép thiếu, khác `score: number | null` bắt có field với
giá trị có thể null. `readonly` giúp kiểm ở compile-time, không đóng băng object runtime.

Generic mô tả quan hệ giữa kiểu, không phải dấu hiệu dữ liệu đã an toàn:

```typescript
function first<T>(items: readonly T[]): T | undefined {
  return items[0];
}
const firstId = first([1, 2]);
```

T được suy ra number; input rỗng cho undefined. Với hàm nhận unknown, dùng
`typeof`, kiểmnull, Array.isArray hoặc parser. `as` là assertion với compiler,
không gọi một trình chuyển đổi. `any` tắt phần lớn kiểm tra quanh giá trị đó.

## Xưởng — Parser và Axios của repo

```typescript
import { z } from 'zod';
const classSchema = z.object({
  id: z.number().int().positive(),
  title: z.string().min(1),
  teacher_id: z.number().int().positive(),
});
const classesSchema = z.array(classSchema);
type ClassroomData = z.infer<typeof classSchema>;
```

`.parse(body)` trả dữ liệu hợp lệ hoặc ném lỗi. `.safeParse(body)` trả biến
thể success/error để xử lý rõ. Trong lớp API sản phẩm, tái dùng api ở lib/axios;
đọc response.data và parse ở ranh giới phù hợp. Không tạo interceptor mới cho
mỗi component hoặc gửi token vào log để biết request “đã có token”.

Khi catch Axios, phân biệt lỗi có response với lỗi mạng/setup. API error cần
được thu hẹp cấu trúc trước khi lấy detail. Backend có thể trả detail là array
lỗi validation, không luôn là string. Form giữ lỗi theo trường/root theo hợp đồng.

## Xưởng — Thực hành ba mức

1. Điền parser cho một lớp; thử id âm, thiếu teacher_id, title null và mảng rỗng.
2. Tự thiết kế response phân trang `{items,total,page,page_size}` và type/schema.
3. Nhận lỗi “200 nhưng UI crash”, tìm field sai bằng Network; viết test parser
   khiến lỗi này xuất hiện trước render.

Qua xưởng khi nói được giá trị nào nằm trong RAM, giá trị nào là JSON, lúc nào
Promise hoàn tất và lỗi được chuyển thành trạng thái giao diện ở đâu.

## Xưởng cú pháp — đọc generic và Promise trước khi dùng Axios

> [!KEY]
> Tách hai câu hỏi: “compiler nghĩ kiểu gì?” và “khi chạy, hàm trả gì?”.
> Generic là cú pháp truyền thông tin kiểu; Promise là đối tượng biểu diễn
> kết quả bất đồng bộ. Hai thứ thường xuất hiện cùng nhưng không là một.

Đọc dòng đang có trong service đăng nhập của repo:

```typescript
const res = await api.post<LoginResponse>('/login', body);
```

Đây là **một dòng trích để đọc**, body đại diện object được dựng ở caller,
không phải file độc lập đã đủ khai báo/import.

| Mảnh | Ý nghĩa |
|---|---|
| `api.post` | Method của Axios instance được tạo trong lib/axios.ts |
| `<LoginResponse>` | Type argument; trong cách gọi này mô tả body response mong đợi |
| `('/login', body)` | Hai đối số runtime: URL path và dữ liệu request |
| `await` | Đợi Promise trong hàm async, reject thì throw tại đây |
| `res` | Axios response gồm data và các thông tin khác |
| `res.data` | Body mà service thật của repo trả cho form |

Trong source, tên biến input là data và body được viết inline. Đừng nhầm
cùng tên data trong form với thuộc tính data của Axios response. Chỉ cần
service `return res.data` thì **caller nhận body**, không nhận lớp vỏ response.

### Generic là tham số của kiểu, đối số là giá trị khi chạy

`Array<number>` và `number[]` cùng diễn đạt array số trong trường hợp này.
`useState<string>('')` đưa **string vào vị trí kiểu**, đưa **chuỗi rỗng vào
vị trí giá trị khởi tạo**. TS có thể suy ra kiểu từ giá trị, nên không phải
lời gọi nào cũng cần viết generic bằng tay.

`api.post<LoginResponse>` không kiểm JSON server trả về, cũng không biến
phoneNumber thành phone_number. Mapping tên nằm ở code dựng body; validation
runtime cần được thực hiện ở biên theo hợp đồng đã chọn.

> [!TASK]
> Tự định nghĩa request/response cho hành động tạo lớp, chỉ bằng type. Sau đó
> tự viết hàm giả async trả response hợp lệ, chưa dùng Axios hay server.
> Viết caller đọc id. Cố bỏ await để xem kiểu biến thay đổi.

> [!CHECK]
> Caller có await đọc được id; caller thiếu await đang giữ Promise. Thử thêm
> nhánh throw vào hàm giả: dòng sau await trong try bị bỏ qua và catch chạy.

### Narrowing: cho dữ liệu quyền được dùng sau khi đã kiểm

Nếu lỗi có kiểu unknown, trước khi đọc thuộc tính, phải kiểm bằng cách phù
hợp. `error instanceof Error` chỉ xác nhận kiểu Error, chưa tự lấy được
`detail` của HTTP response. Đọc hợp đồng lỗi Axios và payload backend riêng.
`as Error` không làm kiểm tra đó xảy ra khi chạy.

Với `number | null`, kiểm `score !== null` giúp thu hẹp kiểu thành number
trong nhánh. `if (score)` lại bỏ điểm 0. Optional chaining `student?.name`
trả undefined khi student null/undefined; nó không xác nhận tên hợp lệ.
Nullish fallback `score ?? 0` chỉ dùng 0 khi null/undefined, khác `score || 0`.

> [!TASK]
> Từ đề: “chưa chấm hiển thị Chưa chấm; điểm 0 vẫn hiện 0”, tự viết hàm nhận
> number hoặc null và trả chuỗi. Kiểm null, 0, 5. Không dùng any hay assertion.

> [!CHECK]
> Giải thích nhánh thu hẹp kiểu và vì sao fallback không được làm mất khác
> biệt giữa chưa chấm với điểm 0. Tự đề xuất hợp đồng lỗi cho JSON sai kiểu.
