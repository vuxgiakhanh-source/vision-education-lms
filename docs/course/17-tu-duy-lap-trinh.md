# Từ một yêu cầu tiếng Việt thành chương trình

Bài này dùng nhánh, vòng lặp và hàm. Nếu các ký hiệu còn lạ, học
[S0 — Chưa biết cú pháp](START-TU-SO-0.md) rồi các mục tương ứng của
[JavaScript](01-javascript.md) trước. “Chốt bài toán trước khi chọn cú pháp”
không có nghĩa bắt người chưa biết code đọc ngay một hàm dài.

## 1. Máy thực hiện chỉ dẫn, người viết quyết định ý nghĩa

“Đếm số bài chưa nộp” còn thiếu: đếm cho ai, bài nháp có tính không, đã quá hạn
có tính không, cùng bài trong hai lớp có trùng không? Đừng giải quyết bằng
`filter` trước khi chốt tập đầu vào và điều kiện thuộc tập kết quả.

Hợp đồng học nhỏ: đầu vào là danh sách task đã được backend cho phép đọc;
mỗi task có status pending/submitted/graded. Đếm pending. Rỗng cho 0; không
sửa input. Tại đây chưa xét quyền hoặc trạng thái quá hạn.

## 2. Biến là tên của một giá trị trong một thời điểm/phạm vi

```javascript
let count = 0;
count = count + 1;
console.log(count); // 1
```

Đọc dòng 2 từ phải sang trái về mặt tính toán: lấy count hiện tại là 0, cộng 1
thành 1, rồi gán lại vào tên count. `=` là chỉ dẫn gán. `===` là biểu thức so
sánh. Biểu thức sinh giá trị; câu lệnh tổ chức thực hiện. Không thể thay mọi
`if` bằng một biểu thức nếu việc đó làm người đọc không hiểu.

## 3. Viết thuật toán bằng lời

```text
Nhận tasks.
Đặt count bằng 0.
Với từng task trong tasks:
    Nếu task.status bằng pending:
        count tăng 1.
Trả count.
```

```javascript
function countPending(tasks) {
  let count = 0;
  for (const task of tasks) {
    if (task.status === 'pending') {
      count = count + 1;
    }
  }
  return count;
}
```

| Lượt | task.status | Điều kiện | count trước | count sau |
|---|---|---|---|---|
| 1 | pending | true | 0 | 1 |
| 2 | graded | false | 1 | 1 |
| 3 | pending | true | 1 | 2 |

Invariant: sau mỗi lượt, count bằng số pending trong phần đã duyệt. Khi vòng
lặp kết thúc, phần đã duyệt là toàn bộ input. Đây là một cách giải thích vì sao
thuật toán đúng, không chỉ dựa vào một ví dụ cho kết quả 2.

## 4. Hàm: hợp đồng nhỏ có thể gọi lại

```javascript
const total = countPending([
  { id: 1, status: 'pending' },
  { id: 2, status: 'graded' },
]);
```

`tasks` là tham số ở định nghĩa; array truyền tại lời gọi là đối số.
`total` nhận giá trị return sau khi hàm chạy. Nếu chỉ `console.log(count)` và
không return, bên gọi nhận undefined. Tên biến bên trong hàm không tự trở thành
biến ở hàm khác. Hãy vẽ riêng input, biến local và output.

## 5. Nhánh và bảng quyết định

Yêu cầu: cho đọc bài nếu tài khoản hoạt động và là chủ bài hoặc cô phụ trách.

```javascript
function canRead(active, owner, assignedTeacher) {
  return active && (owner || assignedTeacher);
}
```

| active | owner | assignedTeacher | Kết quả |
|---|---|---|---|
| false | true | true | false |
| true | false | false | false |
| true | true | false | true |
| true | false | true | true |

Ngoặc giữ ý nghĩa “phải active” cho cả hai nhánh. Thiếu ngoặc và viết sai quan
hệ có thể cho cô đã khóa đọc được dữ liệu. Trong sản phẩm, bảng này phải được
backend thực hiện với dữ liệu được xác minh, không tin boolean gửi từ client.

## 6. Chọn cấu trúc dữ liệu từ thao tác

| Nhu cầu | Cấu trúc đầu tiên nên thử | Lưu ý |
|---|---|---|
| Danh sách có thứ tự | array/list | Duyệt và lọc dễ; tìm lặp theo id có thể tốn |
| Một bản ghi có field | object/dict | Phân biệt field thiếu và field null |
| Tìm theo khóa | Map/dict | Chốt khóa duy nhất; tránh làm mất phần tử trùng |
| Không trùng | Set/set | Xác định “trùng” theo id hay theo object |
| Quan hệ dữ liệu bền | bảng + PK/FK/UNIQUE | Không thay DB bằng một Map toàn cục |

Không cần bắt đầu bằng thuật toán khó. Cần hiểu duyệt O(n), tìm lặp O(n²),
đổi bộ nhớ lấy thời gian và đo dữ liệu thật khi tối ưu. Với dữ liệu lớn, lọc
phân trang phía server thay vì tải hết rồi giấu bớt bằng CSS.

## 7. Tư duy lỗi: dự đoán rồi thiết kế phép thử

```javascript
function brokenCount(tasks) {
  let count = 0;
  for (const task of tasks) {
    if (task.status === 'pending') count += 1;
    return count;
  }
}
```

Trước chạy, đoán output cho rỗng, `[graded,pending]`, `[pending,pending]`.
Vết lỗi: return ở trong for kết thúc lần gọi ngay lượt đầu; rỗng không vào for
nên không return. Sửa bằng đưa return ra ngoài, rồi giữ cả ba trường hợp làm test.

## 8. Ba mức thực hành, đáp án chỉ mở sau khi thử

**Có hướng dẫn:** viết countPending bằng for và ghi bảng vết cho 4 task.

**Bớt hướng dẫn:** viết `getOverdue(tasks, now)` với dữ liệu bài học có
deadline số timestamp và status pending. Đầu ra là array mới; đúng deadline
chưa quá hạn. Tự viết điều kiện và test biên.

**Đề trắng:** thiết kế báo cáo số nhiệm vụ theo trạng thái, kể cả trạng thái
không nhận biết. Tự quyết định từ chối hay nhóm unknown, ghi hợp đồng trước.

<details><summary>Gợi ý cho getOverdue</summary>

Giữ task khi `status === 'pending' && now > deadline`. Đừng dùng `Date.now()`
ẩn trong hàm nếu muốn test thời điểm cố định. Không sort input tại chỗ.

</details>

## 9. Điều kiện sang JavaScript

Tự giải thích biến/nhánh/lặp/hàm, tự viết một hàm từ hợp đồng, dự đoán output,
phát hiện return sai vị trí và đặt test rỗng/biên. Nếu chưa làm được, sửa bài
nhỏ này trước khi thêm framework. Ghi một lỗi bạn đã tự tìm vào nhật ký.
