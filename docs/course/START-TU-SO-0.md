# S0 — Chưa biết cú pháp: bắt đầu từ một dòng

Mày đã biết biến/if/for/hàm trong Python. Bài này là chỗ ôn nhanh cách viết
tương ứng trong JavaScript khi còn vướng ký hiệu. Ta tập trung vào: **JavaScript**, vì sau này dùng nó để điều khiển giao diện.
Chưa học nhiều ngôn ngữ cùng lúc. Mục tiêu đầu tiên chỉ là hiểu và tự sửa vài dòng.

Mỗi mục nhỏ: đọc → đoán → gõ lại → đổi một chỗ → nói vì sao kết quả đổi.
Không cần học hết trong một buổi. Nếu chưa giải thích được dấu nào, dừng tại dấu đó.

## 1. Code là chỉ dẫn; cú pháp là cách viết chỉ dẫn

Tiếng Việt có “lấy 2 cộng 3 rồi cho tao xem kết quả”. Code phải viết theo
quy tắc mà chương trình đọc hiểu được. Quy tắc viết đó gọi là **cú pháp**.
Máy không đoán ý khi thiếu một dấu hoặc tên bị viết sai.

Đừng mở project lớn ngay. Trong sách chọn **Phòng thực hành → Gõ những dòng đầu**.
Ô luyện nhận một phần cú pháp nhỏ của JavaScript, hiển thị kết quả và bảng theo
dõi biến. Nó không chạy file dự án, không gửi mạng và không sửa dữ liệu thật.

**Hôm nay chỉ cần mục 2–7:** hiểu cách hiển thị, tạo một tên giữ số và đổi số đó.
Các mục sau để học tiếp khi phần trước đã tự làm được.

## 2. Một dòng đầu tiên: cho máy hiển thị số

```javascript
console.log(2);
```

Đọc nguyên câu: “Dùng thao tác log của công cụ console để hiển thị số 2”.

| Phần đang nhìn | Đọc thế nào? | Nó làm gì ở dòng này? |
|---|---|---|
| `console` | Tên công cụ hiển thị thông tin | Có sẵn trong môi trường JavaScript đang học |
| `.` | Dấu chấm | Chọn một thao tác thuộc công cụ đó |
| `log` | Tên thao tác hiển thị | Chưa chạy chỉ vì viết tên; phần `(...)` gọi nó |
| `(` và `)` | Ngoặc tròn mở/đóng | Bao phần mình đưa cho thao tác |
| `2` | Số hai | Dữ liệu muốn hiển thị |
| `;` | Chấm phẩy | Kết thúc câu lệnh này |

Kết quả hiển thị là `2`. Gõ lại rồi chỉ đổi `2` thành `9`. Đừng đổi cả tên
console/log khi đang thử số. JavaScript phân biệt hoa/thường: `Console` khác `console`.

Chưa cần thuộc lòng mọi thứ về console. Trước mắt, hiểu `console.log(...)` là
cách nhìn một giá trị. Về sau mới tự viết thao tác của mình, gọi là hàm.

## 3. Cho máy tính rồi hiển thị

```javascript
console.log(2 + 3);
```

Máy tính phần trong ngoặc trước: `2 + 3` cho `5`. Sau đó log hiển thị `5`.
Dấu `+` ở giữa hai số là cộng. `2 + 3` được gọi là **biểu thức**: phần code
tính ra một giá trị. Không hiển thị nguyên chữ `2 + 3` trong ví dụ này.

Tự đoán rồi thử `console.log(4 + 1);`. Bài tự viết: hiển thị kết quả 8 bằng
một phép cộng do mày chọn. Đóng lời giải rồi gõ lại, không chỉ bấm sao chép.

## 4. Số khác chữ: dấu nháy giữ một đoạn văn bản

```javascript
console.log('An');
console.log('2 + 3');
```

Một cặp `'...'` giữ **chuỗi**, tức văn bản. Dòng đầu hiển thị An; dòng sau
hiển thị đúng chữ `2 + 3`, không tính cộng. Dấu nháy là phần code bao văn bản,
thường không được log hiển thị thành một phần của chữ.

Có thể dùng `"An"` thay `'An'`, nhưng dấu mở/đóng phải khớp. Dấu nháy cong
`‘ ’` từ trình soạn văn bản khác dấu nháy thẳng `'` trong code.

| Đoạn | Là gì? |
|---|---|
| `7` | Số, dùng tính toán |
| `'7'` | Chuỗi gồm một chữ số |
| `'diem'` | Chuỗi bốn chữ cái, không đọc biến diem |
| `diem` | Tên cần được khai báo trước khi dùng |

