# F0 — Biết Python, học JavaScript rồi TypeScript

Điểm xuất phát của mày: biết biến, if, for và hàm trong Python; chưa tự viết
JavaScript. Ta giữ lại cách nghĩ đã có, học cách biểu diễn trong ngôn ngữ mới.
Chưa cần quay lại học “biến là gì” từ đầu, chưa cần React/HTTP ở bài này.

Mỗi mục chỉ đối chiếu một việc. Đọc bản Python quen thuộc, viết bản JavaScript,
đoán output rồi chạy. Sau đó mới thêm kiểu của TypeScript vào code đã hiểu.

## 1. Ba thứ đang gặp là gì?

| Tên | Việc nó làm | Ví dụ |
|---|---|---|
| JavaScript (JS) | Ngôn ngữ chạy logic | Cộng điểm, lọc danh sách, xử lý sự kiện |
| TypeScript (TS) | Thêm hệ thống kiểu để kiểm code JS lúc viết/build | Tham số phải là number, object cần title |
| HTML/CSS | Nội dung/cấu trúc và cách trình bày trang | Nút, ô nhập, màu, khoảng cách, bố cục |

Python không tự đổi thành JavaScript khi viết cùng ý. TypeScript cũng không
thay cách JS thực thi một phép cộng. Ta học JS trước để hiểu phần thật sự chạy.
HTML/CSS đi ở bài F1; chưa trộn cả bốn thứ trong cùng một đoạn React.

## 2. Biến và hiển thị: đối chiếu đúng một việc

Python:

```python
score = 7
score = score + 1
print(score)
```

JavaScript:

```javascript
let score = 7;
score = score + 1;
console.log(score);
```

Hai đoạn cho8. Ý tưởng không mới: đọc giá trị cũ, cộng1, gán lại, hiển thị.
Điểm mới là `let` lúc khai báo, `console.log` thay print và cách dùng `;`.
Dùng const khi không gán lại tên; const không đóng băng mọi object bên trong.

Chưa chạy được file JS? Theo bộ công cụ tạo file học `.js` rồi chạy `node ten-file.js`
trong thư mục đó. Ô luyện S0 chạy được ví dụ nhỏ này mà chưa cần cài thêm; nó
chưa chạy được các ví dụ array/if/function bên dưới. Không dán TS vào ô luyện S0.

### Tách câu lệnh trước khi chạy

> [!KEY]
> `let score = 7;` là **khai báo**; `score + 1` là **biểu thức**;
> `console.log(score);` là **lời gọi được dùng như câu lệnh**. Đặt tên đúng
> loại giúp hiểu chỗ nào cần một giá trị và chỗ nào thực hiện một việc.

Nếu thấy `score = score + 1`, che vế trái trước: đọc score cũ → cộng → ghi
lại. Đừng dịch từng dấu bằng ý nghĩa trong toán học.

> [!TASK]
> Đóng hai đoạn trên. Viết JS giữ số bài là 3, thêm 2, rồi hiển thị. Viết
> bảng hai cột “sau dòng / số bài”. Sau đó đổi ban đầu thành 0.

> [!CHECK]
> Hai lần phải ra 5 và 2. Chỉ được đâu là tên tự đặt, đâu là từ khóa/API có sẵn.

## 3. if: đổi dấu và cách viết khối

Python:

```python
score = 7
if score >= 5:
    print('Đạt')
else:
    print('Chưa đạt')
```

JavaScript:

```javascript
const score = 7;
if (score >= 5) {
  console.log('Đạt');
} else {
  console.log('Chưa đạt');
}
```

Python dùng `:` và thụt lề để xác định khối; JS dùng `(điều kiện)` và `{...}`.
Vẫn thụt lề để đọc, nhưng không bỏ ngoặc nhọn vì nghĩ thụt lề đã đủ.

| Python quen thuộc | JS dùng ở khóa này | Chú ý |
|---|---|---|
| True / False | true / false | Khác chữ hoa/thường |
| a == b | a === b | Không tương đương mọi đối tượng; đây là so sánh nghiêm ngặt của JS |
| and / or / not | && / <code>&#124;&#124;</code> / ! | Cần học short-circuit, không thay chữ máy móc |
| None | null hoặc undefined tùy hợp đồng | JS có hai khái niệm, không phải một bản dịch duy nhất |

