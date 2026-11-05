# 06 — SQL và tư duy thiết kế dữ liệu

Toàn bộ bảng dưới đây là mô hình luyện tập đề xuất, không phải migration đã áp
dụng. Thực hành trên database học riêng. Không chạy CREATE/UPDATE/DELETE vào
database đang dùng thật để thử cú pháp.

## Bài 06.1 — Biến câu chuyện thành thực thể và quan hệ

Câu chuyện: người dùng tham gia nhiều lớp; lớp có nhiều bài tập; một học sinh có
một bài nộp cuối cho một bài tập trong phiên bản bài học này; cô có thể chấm bài đó.

```mermaid
erDiagram
    USERS ||--o{ MEMBERSHIPS : joins
    CLASSES ||--o{ MEMBERSHIPS : contains
    CLASSES ||--o{ ASSIGNMENTS : owns
    ASSIGNMENTS ||--o{ SUBMISSIONS : receives
    USERS ||--o{ SUBMISSIONS : submits
    SUBMISSIONS ||--o| GRADES : receives
```

Id định danh, không dùng tên lớp hoặc họ tên làm khóa chính. Foreign key giữ
tham chiếu tồn tại; UNIQUE ngăn trùng theo một quy tắc. Những ràng buộc liên quan
vai trò/quyền và hai bảng thường vẫn cần service kiểm tra.

## Bài 06.2 — Đọc cú pháp tạo bảng

Đây là phần lõi để học, giả định bảng users/classes/assignments đã có và id kiểu
BIGINT UNSIGNED. Tạo đầy đủ các bảng theo thứ tự FK là bài thực hành.

```sql
CREATE TABLE memberships (
    class_id BIGINT UNSIGNED NOT NULL,
    user_id BIGINT UNSIGNED NOT NULL,
    member_role VARCHAR(20) NOT NULL,
    PRIMARY KEY (class_id, user_id),
    FOREIGN KEY (class_id) REFERENCES classes(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE submissions (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    assignment_id BIGINT UNSIGNED NOT NULL,
    student_id BIGINT UNSIGNED NOT NULL,
    answer LONGTEXT NOT NULL,
    submitted_at DATETIME(6) NOT NULL,
    UNIQUE KEY uq_submission_owner (assignment_id, student_id),
    FOREIGN KEY (assignment_id) REFERENCES assignments(id),
    FOREIGN KEY (student_id) REFERENCES users(id)
);
```

Đọc từng phần: tên bảng → tên trường → kiểu → NULL/default → khóa/ràng buộc.
Khóa ghép membership ngăn một người có hai bản ghi thành viên cùng lớp trong
mô hình này. Nếu cần nhiều quyền trong một lớp, phải thiết kế lại có chủ đích.
UNIQUE submission thể hiện một bản nộp cuối; muốn nhiều lượt cần mô hình attempt
và quy tắc chọn lượt, không bỏ UNIQUE một cách mù quáng.

## Bài 06.3 — CRUD và truy vấn có tham số

```sql
SELECT id, full_name FROM users WHERE id = 12;
SELECT id, title FROM assignments
WHERE class_id = 10 AND status = 'published'
ORDER BY id DESC LIMIT 20 OFFSET 0;
```

WHERE lọc hàng; ORDER BY sắp xếp; LIMIT/OFFSET giới hạn trang. Thứ tự ổn định cần
trường phân biệt khi các giá trị bằng nhau. Backend nhận page_size phải có giới
hạn; không tải toàn bộ lớp/bài nộp để frontend tự phân trang khi dữ liệu tăng.

Trong ứng dụng, truyền tham số qua thư viện/ORM. Không nối input thành SQL:
`WHERE full_name = '` + tên người dùng + `'`. Bỏ dấu nháy thủ công không phải
biện pháp thay cho parameterized query.

INSERT tạo hàng, UPDATE đổi hàng, DELETE xóa hàng. Trước khi sửa/xóa dữ liệu
bài thực hành, viết SELECT cùng điều kiện để biết phạm vi. Không nhầm UPDATE
không WHERE với sửa một bản ghi. Việc lưu trữ lịch sử có thể phù hợp hơn xóa cứng.

## Bài 06.4 — JOIN, LEFT JOIN và NULL

Giả định `memberships` dùng member_role='student', `assignments` có class_id.
Lấy các học sinh trong lớp chưa nộp một bài:

```sql
SELECT u.id, u.full_name
FROM assignments AS a
JOIN memberships AS m
  ON m.class_id = a.class_id AND m.member_role = 'student'
JOIN users AS u ON u.id = m.user_id
LEFT JOIN submissions AS s
  ON s.assignment_id = a.id AND s.student_id = u.id
WHERE a.id = 20 AND s.id IS NULL;
```

