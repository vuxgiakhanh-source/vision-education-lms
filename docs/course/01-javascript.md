# 01 — JavaScript: cú pháp và tư duy xử lý dữ liệu

Mục tiêu: tự viết hàm xử lý nhiệm vụ trước khi đưa vào React.
Ví dụ này chạy độc lập trong Node hoặc Console; chưa sửa dashboard thật.

## Trước khi đọc code: cách dùng chương này

Nếu chưa hiểu biến, dấu nháy và dấu gán, học [S0](START-TU-SO-0.md) trước. Mỗi
đoạn sau phải làm ba lần: dự đoán trên giấy, chạy để đối chiếu, đóng tài liệu
và viết một biến thể. Mở Console để quan sát; các snippet là bài học độc lập,
không dán vào source dashboard đang chạy.

Chưa biết nhánh/lặp/hàm là bình thường ở bước này. Học lần lượt các mục;
đọc biểu thức và tự đổi vài dòng trước, rồi mới làm bài thuật toán tổng hợp
ở Tư duy lập trình. Không cần làm được thuật toán trước khi học cú pháp của nó.

## Bài 01.1 — Biến, giá trị và kiểu

```javascript
const studentName = 'Khánh';
let submittedCount = 0;
submittedCount = submittedCount + 1;
const isSubmitted = false;
const selectedTask = null;
console.log(studentName, submittedCount, isSubmitted, selectedTask);
```

`const` ngăn gán lại biến; `let` cho phép gán lại. Dấu `=` là gán, không phải so sánh.
String là chuỗi; number là số; boolean là true/false. `null` biểu thị chủ động
chưa có giá trị. `undefined` thường xuất hiện khi thuộc tính chưa tồn tại hoặc
hàm không trả giá trị. `NaN` biểu thị kết quả số không hợp lệ.

```javascript
console.log('2' + 1);         // '21': nối chuỗi
console.log(Number('2') + 1); // 3
console.log(Number('abc'));   // NaN
console.log(0 === '0');       // false
console.log(Boolean('false'));// true: chuỗi không rỗng
```

Tư duy: biết nguồn dữ liệu. Giá trị nhập từ input thường là chuỗi kể cả input
kiểu number. Ép kiểu rồi kiểm tra trước khi dùng. Không dùng `Boolean` để đọc
chuỗi 'false' thành false; phải parse theo hợp đồng.

## Bài 01.2 — Điều kiện và giá trị rỗng

**if** nghĩa là “nếu”. Nó nhận một điều kiện trong ngoặc tròn; chỉ khi điều
kiện đúng thì chạy phần trong ngoặc nhọn. **else** là phần còn lại nếu sai.

```javascript
let diem = 7;
if (diem >= 5) {
  console.log('Đạt');
} else {
  console.log('Chưa đạt');
}
```

Đọc: diem hiện7; hỏi7>=5 được true; chạy nhánh Đạt và bỏ nhánh Chưa đạt.
`{` mở nhóm lệnh, `}` đóng nhóm lệnh. Thụt dòng giúp mắt thấy dòng nào thuộc
nhóm; ở JavaScript, ngoặc nhọn mới xác định nhóm. Đổi diem thành4 rồi kể nhánh
nào chạy. Chưa cần biết function hoặc return để hiểu ví dụ này.

<details><summary>Đọc sau khi đã quen if và hàm: hai cách chọn giá trị</summary>

```javascript
const score = 0;
console.log(score || 'Chưa chấm'); // sai ý nghĩa: 0 bị coi là falsy
console.log(score ?? 'Chưa chấm'); // 0: chỉ thay null hoặc undefined
```

`===` so sánh nghiêm ngặt. `&&`, `||` có short-circuit và có thể trả giá trị
không phải boolean. `??` có ích khi 0 là điểm hợp lệ. `if`/`else` biểu diễn nhánh;
return sớm giúp tránh nhiều tầng lồng nhau, nhưng phải giữ tên điều kiện dễ hiểu.

</details>

## Bài 01.2a — Array: nhiều giá trị trong một danh sách

**Array** là danh sách có thứ tự. `[` mở danh sách, `]` đóng danh sách, dấu
phẩy `,` ngăn các phần tử. Đây là dấu mới, khác ngoặc tròn gọi thao tác và
ngoặc nhọn nhóm lệnh của if.

```javascript
const scores = [7, 8, 9];
console.log(scores[0]);
console.log(scores.length);
```