Tự đổi score thành4. Viết nhánh cho score bằng0 mà không nhầm0 với thiếu điểm.

### Một lỗi để tự phát hiện

`if (score = 5)` **gán** 5, rồi kiểm truthiness của 5; nó không hỏi có bằng
5 không. Với số trong bài này, câu hỏi bằng dùng `score === 5`. Biến const
thì phép gán còn có thể ném lỗi khi chạy. Luôn đọc toán tử trước khi tin nhánh.

> [!TASK]
> Tự viết hàm phân loại: dưới 0 hoặc trên 10 là không hợp lệ; từ 5 là đạt;
> còn lại chưa đạt. Dùng if/else và tự chọn thứ tự kiểm.

> [!CHECK]
> Chốt kết quả cho -1, 0, 4, 5, 10, 11 trước khi chạy. Nếu 0 bị coi là thiếu
> hoặc 11 được coi đạt, kiểm thứ tự nhánh. Chưa dùng thư viện form.

## 4. List/dict quen thuộc và array/object của JS

Python:

```python
scores = [7, 8, 9]
student = {'name': 'An', 'score': 7}
print(len(scores), scores[0], student['name'])
```

JavaScript:

```javascript
const scores = [7, 8, 9];
const student = { name: 'An', score: 7 };
console.log(scores.length);
console.log(scores[0]);
console.log(student.name);
```

Đừng mặc định API giống nhau: JS array đọc `.length`, không gọi `len(scores)`
hay `scores.length()`. `student.name` đọc thuộc tính; `.name` không phải method
vì không có `()`. Cũng có thể đọc `student['name']` khi cần key dạng chuỗi.

Không phải mọi dict đều nên đổi thành object; khi cần map khóa động có thể
xem Map sau. Trước mắt dùng object cho một bản ghi và array cho danh sách.

### Đọc hình dạng trước tên hàm

`student['name']` có ba bước: đọc object student → chọn key chuỗi name →
nhận giá trị. `students[0].name` thêm bước lấy phần tử đầu của array trước.
Array rỗng thì `students[0]` là undefined, đọc tiếp `.name` gây lỗi.

> [!TASK]
> Tự tạo hai học sinh dưới dạng array object. Đọc tên học sinh thứ hai; đổi
> điểm người thứ nhất thành 0. Ghi hình dạng bằng lời: “danh sách các bản ghi”.

> [!CHECK]
> Phân biệt `students.length`, `students[1]` và `students[1].name`: số lượng,
> một bản ghi, một chuỗi. Đừng dùng cả object khi cần một tên.

## 5. for: cùng thuật toán, khác cách lấy phần tử

Python:

```python
total = 0
for score in [7, 8]:
    total = total + score
print(total)
```

JavaScript:

```javascript
let total = 0;
for (const score of [7, 8]) {
  total = total + score;
}
console.log(total);
```

Cả hai cho15. `for...of` đọc giá trị phần tử. Không thay bằng `for...in` và
nghĩ nó giống Python `in`: JS for...in duyệt tên thuộc tính/key, có nghĩa khác.
Tự chạy với danh sách rỗng rồi giải thích vì sao total vẫn0.

### Theo đúng một lượt

Trước vòng: total = 0. Lượt đầu score = 7 → total = 7. Lượt sau score = 8 →
total = 15. Biến score là **một giá trị mỗi lượt**, không phải cả danh sách.

> [!TASK]
> Viết hàm nhận array điểm, đếm số điểm từ 5 trở lên bằng for...of và if.
> Tự đặt tên biến đếm; không dùng filter trong lần đầu.

> [!CHECK]
> `[]` → 0; `[0, 5, 8]` → 2; `[5]` → 1. Giải thích vì sao return phải
> nằm sau vòng lặp và vì sao tổng điểm không đồng nghĩa số người đạt.

## 6. Hàm trước, mũi tên sau

Python:

```python
def add_one(number):
    return number + 1
result = add_one(7)
```

JavaScript dạng đầy đủ:

```javascript
function addOne(number) {
  return number + 1;
}
const result = addOne(7);
console.log(result);
```

Tên hàm được đặt theo quy ước ngôn ngữ; không có quy tắc bắt buộc add_one phải
đổi thành addOne mới chạy. `return` vẫn trả kết quả cho caller. Định nghĩa khác
lời gọi; dùng `addOne` là lấy giá trị hàm, dùng `addOne(7)` là gọi hàm với7.

