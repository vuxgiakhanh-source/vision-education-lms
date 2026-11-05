# Hệ thống này cần những gì, và học đến đâu là tự làm được?

Đích của khóa học: tự xây một LMS có tài khoản, lớp, bài tập, nộp/chấm bài,
luyện tập, lịch, tài liệu và quản trị; tự kiểm tra và đưa một bản dùng thử lên
môi trường phù hợp. Không có tài liệu hữu hạn bao phủ mọi tình huống phần mềm.
Phạm vi ở đây được ghi thành những năng lực và bằng chứng cụ thể để bạn biết
phần nào đã học, phần nào còn phải thực hành. Không suy ra thành thạo từ việc đọc hết.

Sau các mốc nền, học P0–P5: [core loop](23-san-pham-hoan-chinh.md),
[clean code](24-clean-code-refactor.md), [đo tải](25-hieu-nang-chiu-tai.md),
[phát hành](26-trien-khai-ci-cd.md), [bảo mật/vận hành](27-bao-mat-va-van-hanh.md)
và [nghiệm thu đồ án](28-do-an-va-nghiem-thu.md). Các mốc này cần bằng chứng
chạy riêng; không suy ra từ việc đã đọc nền hoặc mở được lab.

## 1. Nhìn một lần nộp bài qua cả hệ thống

```text
Người học nhập bài
  → event của form
  → validation và trạng thái đang gửi
  → Axios tạo HTTP request
  → FastAPI đọc token và JSON
  → service kiểm người/lớp/trạng thái/hạn nộp
  → repository truy vấn bằng SQLAlchemy
  → MySQL giữ dữ liệu và ràng buộc
  → commit thành công
  → JSON response
  → client xác minh/đọc kết quả
  → UI hiển thị trạng thái thật
```

Trên giấy, đặt một dấu chấm tại từng mũi tên và hỏi: dữ liệu có hình gì, ai
chịu trách nhiệm, có thể lỗi thế nào, quan sát ở đâu? Nếu chưa trả lời được,
bạn đã tìm thấy một bài cần học. Đừng sửa CSS khi API chưa trả dữ liệu; đừng
sửa SQL khi form chưa gửi request.

## 2. Chín lớp kiến thức phải nối lại được

| Lớp | Bạn phải tự làm | Bằng chứng |
|---|---|---|
| Môi trường | Chạy đúng process, thư mục, interpreter và cổng | Giải thích ba terminal/frontend/backend/DB |
| Ngôn ngữ | Biến, nhánh, lặp, hàm, cấu trúc dữ liệu, exception, async | Viết hàm từ đề và test biên |
| Web | DOM, event, CSS, HTTP, origin, JSON, storage | Tự đọc một request trong Network |
| Frontend | Component, props/state, form, router, API, responsive | Reload/đổi tài khoản vẫn đúng dữ liệu |
| Backend | Schema, dependency, service, repository, response | Endpoint đúng cả quyền và lỗi |
| Dữ liệu | Quan hệ, khóa, JOIN, transaction, migration, index | Giữ được ràng buộc khi có lỗi |
| Nghiệp vụ | Quyền theo lớp, trạng thái, thời gian, điểm | Giải thích quyết định bằng bảng quy tắc |
| Chất lượng | Unit/integration/luồng người dùng, debug, Git | Tái hiện lỗi, có test và diff sửa |
| Vận hành | Cấu hình, phát hành, log, backup, phục hồi | Máy khác chạy được; phục hồi thử thành công |

Mỗi lớp có cả phần bắt buộc cho bản đầu và phần mở rộng. Không cần Kafka,
Kubernetes hoặc microservices để chứng minh một lớp học được giao bài đúng.
Khi nhu cầu mới xuất hiện, bạn phải biết đánh giá và học công cụ tương ứng.

## 3. Bản đồ module sản phẩm