JOIN chỉ giữ hàng có đối tác phù hợp. LEFT JOIN giữ hàng bên trái và gán NULL
khi không có bài nộp. Điều kiện sai ở WHERE có thể vô tình biến ý nghĩa thành
INNER JOIN. So sánh NULL dùng IS NULL, không dùng `= NULL`.

```sql
SELECT a.id, COUNT(s.id) AS submitted_count
FROM assignments AS a
LEFT JOIN submissions AS s ON s.assignment_id = a.id
WHERE a.class_id = 10
GROUP BY a.id;
```

COUNT(s.id) bỏ NULL, cho 0 khi chưa ai nộp; COUNT(*) có thể đếm cả hàng đại diện
bên trái. Đừng JOIN thêm một bảng một-nhiều rồi đếm mà không xét nhân bản hàng.

## Bài 06.5 — Transaction và điều kiện tranh chấp

```sql
START TRANSACTION;
-- Ghi bài nộp bằng câu lệnh có tham số từ ứng dụng.
-- Ghi các thay đổi liên quan trong cùng nghiệp vụ.
COMMIT;
```

Nếu một bước lỗi thì ROLLBACK. Atomic nghĩa là cả nhóm cùng thành công hoặc
không được coi là thành công. Hai request đồng thời đều có thể thấy chưa có bài
nộp rồi cùng INSERT; kiểm tra trước ở Python không thay UNIQUE trong database.

Khi gặp xung đột unique, rollback Session trước khi tiếp tục dùng. Chỉ chuyển
thành phản hồi xung đột khi biết lỗi đúng ràng buộc mong đợi; không gọi mọi lỗi
IntegrityError là trùng bài. Chính sách gửi lại cùng nội dung ở chương 10 cần
được hoàn thiện cả ở DB, không chỉ trong repository giả.

Đừng giữ transaction mở trong lúc chờ gửi email hoặc upload mạng lâu.
Transaction DB không rollback được một email đã gửi hay file đã upload.

## Bài 06.6 — Thời gian, điểm và index

- Thống nhất lưu thời điểm UTC. DATETIME tự nó không mang timezone; service
  chuyển đổi theo quy ước, không trộn giờ máy và giờ học sinh.
- Điểm có quy tắc thập phân rõ nên cân nhắc DECIMAL và Decimal; tiền học phí
  nếu thêm sau không nên tính bằng float thiếu kiểm soát.
- Index hỗ trợ kiểu truy vấn cụ thể; có chi phí ghi và lưu trữ. UNIQUE đã tạo index.
- Với truy vấn `WHERE class_id ... ORDER BY due_at, id`, đánh giá composite index
  phù hợp bằng EXPLAIN và dữ liệu thực tế, không index mọi cột.
- Foreign key không chứng minh người nộp thuộc lớp của bài; service/quyền phải kiểm tra.

## Bài tự viết

- **SQL1:** tạo đủ bảng users, classes, memberships, assignments, submissions, grades
  trên database học, chỉ ra PK/FK/UNIQUE và thứ tự tạo.
- **SQL2:** lấy lớp của một học sinh; học sinh của một lớp; bài đã công bố của lớp.
- **SQL3:** tìm ai chưa nộp và đếm đúng khi lớp/bài không có dữ liệu.
- **SQL4:** thử thêm trùng membership; ghi lỗi và giải thích ràng buộc nào bảo vệ.
- **SQL5:** cố tình làm bước thứ hai lỗi trong transaction và xác nhận bước đầu không lưu.
- **SQL6:** giải thích không dùng dữ liệu thật để thử xóa; đề xuất giữ lịch sử điểm.

Qua chương khi tự viết JOIN không nhìn ORM và giải thích được transaction cùng
hai request đồng thời. Các query trong tài liệu chưa được chạy trên MySQL trong
lần soạn giáo án; bạn cần kiểm tra bằng fixture của database học.