Dòng1 giữ danh sách ba số dưới tên scores. `scores[0]` lấy phần tử ở vị trí0
nên cho7; vị trí đầu được đánh số0, tiếp theo1 và2. `.length` đọc số phần tử
nên cho3; đây là đọc một thuộc tính, không phải lời gọi, nên không có `()`.
Đọc `scores[3]` nhận undefined vì không có phần tử thứ tư trong danh sách này.

Tự viết danh sách2 tên trong dấu nháy, hiển thị tên đầu và số tên. Phân biệt
`scores[0]` đọc một mục với `[0]` tự nó là danh sách mới gồm số0.

## Bài 01.2b — for: lặp lại một nhóm lệnh

Khi cần cộng ba điểm, có thể đọc từng vị trí rồi cộng. Vòng lặp cho máy làm
cùng một việc với từng phần tử, không cần chép câu lệnh nhiều lần.

```javascript
const scores = [7, 8, 9];
let total = 0;
for (const score of scores) {
  total = total + score;
}
console.log(total);
```

`for` bắt đầu vòng lặp; `of scores` nói lấy từng phần tử của scores; `const score`
đặt tên cho phần tử đang xét trong lượt này. Phần giữa `{...}` chạy mỗi lượt.
Không gán lại score trong thân, còn total dùng let vì cần cập nhật.

| Lượt | score | total trước | total sau |
|---|---|---|---|
| 1 | 7 | 0 | 7 |
| 2 | 8 | 7 | 15 |
| 3 | 9 | 15 | 24 |

Khi hết phần tử, thoát for rồi log hiển thị24. Danh sách rỗng `[]` không chạy
thân lần nào nên total vẫn0. Tự đổi danh sách thành `[2, 3]`, dự đoán từng lượt.
Các ví dụ này chạy bằng JavaScript thật theo bộ công cụ; ô luyện S0 chưa hỗ
trợ array/vòng lặp và sẽ nói rõ giới hạn nếu dán chúng vào.

## Bài 01.3 — Hàm, tham số, trả về, scope

**Hàm** là một công việc được đặt tên để gọi khi cần. Viết định nghĩa không
có nghĩa công việc đã chạy. Bắt đầu bằng một phép cộng, chưa lồng vòng lặp:

```javascript
function addOne(number) {
  return number + 1;
}
const result = addOne(7);
console.log(result);
```

| Phần | Nghĩa cụ thể |
|---|---|
| function | Định nghĩa một hàm |
| addOne | Tên mình đặt cho công việc |
| (number) ở định nghĩa | Tên nhận dữ liệu mỗi lần hàm được gọi: tham số |
| { và } | Bao những câu lệnh thuộc hàm |
| return number + 1; | Tính và đưa kết quả về nơi đã gọi, rồi kết thúc lần gọi |
| addOne(7) | Gọi hàm, đưa số7 vào number: đối số |
| const result = ... | Nhận số8 hàm trả về và giữ dưới tên result |

Chạy ba dòng định nghĩa đầu mới chỉ có công việc tên addOne. Dòng gọi mới
chạy thân với number=7; return đưa8 về dòng đó. Log hiển thị8. Chỉ log bên
trong mà không return thì bên ngoài không nhận được kết quả như trên.

Tự gọi addOne(2) và addOne(10). Sau đó đóng mẫu, tự viết addTwo nhận một số
và trả số đó cộng2. Khi đã giải thích được, ghép hàm với array/for đã học:

```javascript
function average(scores) {
  if (scores.length === 0) return null;
  let total = 0;
  for (const score of scores) total += score;
  return total / scores.length;
}

console.log(average([8, 6, 10])); // 8
console.log(average([]));        // null, chưa có điểm
```

`scores` là tham số; `[8, 6, 10]` là đối số ở lời gọi. `return` đưa kết quả ra ngoài
và kết thúc lần gọi. `console.log` chỉ quan sát, không thay return.
`total` ở trong hàm không phải biến toàn cục.

Trong bài học này đầu vào được giả định là mảng số hợp lệ. Khi nhận dữ liệu từ
mạng phải kiểm tra thêm. Quy tắc điểm trung bình thật cần chốt trọng số và loại bài.

## Bài 01.3a — Object: các mục dữ liệu có tên

**Object** gom các mục như tên và điểm của cùng một học sinh. Mỗi mục gọi là
thuộc tính: có tên và giá trị. Dấu `{...}` ở đây tạo dữ liệu, khác khối lệnh
sau if/for/function; nhìn cả ngữ cảnh, không đoán chỉ từ một dấu.

