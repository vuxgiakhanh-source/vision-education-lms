# Điểm dừng và nhật ký học/code

## Mức hiện tại đã xác nhận — cập nhật 17/10/2026

Người học biết cú pháp Python và biến/if/for/hàm, chưa tự viết JavaScript,
chưa biết TypeScript/CSS; cần cách đọc và dùng API/tool lạ. **Điểm bắt đầu mới
là [G0](course/G0-cach-hoc-de-tu-xay.md)**, rồi F0 phần JS, F2, F1, G1–G6.
Sách có 14 bài chính và thư viện chuyên đề thu gọn. G1/G2 tự tạo web từng file;
G3 tách Python trước/sau; G4 giải tính năng xuyên hệ thống và đáp án tách
feature; G5 mở rộng module; G6 nộp/review/sửa và bài mới. P2–P5 đến sau.

Việc tiếp theo của người học: chốt bảng ví dụ Sổ lớp ở G0, tự chuyển bài lọc
điểm Python sang JS rồi dựng card/web G1. Chưa đánh dấu đã đạt bất kỳ mốc nào.
Code studio/workshop tách khỏi sản phẩm. Phép kiểm và giới hạn hiện tại ở
[VALIDATION](course/VALIDATION.md). Các mục bên dưới là lịch sử các lần soạn.

## Sửa điểm bắt đầu theo năng lực hiện tại — 17/10/2026

Người học nói chưa biết cú pháp. Việc tiếp theo là S0, mục2–7: hiển thị một số,
phân biệt chữ/số, tạo let và đổi giá trị qua từng dòng. Chưa học P0 hay triển
khai lúc này. Đầu ra buổi đầu: tự gõ3 dòng với soBai, tăng1 và giải thích từng
ký hiệu; chưa tự đánh dấu đã đạt. Home sách và ô luyện đã chuyển về hướng này.

## Bổ sung giáo án P0–P5 — 17/10/2026

- Sách hiện có30 bài,128 câu hỏi,90 thẻ và18 mốc/54 tiêu chí. Thêm sản phẩm xuyên
  suốt, refactor có tests, đo tải, triển khai/CI, bảo mật/vận hành và nghiệm thu.
- Xưởng riêng có core loop API/React/DB giao/nộp/chấm/công bố, Transaction adapter,
  MySQL/Alembic/Compose/Nginx template và script k6. Sản phẩm chính chưa nhận các
  module lab này. Bằng chứng và giới hạn ở `course/VALIDATION.md`.
- Browser đã thử core loop bằng tài khoản giả và SQLite file. Bộ xưởng26 test
  qua,2 test MySQL skip; chưa đo tải/MySQL/restore vì Docker Engine chưa chạy.
- Việc học đề xuất sau nền và chương10: P0 core loop rồi P1 refactor; không
  tự đánh dấu người học đã đạt bất kỳ mốc mới nào.

## Đọc đầu tiên khi mở dự án

Đã có [giáo án chi tiết 15 chương](course/README.md), kèm ví dụ tham chiếu và bộ
kiểm tra riêng cho việc học. Điểm dừng dưới đây tiếp tục dùng được; có thể bắt
đầu bằng khảo sát chương 00 nếu muốn xác định phần nền tảng cần ôn.

Bản dễ học bằng hình và thao tác: [sách HTML Hiểu tận gốc](course/GIAO-AN-LMS.html).
Mở bằng Chrome/Edge để dùng mô phỏng, giải thích từng dòng, câu hỏi và thẻ ôn.
Sách chạy offline; ghi chú cần xuất bản sao nếu chuyển trình duyệt/máy.

Sách đã mở rộng 24 bài, lộ trình 12 mốc/36 tiêu chí. Học bộ công cụ và nền tảng
trước; xưởng lớp học là code tham chiếu độc lập, không phải thay đổi sản phẩm.
Đọc [phạm vi kiểm tra](course/VALIDATION.md) trước khi suy từ test sang năng lực.