Khi đã tự viết dạng trên, đọc dạng mũi tên:

```javascript
const addOne = (number) => {
  return number + 1;
};
```

Ở đây `=>` định nghĩa hàm, không phải so sánh. Hai snippet addOne độc lập,
không dán khai báo trùng tên vào cùng scope. Dạng `number => number + 1` là
viết gọn có return ngầm khi thân là biểu thức; `{...}` thì cần return rõ.

### Ba cách viết cần tự phân biệt

| Cách viết | Máy nhận gì? |
|---|---|
| `addOne` | Giá trị hàm; có thể giao cho người khác gọi |
| `addOne(7)` | Kết quả của lần gọi với 7 |
| `(number) => number + 1` | Một hàm mới được viết ngay tại chỗ |

`const makeLabel = (name) => ({ title: name });` trả object. Ngoặc tròn bao
object để không bị đọc là thân khối. Nếu đổi sang `=> { ... }`, tự thêm
return. Dấu ngoặc không phải đồ trang trí.

> [!TASK]
> Tự viết hàm nhận một tên lớp, trả object có title là tên đó và archived là
> false. Viết dạng function trước, rồi tự chuyển sang arrow.

> [!CHECK]
> Gọi bằng Toán phải nhận object, không phải undefined. Đọc được vì sao có
> hai cặp ngoặc với vai trò khác nhau; không nhớ bằng hình dạng cả đoạn.

## 7. Callback và map: không bắt nhớ một tên hàm lạ

Python đã có cách tạo list mới:

```python
scores = [7, 8]
next_scores = [score + 1 for score in scores]
```

JS có thể viết bằng vòng lặp trước; rồi học `map` theo hợp đồng:

```javascript
function addOne(number) {
  return number + 1;
}
const scores = [7, 8];
const nextScores = scores.map(addOne);
console.log(nextScores);
```

map là method của array. Nó nhận một hàm, gọi hàm đó cho từng phần tử rồi tạo
array kết quả. `addOne` được truyền vào; không gọi sớm thành `addOne()`.
Lượt1 đưa7 vào hàm, nhận8; lượt2 đưa8, nhận9; kết quả `[8, 9]`.

Đọc `scores.map(score => score + 1)` sau cùng: chỉ thay cách viết callback,
không thay hợp đồng của map. Filter là việc khác: callback quyết định giữ/bỏ.

### Callback không phải “hàm tự chạy”

`scores.map(addOne)` gọi map ngay; map là bên sẽ gọi addOne từng lượt.
`scores.map(addOne(7))` lại gọi addOne trước, được số 8, rồi cố đưa số làm
callback. Nhìn **bên nào gọi, khi nào gọi, đưa gì vào**.

> [!TASK]
> Với cùng array, tự viết ba việc riêng: map thành nhãn điểm, filter giữ điểm
> đạt, find lấy điểm đạt đầu tiên. Trước mỗi API, viết kết quả mong đợi bằng tay.

> [!CHECK]
> map giữ số phần tử; filter trả array; find có thể trả undefined. Mở Tra
> hàm/tool để kiểm hợp đồng nếu chưa chắc, đừng đoán theo tên.

## 8. Giờ mới thêm kiểu TypeScript

JS đã chạy được:

```javascript
function addOne(number) {
  return number + 1;
}
```

TS ghi rõ hợp đồng:

```typescript
function addOne(number: number): number {
  return number + 1;
}
const result: number = addOne(7);
```

| Mảnh mới | Nghĩa |
|---|---|
| number trước dấu : | Tên tham số, mình đặt |
| : number sau tên tham số | Yêu cầu tham số thuộc kiểu số |
| : number sau ) | Kiểu kết quả hàm trả về |
| : number sau result | Kiểu của biến result |

Trong ví dụ, tên tham số number trùng tên kiểu number chỉ để minh họa; có thể
đổi tên thành score cho đỡ nhầm. TS thường tự suy ra kiểu result, không phải
biến nào cũng cần tự ghi annotation. Dấu kiểu không tự biến chuỗi thành số.

### Dấu kiểu không tham gia phép tính

> [!KEY]
> `score: number` nói **mong đợi kiểu số**; `Number(text)` mới là một lời gọi
> chuyển đổi giá trị khi chạy. TypeScript không thay một chuỗi thành số hộ mày.