```javascript
const student = { name: 'An', score: 7 };
console.log(student.name);
console.log(student.score);
```

`name` và `score` là tên thuộc tính; dấu `:` ngăn tên với giá trị; dấu phẩy
ngăn các cặp. `.name` đọc mục name của student, nên cho chuỗi An. `.score`
cho7. `student` giữ cả object, không chỉ một mục.

Tự tạo object task có title là một chuỗi và status là chuỗi pending. Đọc từng
mục bằng dấu chấm. Sau đó mới đặt vài object vào một array để có danh sách task.

## Bài 01.4 — Object, array, destructuring và callback

Đã biết object/array/hàm, giờ mới học cách viết gọn. **Callback** là một hàm
được đưa cho hàm khác để nó gọi lúc cần; `filter` là thao tác của array dùng
kết quả callback để quyết định giữ từng phần tử. Đọc dạng viết đầy đủ ở Xưởng1
nếu chưa quen dấu `=>`; chưa cần dùng dạng ngắn để chứng minh biết code.

```javascript
const tasks = [
  { id: 1, title: 'Hàm số', status: 'pending' },
  { id: 2, title: 'Tích phân', status: 'submitted' },
  { id: 3, title: 'Hình học', status: 'pending' },
];

const first = tasks[0];
const { id, title } = first;
const pending = tasks.filter(task => task.status === 'pending');
const titles = pending.map(task => task.title);
console.log(id, title, titles); // 1, 'Hàm số', ['Hàm số', 'Hình học']
```

- Object giữ các trường có tên; array giữ danh sách có thứ tự, index bắt đầu từ 0.
- `task => ...` là hàm mũi tên một tham số và return ngầm biểu thức.
- `filter` giữ phần tử khi callback trả truthy; `map` tạo kết quả cho từng phần tử.
- `find` trả phần tử đầu hoặc undefined; `some` trả boolean; `forEach` không trả
  mảng kết quả; `reduce` gom giá trị và nên có giá trị khởi tạo rõ ràng.
- `task => { task.id }` không có return; nó khác `task => task.id`.

```javascript
const count = tasks.reduce(
  (total, task) => total + (task.status === 'pending' ? 1 : 0),
  0,
);
console.log(count); // 2
```

Hãy viết vòng lặp trước nếu `reduce` làm bạn không hiểu. Tính đúng và đọc rõ
quan trọng hơn dùng cú pháp ngắn nhất.

## Bài 01.5 — Tham chiếu, mutation và copy nông

```javascript
const original = { title: 'Đại số', meta: { attempts: 1 } };
const alias = original;
alias.title = 'Hình học';
console.log(original.title); // 'Hình học'

const shallow = { ...original };
shallow.meta.attempts = 2;
console.log(original.meta.attempts); // 2: object lồng vẫn chung

const next = {
  ...original,
  meta: { ...original.meta, attempts: 3 },
};
console.log(original.meta.attempts, next.meta.attempts); // 2, 3
```

`const` không làm object bất biến. Spread tạo bản sao nông. Đây là lý do trong
React không gán trực tiếp `state.tasks[0].status = ...` rồi mong UI đúng.

```javascript
function markSubmitted(tasks, taskId) {
  return tasks.map(task =>
    task.id === taskId ? { ...task, status: 'submitted' } : task
  );
}
```

Hàm này chỉ minh họa cập nhật dữ liệu local; quyền nộp và trạng thái thật phải
được backend xác nhận. Array mới được tạo; các object không thay đổi được giữ tham chiếu.
`sort` và `reverse` sửa array gốc; dùng bản sao hoặc `toSorted`/`toReversed`
khi cần giữ dữ liệu cũ.

## Bài 01.6 — Tách hàm và độ phức tạp

Một hàm dễ kiểm tra nên có đầu vào, đầu ra và quy tắc rõ. Hàm tính số bài chưa
nộp không nên đồng thời sửa DOM, gọi API và ghi localStorage.
Duyệt n phần tử một lần thường có chi phí O(n); hai vòng lặp lồng đầy đủ có thể
là O(n²). Với nhiệm vụ hiện tại, ưu tiên thuật toán rõ trước khi tối ưu.

Khi tìm nhiều lần theo id, Map có thể phù hợp. Không học cấu trúc dữ liệu chỉ
để thuộc ký hiệu: hãy đo và giải thích thao tác đang lặp lại.

