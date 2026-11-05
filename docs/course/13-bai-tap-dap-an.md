# 13 — Bài tập tổng hợp, gợi ý và đáp án để tự kiểm tra

Đọc yêu cầu, tự viết và thử trước khi mở gợi ý. Sau khi xem đáp án, đóng lại rồi
làm một biến thể: đổi dữ liệu, thêm một tình huống lỗi hoặc một quy tắc mới.

## Bộ A — Ngôn ngữ và tư duy

### A1: Đếm và lọc nhiệm vụ

Đầu vào có pending/submitted/graded, mảng rỗng, tên có hoa/thường. Viết countPending,
searchTasks và markSubmitted không sửa dữ liệu gốc. Không đổi bài graded về submitted.

<details><summary>Gợi ý</summary>

Count dùng vòng lặp hoặc filter; search trim/lowercase cả query và title;
update dùng map và spread đúng object. So sánh cả nội dung gốc và tham chiếu.
Lời giải chạy được: [tasks.ts](examples/tasks.ts), [test](examples/tasks.test.ts).

</details>

### A2: Trung bình và dữ liệu rỗng

Với [0, null, 10], kết quả là 5. Với [null], kết quả là null. Hãy giải thích vì
sao filter(Boolean) sai cho bài này và vì sao chia cho 0 phải được xử lý.

<details><summary>Đáp án tham khảo</summary>

```javascript
function averageGraded(scores) {
  const graded = scores.filter(score => score !== null);
  if (graded.length === 0) return null;
  return graded.reduce((total, score) => total + score, 0) / graded.length;
}
```

Giả định đầu vào chỉ number hợp lệ/null. 0 là falsy nên filter(Boolean) sẽ loại
điểm 0. Response mạng cần validation riêng, không áp dụng giả định này tùy tiện.

</details>

### A3: Dự đoán và sửa

```javascript
const source = [{ id: 1, status: 'pending' }];
const copy = [...source];
copy[0].status = 'submitted';
console.log(source[0].status);
```

<details><summary>Đáp án</summary>

In submitted vì object đầu tiên vẫn chung. Để đổi mà giữ source, tạo object mới
ở phần tử thay đổi: `source.map(item => item.id === 1 ? {...item, status:'submitted'} : item)`.

</details>

## Bộ B — React và API

### B1: Trang nhiệm vụ

Tự viết component có input tìm kiếm, callback mở bài, số kết quả, loading/error/empty.
Chuyển classId nhanh không nhận kết quả cũ. Sản phẩm nộp: component, type/schema,
lớp gọi API và bản ghi Network cho ba tình huống. Không chép token vào báo cáo.

<details><summary>Hướng đối chiếu</summary>

Query là state; filtered list tính từ dữ liệu/query. Effect phụ thuộc classId,
cleanup/cancel phù hợp. Key dùng id. Server vẫn quyết định dữ liệu lớp được xem.
Lỗi HTTP và lỗi mạng không bị báo chung là phiên hết hạn. Xem mẫu chương 04.

</details>

### B2: Đọc lại đăng nhập hiện có

Tự vẽ sơ đồ, giải thích 10 từ/cú pháp: async, await, try/catch, register,
handleSubmit, Promise, Depends, self, Session, commit. Tìm một điểm chưa hoàn
chỉnh trong luồng hiện tại và đề xuất test trước khi sửa.

<details><summary>Điểm cần phân biệt</summary>

Form kiểm tra dữ liệu trước gửi, backend vẫn xác thực. Axios chuyển phoneNumber
thành phone_number. Router gọi service, repository tìm User, service kiểm mật
khẩu/trạng thái và tạo response, frontend lưu token/navigate. AuthGuard hiện chỉ
kiểm tra token tồn tại; dashboard còn ngoài guard. Không nói toàn hệ thống đã có RBAC.

</details>

## Bộ C — Nghiệp vụ và dữ liệu

### C1: Viết SubmitService theo hợp đồng chương 10

Viết tay trước, dùng repository bộ nhớ do chính bạn tạo. Tối thiểu kiểm tra:
học sinh hợp lệ, đúng lớp, bài published, deadline, answer, retry và bản gốc
không bị thay đổi khi xung đột.

<details><summary>Đáp án và điều chưa được chứng minh</summary>

[domain.py](examples/domain.py) là lời giải tham chiếu; [test_domain.py](examples/test_domain.py)
kiểm tra các quy tắc thuần. Protocol giúp thay repository; fake không mô phỏng
transaction/concurrency MySQL. Muốn chứng minh phần đó phải làm integration test.