> [!TASK]
> Tự viết hàm tính tổng hai số bằng JS; kiểm 2 và 3. Sau đó thêm kiểu cho hai
> tham số và return. Cố gọi với chuỗi để đọc thông báo lỗi kiểu.

> [!CHECK]
> Chỉ được phần annotation bị bỏ khỏi JavaScript được build. Phân biệt lỗi
> kiểu với trường hợp phép cộng chuỗi chạy được nhưng cho kết quả ngoài ý muốn.

## 9. Đọc object type từ dữ liệu trước

Dữ liệu JS:

```javascript
const student = { name: 'An', score: 7 };
```

Mô tả kiểu TS:

```typescript
type Student = {
  name: string;
  score: number;
};
const student: Student = { name: 'An', score: 7 };
```

`type` tạo tên cho kiểu, không tự tạo student thật. `name: string` mô tả mục
name là chuỗi; `name: 'An'` ở object là dữ liệu có giá trị An. Nhìn context
để phân biệt hai dấu `:`; không học bằng cách dịch một ký hiệu thành một nghĩa.

Sau đó mới đến `Student[]`, `number | null`, thuộc tính `note?: string` ở
chương02. Chưa cần generic, React props hoặc Promise trong buổi đầu.

### Hai dấu hai chấm, hai công việc

`title: string` trong type mô tả kiểu; `title: name` trong object lấy **giá trị
của biến name** làm dữ liệu. Type không tự tạo object, không tự gọi server.

> [!TASK]
> Tự định nghĩa ClassInput có title chuỗi và capacity số. Tạo một dữ liệu hợp
> lệ, rồi cố bỏ capacity. Sau đó thử title toàn khoảng trắng.

> [!CHECK]
> TS bắt thuộc tính thiếu, nhưng chuỗi trắng vẫn đúng kiểu string. Mày cần
> một bước kiểm quy tắc lúc chạy; đây là lý do validation không biến mất.

## 10. Kiểu khi viết khác dữ liệu khi chạy

TypeScript giúp báo lỗi dùng sai kiểu trong code được kiểm. Server trả JSON
sai vẫn có thể xảy ra; `as Student` không sửa hay xác minh JSON. Tới chương02
mới học parser và Zod. Cũng đừng dùng any để bỏ qua lỗi chưa hiểu.

Môi trường repo đã có TypeScript/Vite; dùng lệnh build của frontend để kiểm
kiểu theo cấu hình hiện tại. Không đưa cú pháp `: number` thẳng vào Console
JavaScript hay file .js rồi nghĩ lỗi là do chưa cài React.

## 11. Buổi học đầu tiên đúng với mức hiện tại

1. Chọn đúng một mục từ2–6, tự viết JS cho bài Python tương ứng.
2. Chạy, so kết quả và ghi ký hiệu mới khác Python.
3. Tự đổi input: score0, list rỗng, tên khác hoặc số khác.
4. Chỉ khi làm được JS mới thêm kiểu TS ở mục8–9.

Không cần xem hết một lần. Khi gặp tên method/thư viện lạ, dùng
[F2 — Đọc hàm/tool](F2-doc-ham-va-tool.md) và nút **Tra hàm/tool** trong khối code.
Sau bài này, đi vào JavaScript chi tiết/chương02; phần UI bắt đầu ở
[F1 — HTML/CSS](F1-html-css-tu-dau.md), không nhảy thẳng vào dashboard Tailwind.

## 12. Bài tự viết và bằng chứng hiểu

Viết Python trước: nhận một list số, trả list các số từ5 trở lên. Sau đó tự
viết JS bằng for...of và if; rồi mới thử filter. Cuối cùng thêm kiểu TS cho
tham số và kết quả. Test `[0, 5, 8]` cho `[5, 8]`, rỗng cho rỗng.

Giải thích được vì sao dùng of, hàm nào được gọi, dữ liệu nào là array và kiểu
nào biến mất khi build. Nếu chỉ nhận ra code mẫu, viết lại bằng số/input khác.