## Bài tự viết — không nhìn ví dụ

1. **JS1:** `countPending(tasks)` trả 0 khi rỗng, không đếm trạng thái khác.
2. **JS2:** `searchTasks(tasks, query)` bỏ khoảng trắng hai đầu, không phân biệt hoa thường.
   Chưa yêu cầu tìm không dấu; muốn hỗ trợ phải bổ sung quy tắc riêng.
3. **JS3:** cập nhật một task theo id mà không sửa array và object gốc.
4. **JS4:** tính trung bình điểm đã chấm; giữ điểm 0, bỏ null, rỗng trả null.
5. **JS5:** dự đoán kết quả copy nông trước khi chạy, rồi tự tạo bản sao đúng mức.

Điều kiện qua: viết bằng tay, giải thích từng tham số/return, kiểm tra rỗng,
không tìm thấy, điểm 0 và không sửa dữ liệu đầu vào.

Tham khảo: [MDN JavaScript Guide](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide).

## Xưởng 1 — Giải phẫu cú pháp trước khi rút gọn

```javascript
function isPending(task) {
  return task.status === 'pending';
}
const selected = tasks.filter(isPending);
```

Đọc từng mảnh: function khai báo hàm; isPending là tên; task là tham số local;
ngoặc tròn chứa tham số/đối số tùy vị trí; ngoặc nhọn chứa khối lệnh; dấu chấm
đọc thuộc tính status; === trả boolean; return đưa boolean cho bên gọi.
`tasks.filter` đọc method trên array, `(isPending)` truyền giá trị hàm.
Không có `()` sau isPending ở đây vì bạn chưa gọi nó ngay.

```javascript
const selectedAgain = tasks.filter(function (task) {
  return task.status === 'pending';
});
const selectedShort = tasks.filter(task => task.status === 'pending');
```

Ba cách biểu diễn cùng predicate trong ví dụ này. Filter sẽ gọi callback với
mỗi phần tử, dùng kết quả truthy/falsy để quyết định giữ phần tử. Dấu `=>`
không nghĩa là “so sánh”; nó định nghĩa hàm. Khi thân là biểu thức, giá trị
được return ngầm. Khi thêm `{}`, cần return rõ.

| Cú pháp | Khi nào chạy | Giá trị đưa vào filter |
|---|---|---|
| `filter(isPending)` | Filter tự gọi từng lượt | Một hàm |
| `filter(task => isPending(task))` | Callback gọi isPending từng lượt | Một hàm |
| `filter(isPending(tasks[0]))` | Gọi ngay trước filter | Boolean, sai hợp đồng callback |

Viết lại bằng for để tự chứng minh cách nghĩ:

```javascript
const selectedByLoop = [];
for (const task of tasks) {
  const keep = isPending(task);
  if (keep) selectedByLoop.push(task);
}
```

## Xưởng 2 — Truy vết tìm kiếm không cần đoán

Hợp đồng: nhận array task và query string; trim query, không phân biệt
hoa/thường; query rỗng trả toàn bộ nội dung theo thứ tự; không sửa task gốc.

```javascript
function searchTasks(items, query) {
  const normalized = query.trim().toLowerCase();
  return items.filter(item => {
    const title = item.title.toLowerCase();
    return title.includes(normalized);
  });
}
```

Với query `' HÀM '`: normalized `'hàm'`; title `'hàm số'` → true;
title `'tích phân'` → false. Filter tạo array mới nhưng giữ chính object đã
khớp; nếu sửa selected[0].title thì object gốc có thể đổi. Tìm kiếm không dấu
là yêu cầu khác; cần normalize dấu và quy tắc riêng, không giả định lowerCase làm việc đó.

Tự test: query rỗng, toàn khoảng trắng, không khớp, hoa/thường, hai title
giống nhau và input rỗng. Nếu API có phân trang, tìm kiếm trên một trang local
không đồng nghĩa tìm toàn hệ thống. Khi đó gửi query cho server theo hợp đồng.

## Xưởng 3 — Template string, optional chaining và toán tử ba ngôi

```javascript
const user = { name: 'An', profile: null };
const greeting = `Chào ${user.name}`;
const avatar = user.profile?.avatarUrl ?? '/default-avatar.svg';
const score = 0;
const scoreLabel = score === null ? 'Chưa chấm' : `${score}/10`;
```