Tự viết dòng hiển thị tên mình. Tự viết thêm dòng hiển thị đúng chữ `2 + 3`.

## 5. Biến: đặt một tên để đọc lại giá trị

```javascript
let diem = 7;
console.log(diem);
```

Đọc dòng đầu: “Tạo biến tên diem, gắn giá trị ban đầu là số 7”.
**Biến** là một tên để chương trình đọc và, khi được phép, đổi giá trị.

| Phần | Ý nghĩa |
|---|---|
| `let` | Từ khóa dùng tạo biến có thể gán lại |
| `diem` | Tên mình đặt, chưa phải từ khóa JavaScript |
| `=` | Gán giá trị bên phải vào biến bên trái |
| `7` | Giá trị ban đầu |
| `;` | Kết thúc câu lệnh |

Dòng hai đọc tên diem nên lấy số 7 để hiển thị. Nếu viết `'diem'` trong dấu
nháy, máy hiển thị chữ diem. Dùng một tên đơn giản, không dấu, không khoảng
trắng như diem hoặc soBai khi mới học; không bắt đầu tên bằng chữ số.

Bài tự viết: tạo `soBai` bằng 3 rồi hiển thị nó. Tự đổi tên ở cả chỗ tạo và
chỗ đọc. Nếu chỉ đổi một chỗ, máy không tự biết hai tên là cùng ý của mày.

## 6. Đổi giá trị và hiểu dấu bằng

```javascript
let diem = 7;
diem = 8;
console.log(diem);
```

Dòng 1 tạo biến. Dòng 2 đổi biến đã có; không viết thêm let mỗi lần đổi.
Dòng 3 đọc giá trị hiện tại nên hiển thị 8. Dấu `=` ở đây là một hành động
gán, không phải câu khẳng định hai vế bằng nhau như phương trình toán.

| Sau dòng | diem đang giữ gì? | Có gì được hiển thị? |
|---|---|---|
| 1 | 7 | Chưa có |
| 2 | 8 | Chưa có |
| 3 | 8 | 8 |

Chỉ tạo/đổi biến không tự hiển thị. Nếu không có dòng log, ô kết quả có thể
trống dù chương trình đã chạy đúng. Nhìn bảng biến để biết điều đã thay đổi.

## 7. Đọc vế phải trước: diem = diem + 1

```javascript
let diem = 7;
diem = diem + 1;
console.log(diem);
```

Dòng 2 gồm ba việc theo thứ tự:

1. Đọc diem ở bên phải: hiện là 7.
2. Tính `7 + 1`, được 8.
3. Gán kết quả 8 vào diem ở bên trái.

Không có chuyện giải phương trình `diem = diem + 1`. Máy làm một lần cập
nhật giá trị. Sau dòng 2, diem là 8. Dòng 3 hiển thị 8.

**Dừng buổi đầu tại đây nếu cần.** Đóng code mẫu, tự viết biến soBai bằng 2,
tăng nó thêm 1 rồi hiển thị. Nói được vì sao kết quả là 3 mới học tiếp.

## 8. const: tên không được gán lại

```javascript
const ten = 'An';
console.log(ten);
```

`const` cũng tạo biến, nhưng không cho gán lại tên đó. `ten = 'Bình';` sau
khai báo trên sẽ gây lỗi. Dùng let trong bài cần cập nhật diem; dùng const
khi không định gán lại. Chưa cần học object ở bước này.

Giới hạn cần nhớ khi học tiếp: const không tự làm mọi dữ liệu bên trong một
object bất biến. Chương JavaScript giải thích phần đó sau khi đã biết object.

## 9. Phép tính, ngoặc và kiểu dữ liệu

```javascript
console.log(2 + 3 * 4);
console.log((2 + 3) * 4);
console.log('2' + 1);
```

`*` là nhân, `/` là chia, `-` là trừ. Nhân/chia được tính trước cộng/trừ.
Ngoặc tròn bên trong ép tính phần đó trước: hai dòng đầu lần lượt cho 14 và20.

Dòng cuối có chuỗi `'2'`; phép cộng với chuỗi này nối chữ nên cho `'21'`,
không phải 3. **Kiểu dữ liệu** nói giá trị là số, chuỗi hay loại khác. Đừng
nhìn một chữ số rồi mặc định đó là số. Chưa cần ép kiểu hay form ở bài này.

Bài tự viết: cùng hai số 4 và2, hiển thị tổng, hiệu, tích, thương ở bốn dòng.

