# 01 — JavaScript: cú pháp và tư duy xử lý dữ liệu

Mục tiêu: tự viết hàm xử lý nhiệm vụ trước khi đưa vào React.
Ví dụ này chạy độc lập trong Node hoặc Console; chưa sửa dashboard thật.

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

```javascript
function canShowFeedback(status) {
  if (status === 'graded') return true;
  return false;
}

const score = 0;
console.log(score || 'Chưa chấm'); // sai ý nghĩa: 0 bị coi là falsy
console.log(score ?? 'Chưa chấm'); // 0: chỉ thay null hoặc undefined
```

`===` so sánh nghiêm ngặt. `&&`, `||` có short-circuit và có thể trả giá trị
không phải boolean. `??` có ích khi 0 là điểm hợp lệ. `if`/`else` biểu diễn nhánh;
return sớm giúp tránh nhiều tầng lồng nhau, nhưng phải giữ tên điều kiện dễ hiểu.

## Bài 01.3 — Hàm, tham số, trả về, scope

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

## Bài 01.4 — Object, array, destructuring và callback

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