- **Hiện tại:** đã có khung auth và dashboard responsive; dashboard vẫn dùng mock.
- **Việc đang chọn:** L00.2 — kể lại luồng đăng nhập từ frontend đến database và quay về.
- **Mở ở đâu:** [CODE_GUIDE mục luồng đăng nhập](CODE_GUIDE.md#5-đọc-một-luồng-hoàn-chỉnh-đăng-nhập).
- **Khi nào xong:** tự vẽ và giải thích được luồng mà không nhìn tài liệu;
  chạy thử nếu môi trường backend sẵn sàng và ghi kết quả thật.
- **Sau đó:** L00.3 — đọc lại đổi mật khẩu.
- **Chưa rõ:** thời gian học mỗi ngày và mức tự làm của từng mảng; chưa đặt lịch tuần.

Đây là điểm bắt đầu đề xuất. Khi chọn việc khác, thay nội dung khối này để nó
luôn chỉ đúng một việc tiếp theo.

## Quy trình mỗi buổi

**Mở buổi:** đọc điểm dừng → xem `git status --short` → chọn một mã việc →
nói rõ đầu vào, đầu ra và cách kiểm tra trước khi sửa.

**Trong buổi:** học phần nhỏ cần dùng → thực hành → giải thích lại → kiểm tra.
Nếu nhờ AI, yêu cầu chỉ ra luồng và lý do thay đổi; tự xem diff trước khi nhận là đã hiểu.

**Cuối buổi:** ghi kết quả theo mẫu → cập nhật điểm dừng → đánh dấu checklist
khi có bằng chứng → tạo commit mô tả đúng phần đã làm nếu muốn lưu mốc.
Không đưa cả thay đổi không liên quan vào cùng một commit.

## Mẫu ghi nhanh — sao chép cho mỗi buổi

```text
Ngày:
Mã việc:
Mục tiêu của buổi:

Mình đã đọc/sửa file nào? Vì sao?
-

Luồng xử lý mình hiểu được (viết bằng lời của mình):
-

Đã kiểm tra gì? Kết quả thật?
- Lệnh/tình huống:
- Kết quả:
- Chưa kiểm tra:

Quyết định nghiệp vụ (nếu có): ai chốt, nội dung, còn đề xuất hay đã duyệt?
-

Điều còn chưa hiểu/lỗi có thể tái hiện:
-

Việc đầu tiên lần sau (ghi cụ thể file và thao tác):
-

Commit nếu có:
```

## Nhật ký 17/10/2026 — lập lại bản đồ dự án

- Đã đọc cấu trúc source, luồng login/change-password/me, model users và nơi lấy dữ liệu dashboard.
- Đã viết README, CODE_GUIDE, LEARNING_ROADMAP và nhật ký này để có điểm quay lại.
- Dashboard responsive đã được áp dụng ở các buổi trước; phần nghiệp vụ vẫn dùng mock.
- Ở các buổi trước, frontend build/lint đã qua và đã đo 20 mốc chiều rộng dashboard.
- Trong lần lập tài liệu này chưa chạy lại đăng nhập/database, chưa chạy migration,
  seed hoặc thay đổi hành vi ứng dụng.
- Chưa đánh dấu bài học nào là người dùng đã hiểu; các checklist vẫn để mở.
- Việc tiếp theo đề xuất: L00.2 trong LEARNING_ROADMAP.

## Nhật ký 17/10/2026 — bổ sung giáo án viết code bằng tay

- Thêm giáo án theo stack thật: nền tảng, React, Python/OOP, SQL, API, ORM,
  quyền, giao/nộp/chấm, luyện thi, kiểm thử/vận hành và các module mở rộng.
- Thêm bài tự viết, gợi ý/đáp án và câu hỏi bảo vệ; chưa đánh dấu người dùng đã đạt bài nào.
- Ví dụ học tập tách khỏi ứng dụng, không kết nối dữ liệu lớp thật.
- Báo cáo kiểm tra giáo án và ví dụ nằm tại `docs/course/VALIDATION.md`.
- Chưa triển khai các module nghiệp vụ tương lai vào sản phẩm.


## 22/10/2026 — Giáo án: ưu tiên kiến thức dự án, cú pháp và tự thiết kế

Theo phản hồi người học biết Python nhưng chưa biết JS/TS/CSS: thêm ba ưu
 tiên mỗi bài, mổ xẻ cú pháp/trách nhiệm cho 41 bài và bản đồ 29 nhóm kiến
thức dùng trong Vision LMS. Nhãn mức cần học và ứng dụng đặt ngay cạnh mục;
link atlas đến đúng step. Bổ sung F0/02/04 và G4.10 theo source auth thật,
phân biệt trạng thái repo với module sẽ xây. Mã dài thu gọn để đối chiếu,
ô tự viết trống lưu cùng ghi chú; S0 thêm 11 drill có kiểm output/biến/trace.
UI giữ trắng/xám + xanh dương, callout phân cấp, đọc một cột và responsive.
Build/verifier, snippet/type checks, DOM double và drill tests qua; CSS parse
0 warning. Chưa kiểm trực quan bản mới trong browser, chưa đo tải/MySQL hay
restore. Không thay code sản phẩm hoặc file requirements của người dùng.