Tham khảo đúng chỗ khi cần: [JS Guide](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide),
[TS cho người biết JS](https://www.typescriptlang.org/docs/handbook/typescript-in-5-minutes.html),
[TS everyday types](https://www.typescriptlang.org/docs/handbook/2/everyday-types.html).

## 13. Destructuring: lấy phần nào, đổi tên phần nào?

Trong Python mày có thể gán nhiều biến từ tuple. JS còn lấy thuộc tính object
bằng cú pháp sau. Đọc từ dữ liệu gốc trước:

```javascript
const student = { name: 'An', score: 0 };
const { name, score: currentScore } = student;
```

| Mảnh | Nghĩa ở đúng vị trí này |
|---|---|
| `const { ... } = student` | Khai báo tên bằng cách lấy thuộc tính từ object |
| `name` | Lấy student.name, đặt tên biến là name |
| `score: currentScore` | Lấy student.score, đặt tên biến là currentScore |

Dấu hai chấm ở đây **đổi tên khi lấy dữ liệu**, không tạo thuộc tính mới và
không phải annotation kiểu. Sau dòng đó có name và currentScore; không tự
khai báo biến score. Với array, `const [first, second] = items;` lấy **theo
vị trí**. Với object, lấy **theo tên key**.

> [!TASK]
> Tạo object lớp có id, title, teacher_id. Tự lấy title và đổi teacher_id
> thành teacherId. Không sửa tên key của object gốc.

> [!CHECK]
> Object gốc vẫn có teacher_id; biến teacherId giữ cùng giá trị. Giải thích
> vì sao `const { teacherId } = classroom` không tự đọc teacher_id.

## 14. Spread, rest và bản sao nông

```javascript
const original = { title: 'Toán', archived: false };
const changed = { ...original, archived: true };
```

`...original` trải các thuộc tính riêng enumerable vào object mới. Viết
archived phía sau thì giá trị phía sau ghi đè. Đổi thứ tự thành
`{ archived: true, ...original }` sẽ bị archived từ original ghi đè trở lại.

> [!KEY]
> Đây là **bản sao nông**: object ngoài mới, object lồng bên trong vẫn có thể
> dùng chung tham chiếu. const cũng không đóng băng object.

Ở khai báo hàm `function collect(...items) { return items; }`, ba chấm lại là
**rest parameter**, gom đối số thành array. Cùng dấu, ngữ cảnh khác: trải giá
trị khi dùng; gom giá trị khi khai báo tham số.

> [!TASK]
> Tạo lớp có settings là object lồng. Thử sao nông rồi sửa settings; quan sát
> original. Sau đó tự tạo cả settings mới để tránh sửa dữ liệu cũ.

> [!CHECK]
> Giải thích bằng hai tầng object. Đừng kết luận mọi spread là deep copy.

## 15. Import/export: tên đến từ đâu?

```javascript
export function isPassing(score) {
  return score >= 5;
}
```

Đoạn trên nằm trong file module riêng. File khác dùng named import:
`import { isPassing } from './grades.js';`. Ngoặc nhọn ở import là danh sách
binding được import, không phải tạo object hay destructuring thông thường.
Tên export phải khớp; đường dẫn tương đối tính từ **file đang import**.

`export default` có quy tắc import khác: không có ngoặc nhọn và caller được
chọn tên. Đừng thêm/bỏ ngoặc chỉ để hết báo đỏ; tra file export thật. Trong
repo, `import type` là TypeScript chỉ lấy tên dùng trong kiểu; build bỏ import
chỉ có vai trò kiểu. Import React không làm Python hoặc SQL chạy trong browser.

> [!TASK]
> Tách hàm lọc điểm tự viết sang module khác, tự viết named export/import.
> Dùng bài web G1 để chạy bằng browser module; Node cần cấu hình module phù hợp.

> [!CHECK]
> Cố viết sai tên export rồi đọc lỗi. Nêu file entry, file nhận import và vì
> sao đường dẫn không tính từ terminal.

## 16. Khi chưa tự viết được, quay về mảnh nhỏ nào?

Đọc một dòng repo theo thứ tự: **tên đang có trong scope → cấu trúc cú pháp →
API được gọi → giá trị trả → nơi dùng kết quả**. Ví dụ useState vừa có cú pháp
lấy hai phần tử của JS, vừa có hợp đồng hook của React. Học hai lớp riêng.

Chỉ dùng các mục 13–15 khi gặp trong G1/G2; không cần nhồi hết trước buổi web
đầu. Trong tab **Cú pháp & kiến trúc**, tự viết bản nháp trước, chạy bằng môi
trường bài rồi ghi kết quả. Ô luyện S0 chỉ chạy tập con rất nhỏ đã ghi rõ.