</details>

### C2: Ai chưa nộp?

Tự viết SQL tìm học sinh trong lớp của bài, không có submission cho bài đó.
Thử lớp rỗng, 0 người nộp, một người nộp và người nộp ở lớp khác.

<details><summary>Đối chiếu</summary>

JOIN assignments→memberships→users rồi LEFT JOIN submissions theo cả assignment
và student, lọc s.id IS NULL. Bắt đầu từ submissions sẽ mất những người chưa có
hàng. Mẫu đầy đủ nằm chương 06; dữ liệu quyền phải được xử lý ở API/service.

</details>

### C3: Hai request cùng nộp

Cả hai đều đọc chưa có submission. Làm sao tránh hai bản ghi? Nếu cùng nội dung
thì response gì? Khác nội dung thì bản nào được giữ? Kiểm tra bằng MySQL test.

<details><summary>Hướng giải</summary>

UNIQUE đảm bảo ràng buộc DB. Một transaction thắng; transaction gặp đúng conflict
phải rollback, đọc lại theo policy và đối chiếu nội dung, không che lỗi FK/DB khác.
Test tuần tự chưa chứng minh cạnh tranh. Chốt isolation/locking khi có thay đổi
quyền hoặc trạng thái đồng thời; ghi giới hạn nếu chưa giải quyết.

</details>

## Bộ D — Đồ án tự làm

### D1: Lát cắt lớp học

Đặc tả quyền → thiết kế bảng/migration → API → UI → test. Cô xem lớp được phân
công, học sinh xem lớp mình, tài khoản khác bị chặn. Có phân trang và trạng thái UI.

### D2: Lát cắt giao/nộp/chấm

Thực hiện từng lát cắt chương 10. Nộp bằng hai tài khoản, có refresh và lỗi mạng.
Đính kèm ma trận quyền, hợp đồng API, sơ đồ dữ liệu và kết quả test thực tế.

### D3: Luyện thi một dạng câu

Ngân hàng câu → phát hành đề → attempt → lưu tiến độ → nộp → chấm → xem kết quả.
Giữ mapping khi đảo đáp án, kiểm deadline server và quyền xem đáp án. Thay quy tắc
chấm rồi giải thích cách giữ kết quả cũ có thể tái lập.

### D4: Thay đổi yêu cầu để kiểm tra hiểu thật

Chọn một yêu cầu: nộp muộn có phép; trợ giảng chỉ chấm một nhóm; công bố điểm
theo đợt; hoặc thêm lượt làm lại. Trước khi sửa, liệt kê tác động đến dữ liệu,
API, quyền, trạng thái UI, transaction, migration và test. Thực hiện một lát cắt
nhỏ rồi demo. Không bỏ ràng buộc DB chỉ để request chạy qua.

## 20 câu bảo vệ dự án

1. Một request login đi qua file nào, dữ liệu đổi hình dạng ở đâu?
2. TypeScript khác validation runtime thế nào?
3. Props/state khác nhau ra sao, dữ liệu nào không cần state?
4. Vì sao effect cleanup quan trọng khi đổi lớp?
5. Sau timeout, bạn có biết chắc bài chưa lưu không?
6. Object service giữ dependency gì, ai tạo nó?
7. Kế thừa khác composition thế nào trong code của bạn?
8. Token hợp lệ có đủ quyền xem mọi bài không?
9. Một người thuộc nhiều lớp được mô hình hóa thế nào?
10. Foreign key và UNIQUE bảo vệ điều gì khác nhau?
11. Flush khác commit ở đâu?
12. Hai request cùng thấy chưa có dữ liệu được xử lý ra sao?
13. Bài đã phát hành sửa nội dung có ảnh hưởng lượt cũ không?
14. Vì sao không gửi đáp án về client rồi ẩn bằng CSS?
15. Điểm 0 khác chưa chấm thế nào?
16. Tỉ lệ đúng lấy mẫu số nào và lấy lượt làm nào?
17. Test fake khác test MySQL thật ở đâu?
18. Cách dựng lại môi trường không lộ secret là gì?
19. Làm sao biết backup phục hồi được?
20. Nếu tự viết lại một module, bạn bắt đầu từ quy tắc hay tên class? Vì sao?

Tự trả lời và mở code chứng minh. Mục tiêu là tự sửa khi yêu cầu đổi, không phải
thuộc câu trả lời mẫu. Dùng thang điểm trong README giáo án và ghi điểm yếu vào WORKLOG.