## 10. So sánh: tạo một giá trị đúng hoặc sai

```javascript
let diem = 7;
console.log(diem === 7);
console.log(diem > 8);
```

`===` hỏi hai giá trị có bằng nhau nghiêm ngặt không. `>` hỏi lớn hơn không.
Hai dòng log cho `true` và `false`, nghĩa là đúng và sai. Đây là **boolean**,
không phải chuỗi `'true'` hoặc `'false'`.

| Ký hiệu | Đọc thành lời |
|---|---|
| `=` | Gán giá trị |
| `===` | So sánh bằng nhau nghiêm ngặt |
| `!==` | So sánh không bằng nhau nghiêm ngặt |
| `>` và `<` | Lớn hơn và nhỏ hơn |
| `>=` và `<=` | Lớn hơn hoặc bằng; nhỏ hơn hoặc bằng |

Ví dụ `7 === '7'` là false: một bên số, một bên chuỗi. Chưa dùng `==` khi
mới học để tránh đưa thêm quy tắc chuyển kiểu vào đầu cùng lúc.

## 11. Học đọc lỗi bằng một chỗ sai nhỏ

| Mã lỗi để thử | Chỗ cần nhìn | Cách sửa trong bài |
|---|---|---|
| `console.log('An);` | Nháy mở không có nháy đóng | Viết `'An'` |
| `console.log(2;` | Ngoặc mở không đóng | Viết `console.log(2);` |
| `console.log(Diem);` sau khi tạo diem | Hoa/thường không khớp | Đọc đúng tên diem |
| Gán lại biến khai báo const | Quy tắc gán lại | Giữ const hoặc chọn let nếu cần đổi |
| `let diem = 7; let diem = 8;` | Khai báo cùng tên hai lần | Dòng sau chỉ gán `diem = 8;` |

Trong bộ luyện, viết `;` cho từng câu lệnh. JavaScript đầy đủ có quy tắc có
thể tự chèn chấm phẩy; bộ luyện nhỏ cố ý yêu cầu viết rõ và sẽ báo khi thiếu.
Nó chưa nhận if, vòng lặp, hàm, array/object hay mọi cú pháp JavaScript.

Mỗi lần sửa một lỗi, ghi “đã đoán gì → máy báo gì → sửa ký hiệu nào”. Không
cần hiểu toàn bộ thông báo lỗi của một project lớn ngay bây giờ.

## 12. Đường đi tiếp theo — chưa cần mở project lớn

Khi tự viết được các bài trên, học tiếp từng bước trong [JavaScript](01-javascript.md):

| Thứ tự | Ý mới | Chỉ học khi |
|---|---|---|
| 1 | if/else: chọn có chạy một nhóm lệnh không | Đã hiểu biểu thức true/false |
| 2 | Array: giữ danh sách và đọc một phần tử | Đã đọc được một biến |
| 3 | for: làm lại một nhóm lệnh cho các phần tử | Đã hiểu thứ tự và cập nhật biến |
| 4 | function/return: đặt tên việc làm và trả kết quả | Đã viết được vài lệnh theo thứ tự |
| 5 | Object: dữ liệu có các mục được đặt tên | Đã phân biệt tên với chuỗi |
| 6 | Callback: đưa một hàm cho hàm khác sử dụng | Đã tự gọi và trả kết quả từ hàm |

Sau đó mới học [tư duy bài toán tổng hợp](17-tu-duy-lap-trinh.md), TypeScript,
HTML/CSS, React; rồi Python, API, SQL và hệ thống. Bài đọc login và P0–P5 là
đích về sau, không phải việc đầu tiên của người chưa biết cú pháp.

## 13. Tự kiểm bằng bài nhỏ, không bằng số trang đã đọc

Đóng lời giải. Tự tạo một biến soBai bằng 2, tăng thêm 1, hiển thị số mới và
hiển thị kết quả so sánh số mới có bằng 3 không. Đầu ra phải là 3 và true.

<details><summary>Mở sau khi tự gõ thử</summary>

```javascript
let soBai = 2;
soBai = soBai + 1;
console.log(soBai);
console.log(soBai === 3);
```

Tự đọc từng dấu: let tạo tên; = gán; + cộng; console.log hiển thị; (...) chứa
giá trị đưa vào; === so sánh; ; kết thúc câu. Đổi số ban đầu thành 5 rồi dự đoán
cả hai dòng output. Nếu chỉ nhớ đáp án 3/true mà không giải thích được, làm lại
bài với số khác và chưa chuyển chương.

</details>