Tham khảo: [MySQL Tutorial](https://dev.mysql.com/doc/refman/8.0/en/tutorial.html).

## Xưởng — Từ câu chuyện đến bảng, từng bước

Một cô quản lý nhiều lớp; một học sinh học nhiều lớp. Bảng classes giữ một
teacher_id cho bản đầu; memberships biểu diễn nhiều-nhiều student–class.
Nếu sau này một lớp nhiều cô, đó là thay đổi quan hệ cần migration và policy,
không nhét danh sách id thành chuỗi phân tách dấu phẩy trong một cột.

```sql
CREATE TABLE learning_classes (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  title VARCHAR(200) NOT NULL,
  teacher_id BIGINT NOT NULL,
  INDEX ix_learning_classes_teacher (teacher_id)
);
```

Chỉ chạy trong DB học mới sau khi đọc lệnh. Ví dụ bảng độc lập này chưa có FK
vì chưa tạo users tương ứng; schema đầy đủ phải thêm FK đúng kiểu/engine và
quy tắc xóa. PK định danh row; index không tự cấp quyền; NOT NULL không ngăn
chuỗi rỗng; UNIQUE title chỉ thêm nếu nghiệp vụ thật cấm trùng trong phạm vi đó.

Học kiểu: integer cho id/count theo miền, VARCHAR cho chuỗi giới hạn, TEXT cho
nội dung theo nhu cầu, DECIMAL cho số chính xác có precision/scale đã chọn,
thời gian với policy timezone rõ. Đừng mặc định float cho mọi điểm hoặc TEXT
cho mọi thứ. Xem utf8mb4/collation và kiểm cách so tên có dấu/hoa thường trên DB thật.

## Xưởng — Viết SELECT trước ORM

```sql
SELECT id, title, teacher_id
FROM learning_classes
WHERE teacher_id = 1
ORDER BY id
LIMIT 20 OFFSET 0;
```

SELECT chọn cột; FROM chọn nguồn; WHERE lọc hàng; ORDER BY đặt thứ tự; LIMIT
giới hạn. Không có ORDER BY thì không hứa thứ tự ổn định. Parameter user đưa
vào phải bind, không nối chuỗi. Identifier sort không bind như giá trị: dùng
allowlist field và hướng sort hợp lệ, không chèn raw input.

Aggregation: WHERE lọc trước nhóm; GROUP BY tạo nhóm; HAVING lọc kết quả nhóm.
COUNT(*) đếm hàng,COUNT(column) bỏ NULL; AVG bỏ NULL nên phải định nghĩa rõ
chưa làm bài có được tính điểm 0 hay không. Đừng dùng AVG để tự quyết định
chính sách báo cáo chưa chốt.

## Xưởng — JOIN và nhân hàng

Một lớp có10 thành viên và4 bài tập; JOIN cả hai bảng con độc lập có thể tạo40 hàng,
làm COUNT sai. Tính tay fixture 2 thành viên×3 bài=6 trước khi viết query. Có thể
tổng hợp từng tập trước rồi JOIN, hoặc truy vấn riêng theo mục tiêu; DISTINCT
không phải thuốc chữa mọi loại nhân hàng và có thể che sai mô hình.

Với LEFT JOIN, chuyển điều kiện bảng phải từ ON sang WHERE có thể loại hàng
NULL và làm mất người chưa nộp. Bài: lấy đủ thành viên của một lớp, chỉ khớp
submission của assignment được chọn, rồi WHERE submission.id IS NULL.

## Xưởng — Transaction và cạnh tranh

```text
T1 kiểm chưa có bài       T2 kiểm chưa có bài
T1 INSERT                T2 INSERT
         UNIQUE(assignment_id,student_id) quyết định bản trùng
```

Hai lần SELECT trước INSERT không ngăn race. Cần constraint và hợp đồng xử lý
IntegrityError/retry, kiểm lại sau rollback bằng transaction phù hợp. Isolation
và khóa ảnh hưởng điều nhìn thấy; phải thử MySQL và driver thật. Với bản cuối
của thư viện hoặc giới hạn số học sinh, cần xét atomic update/lock phù hợp,
không chỉ đếm rồi insert ở hai transaction riêng.

Một transaction nhóm thay đổi DB, không rollback email/file đã gửi ra ngoài.
Outbox/cleanup cần thiết khi phối hợp tài nguyên khác. Commit xác nhận nhưng
client mất response vẫn có thể không biết tác dụng đã xảy ra.

## Xưởng — Index, EXPLAIN và migration

Đọc query hay dùng trước khi thêm index. Compound index có thứ tự cột và tradeoff
ghi/storage. EXPLAIN giúp xem plan; đo với dữ liệu đại diện. OFFSET rất lớn có
thể cần cursor pagination, nhưng phải thiết kế ordering ổn định và tie-breaker.

Chuẩn hóa tránh lặp thông tin gây update lệch; snapshot có chủ ý như title câu
hỏi lúc thi là bài toán khác. Soft delete cần chính sách scope/unique/lịch sử;
không cứ thêm deleted_at là mọi query tự đúng.

**Điền:** tạo fixture 3 lớp,2 cô,4 học sinh; viết SELECT đúng phạm vi.

**Trắng:** ERD bài tập/bài nộp/điểm và báo cáo người chưa nộp; tính tay trước query.

**Sửa lỗi:** báo cáo đếm trùng sau JOIN; chứng minh bằng fixture tối thiểu, sửa
và thêm test0hàng,NULL,trùng tên,điểm 0 và nhiều bản ghi con.