Backtick tạo template literal; `${...}` đưa biểu thức vào chuỗi. `?.` dừng
truy cập khi vế trái null/undefined; nó không tự validate một cấu trúc JSON lạ.
`condition ? a : b` là biểu thức chọn một trong hai giá trị. Không lồng nhiều
tầng ba ngôi nếu khó đọc; tách hàm hoặc if rõ.

`[]` dùng cho array hoặc truy cập key động; `{}` có thể là object literal
hoặc block tùy ngữ cảnh. `task => ({ id: task.id })` dùng ngoặc tròn để return
object literal, khác `task => { id: task.id }` là block không return object.

## Xưởng 4 — Module và thứ tự thực hiện

```javascript
// task-utils.js
export function taskLabel(task) {
  return `${task.id}: ${task.title}`;
}
```

```javascript
// main.js, chạy trong môi trường ESM
import { taskLabel } from './task-utils.js';
const format = taskLabel;
console.log(format({ id: 1, title: 'Hàm số' }));
```

Export/import nối module, không tự gọi hàm. Named export cần đúng tên; default
export là dạng khác. Browser module, Node ESM và Vite có quy tắc resolve khác;
trong repo, đọc package.json và config trước khi sửa extension theo cảm tính.

## Xưởng 5 — Closure và event handler

```javascript
function makeCounter() {
  let value = 0;
  return function increment() {
    value += 1;
    return value;
  };
}
const a = makeCounter();
const b = makeCounter();
console.log(a(), a(), b()); // 1, 2, 1
```

Hàm trả ra tiếp tục truy cập phạm vi lexical nơi được tạo. Hai lần gọi
makeCounter có hai value riêng. Trong React, handler cũng giữ giá trị/phạm vi
của lần render tạo nó; đây là cầu nối sang snapshot và dependency effect.

## Xưởng 6 — Promise trước async/await

```javascript
function loadExample(fail) {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      if (fail) reject(new Error('Không tải được'));
      else resolve({ title: 'Hàm số' });
    }, 20);
  });
}
async function run() {
  console.log('A');
  try {
    const task = await loadExample(false);
    console.log(task.title);
  } catch (error) {
    console.log(error.message);
  }
  console.log('B');
}
void run();
console.log('C');
```

Dự đoán: A → C → Hàm số → B. Await tạm dừng phần tiếp theo của run, không
dừng cả chương trình. Đổi false thành true: A → C → Không tải được → B.
Async luôn trả Promise; try/catch chỉ bắt rejection nếu đường đó được await
hoặc nối xử lý đúng. Viết `loadExample(true)` rồi bỏ Promise có thể tạo lỗi
không được xử lý. `void` biểu thị chủ ý bỏ giá trị, không tự xử lý rejection.

Chưa cần thuộc mọi hàng đợi event loop, nhưng phải biết code đồng bộ chạy
trước continuation sau await, thời điểm render có thể khác thời điểm request
hoàn tất và hai request có thể về ngược thứ tự gửi.

## Xưởng 7 — Bài điền, bài trắng và bài sửa lỗi

**Điền:** dùng vòng lặp viết `countByStatus(items, status)`; giữ 0 cho rỗng.

**Trắng:** viết `summarizeGrades` trả `{ gradedCount, average, highest }`.
Input chỉ gồm number0..10 hoặc null; chưa có điểm thì average/highest null.
Định nghĩa cách xử lý input sai trước khi mở lời giải.

**Sửa lỗi:** tìm cả hai lỗi trong hàm sau:

```javascript
function brokenAverage(scores) {
  const graded = scores.filter(Boolean);
  return graded.reduce((sum, score) => sum + score) / scores.length;
}
```

<details><summary>Đối chiếu sau khi đã viết test</summary>

Có hơn hai điểm cần xét: Boolean loại0; mẫu số dùng sai tập; reduce không có
initial value sẽ lỗi với rỗng; chưa xử lý không có điểm. Test `[0,null,10]`,
`[null]`, `[]`, `[0]`. Hàm đúng phải giữ0, bỏnull, có accumulator ban đầu và
xử lý rỗng theo hợp đồng. Sau sửa, tự thêm weighted average với hợp đồng trọng số.

</details>

Qua xưởng khi tự làm được biến thể và giải thích từng callback, tham số,
return, biến local, tham chiếu và đường bất đồng bộ. Kết quả Console đúng một
lần chưa thay cho các test biên.