| Module | Dữ liệu cốt lõi | Quy tắc phải hỏi trước khi code |
|---|---|---|
| Tài khoản | user, role, active, password hash | Ai tạo/reset/khóa, phiên cũ ra sao? |
| Lớp | class, membership, phân công | Một người nhiều lớp? Rời lớp giữ lịch sử thế nào? |
| Bài tập | assignment, deadline, status | Nháp/công bố/đóng khác nhau gì? |
| Bài nộp | submission, nội dung, thời điểm | Có sửa/nộp lại không? Gửi lặp xử lý sao? |
| Chấm | grade, feedback, published_at | Ai chấm, thang điểm, chấm lại, khi nào học sinh thấy? |
| Luyện tập | question, option, attempt, answer | Lượt nào được tính, phiên bản câu hỏi, đáp án bị lộ không? |
| Lịch | session, thời gian, hủy/dời | Múi giờ, trùng lịch, lịch lặp và ngoại lệ? |
| Điểm danh | session/student/status | Ai ghi/sửa; lưu lịch sử; học sinh rời lớp? |
| Tài liệu | metadata, storage_key, quyền tải | File nháp, mất file, upload lỗi, dung lượng? |
| Thông báo | recipient, event, read_at | Đúng người, gửi lặp, gửi thất bại? |
| Hỏi đáp/chat | thread, message, thành viên | Ai đọc/ẩn; phân trang; mất kết nối? |
| Dashboard | các truy vấn tổng hợp | Định nghĩa chỉ số, phạm vi lớp/thời gian và mẫu số? |
| Quản trị | thao tác và audit | Ai được đổi vai trò; có phục hồi; xuất dữ liệu gì? |

Đây là câu hỏi thiết kế để chốt với người dùng. Giáo án không tự thay mong muốn
kinh doanh thành quyết định đã duyệt. Viết bản đầu nhỏ, có đường nâng cấp rõ.

## 4. Học qua sáu mức, không chỉ đọc

1. **Nhận diện:** nói được một ký hiệu/hàm dùng để làm gì.
2. **Theo dấu:** dự đoán giá trị và nhánh trước khi chạy.
3. **Hoàn thiện:** điền phần thiếu trong một khung đã có.
4. **Tự viết:** từ yêu cầu trắng, chọn dữ liệu và viết implementation.
5. **Sửa sai:** tái hiện và sửa một lỗi mà không có lời giải sẵn.
6. **Chuyển giao:** làm yêu cầu mới hoặc miền mới bằng cách tự phân tích.

Nếu mới làm được mức 1–2, giữ bài đó ở trạng thái đang học. Việc tự đánh dấu
hoàn thành trong sách không phải hệ thống đã chấm code hoặc chứng nhận bạn.

## 5. Bài khảo sát để chọn đúng điểm bắt đầu

Viết tay trên giấy hoặc file riêng, chưa mở lời giải:

- Với `[0, null, 10]`, viết hàm trung bình hợp lệ và giải thích mẫu số.
- Với danh sách task, tìm theo tên và giữ nguyên dữ liệu gốc.
- Vẽ nơi chạy của JSX, Python và SQL; chỉ ra nơi HTTP nối chúng.
- Với “cô chỉ xem bài lớp mình”, viết điều kiện quyền bằng lời.
- Một request tạo lớp timeout: giải thích vì sao chưa thể biết DB đã lưu chưa.
- Từ thư mục mới, giải thích phải tạo/chạy những gì trước trang React đầu tiên.

Không làm được câu nào thì dùng câu đó làm bài đầu. Không cố đọc theo tốc độ
của người đã biết một phần. Cuốn sách không đặt thời hạn đồng loạt cho mọi người.

## 6. Dự án xuyên suốt và dự án chuyển giao

Dự án xuyên suốt là LMS nhỏ. Bắt đầu từ bài tập dữ liệu, sang UI local, API
preview, SQL, lớp có quyền, rồi giao/nộp/chấm. Chương **Xưởng từ số 0** có một
lát cắt lớp học chạy được để đối chiếu. Tự viết trước khi xem source.

Sau đó làm **quản lý mượn sách** từ yêu cầu mới: độc giả, sách, bản sao, phiếu
mượn, hạn trả và quyền thủ thư. Nếu chỉ đổi tên Class thành Book mà không xét
bản sao/hết sách/trả lại, bạn chưa chuyển được tư duy nghiệp vụ.

Được tra tài liệu, xem lỗi compiler, dùng debugger. Ghi nguồn đã tra và giải
thích cách áp dụng. Trong bài đánh giá độc lập, không nhận nguyên chức năng do
AI sinh rồi coi đó là sản phẩm tự viết. AI có thể đóng vai người hỏi/gợi ý/review.

## 7. Cách ghi bằng chứng cho mỗi mốc

```text
Yêu cầu tôi nhận:
Đầu vào / đầu ra / quy tắc:
Sơ đồ dữ liệu và đường chạy:
File tôi tự viết và lý do tách:
Lệnh chạy + kết quả thật:
Trường hợp sai đã thử:
Lỗi tôi gặp → giả thuyết → phép thử → cách sửa:
Thay đổi yêu cầu tôi đã tự xử lý:
Phần chưa làm được:
```

Giữ bằng chứng trong repo thực hành của bạn. Người khác phải đọc README để chạy
được, không cần bạn đứng cạnh bấm từng bước hoặc đưa secret trong tin nhắn.
