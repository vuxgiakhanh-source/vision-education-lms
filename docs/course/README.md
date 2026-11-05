# Giáo án tự xây LMS — từ nền Python đến dự án độc lập

Nếu đang đọc bản ZIP: có thể mở [G0 Markdown](G0-cach-hoc-de-tu-xay.md) ngay;
để học tương tác, giữ file HTML đã tải và đặt cạnh README này nếu cần dùng
liên kết bên dưới. ZIP chứa source/tài liệu, không lồng lại sách HTML.

**Mở [GIAO-AN-LMS.html](GIAO-AN-LMS.html) và bắt đầu G0.** Bản xây lại
22/10/2026 dành cho người biết biến/if/for/hàm Python, chưa tự viết JavaScript,
TypeScript hoặc CSS và còn vướng cách dùng thư viện.

Khóa học đi qua một Sổ lớp nhỏ trước, rồi tổ chức Python, nối UI/API/DB và
mở rộng LMS. Mỗi chặng có bài làm cùng, bài giảm gợi ý, bài tự làm, kết quả
mong đợi, cách tìm lỗi và yêu cầu thay đổi. Chọn cấu trúc từ trách nhiệm và
những thay đổi cụ thể; mỗi quyết định đều cần giải thích bằng ví dụ.

## Đường học chính

| Chặng | Bài | Sản phẩm để kiểm |
|---|---|---|
| 0 | [G0 — Cách học](G0-cach-hoc-de-tu-xay.md) | Hợp đồng Sổ lớp, thư mục học, cách tự kiểm |
| 1 | [F0 — Python sang JS](F0-python-sang-js-ts.md), [F2 — Tra API](F2-doc-ham-va-tool.md), [F1 — HTML/CSS](F1-html-css-tu-dau.md) | JS if/for/hàm, phiếu API, card HTML/CSS |
| 2 | [G1 — Web từ thư mục trống](G1-trang-web-tu-thu-muc-trong.md) | Tự tạo HTML/CSS/JS, sự kiện → dữ liệu → render |
| 3 | [G2 — TS/React](G2-tu-js-sang-react.md) | Tạo manifest/config/entry, chia component và state |
| 4 | [G3 — Tổ chức Python](G3-python-tu-mot-file-den-module.md) | Một file → tách module, cây trước/sau, import và test |
| 5 | [G4 — Xuyên hệ thống](G4-thiet-ke-tinh-nang-xuyen-he-thong.md) | Yêu cầu → quyền/dữ liệu/API/UI, bài thay đổi lưu trữ lớp |
| 6 | [G5 — Mở rộng LMS](G5-tu-lat-cat-den-toan-bo-lms.md) | Điểm danh có hướng dẫn → tài liệu bớt gợi ý → thông báo tự làm |
| 7 | [G6 — Tự làm/review](G6-tu-lam-va-duoc-phan-hoi.md) | Code riêng, phản hồi có ca lỗi, sửa và làm biến thể |
| 8 | [P2](25-hieu-nang-chiu-tai.md) → [P3](26-trien-khai-ci-cd.md) → [P4](27-bao-mat-va-van-hanh.md) → [P5](28-do-an-va-nghiem-thu.md) | Đo tải, triển khai, phục hồi và nghiệm thu |

F0 học phần JS trước; phần thêm kiểu quay lại ở G2. Mỗi H2 là một buổi nhỏ,
có thể cần nhiều lần thực hành. Bài đang học có liên kết chuyên đề để tra đúng
lúc. Các chương 00–28 còn lại, S0 ôn từng dấu và ví dụ đăng nhập nằm trong thư
viện tham khảo thu gọn; bài xưởng tổng hợp 21 làm sau G4.

Sách gồm 14 bài trên đường chính và 27 bài chuyên đề. Số bài, câu hỏi và tiến
độ hỗ trợ tìm đường; code tự viết và xử lý biến thể mới cho biết năng lực.
G6 hướng dẫn nộp code và nhận review cụ thể. Sách chưa tự chấm dự án riêng.

## Đọc và dùng giao diện

Giao diện dùng nền trắng/xám, điểm nhấn xanh dương; chế độ tối dùng slate/navy.

File HTML tự chứa bài giảng, code tham chiếu, CSS/JS, tìm kiếm và mô phỏng.
Mở bằng trình duyệt để đọc offline; liên kết tài liệu chính thức cần mạng khi
chủ động mở. Không cần khởi động ứng dụng LMS để đọc sách.

- Trang chủ: đường học theo chặng, bài đang tiếp tục và bộ mã tải về.
- Trong bài: Cần nhớ / Phải tự làm / Cách kiểm; Học từng bước, Cú pháp & kiến trúc, Toàn bộ bài, Tự kiểm tra.
- Khối code: tra ký hiệu và hàm/tool. Mã giảng dài được thu gọn để đối chiếu sau lần tự viết; CSS có khung thử cơ bản.
- Mốc thực hành: đầu ra, bài biến thể, tiêu chí và ghi bằng chứng.
- Ghi chú: lưu tại trình duyệt/địa chỉ đang mở; dùng Xuất/Nhập để có bản sao.
- In/PDF: mở hộp thoại in của trình duyệt; chưa có PDF dựng sẵn đi kèm.

Giữ id bài và storage key cũ để dùng lại ghi chú. Sắp lại thứ tự mục có thể
làm vị trí đọc cũ đổi nội dung; chọn lại bài nhỏ trong danh sách khi cần.
Các mô phỏng có phạm vi ghi ngay trong bài, không thay việc chạy project thật.

## Biết kiến thức nào cần cho dự án

Mở **Kiến thức dùng trong dự án** ở mục lục. Bản đồ 29 nhóm kiến thức ghi
rõ dùng ở đâu, vì sao phải hiểu, bằng chứng tự làm và liên kết đến đúng mục.
Nhãn có cả chữ, không chỉ dựa vào màu:

- **CỐT LÕI ĐỂ XÂY:** cú pháp, dữ liệu, UI, HTTP và kiến trúc nghiệp vụ.
- **CẦN TRƯỚC KHI CÓ USER:** quyền, migration, concurrency, test, đo tải,
  phát hành và phục hồi; học ở chặng tương ứng trước khi phát hành.
- **TRA KHI CÓ NHU CẦU:** cache/queue và mở rộng có bằng chứng nhu cầu.

Nhãn **DÙNG TRONG DỰ ÁN** đặt ngay cạnh mục liên quan, ở cả chế độ học từng
bước và toàn bộ bài. Mỗi bài có phần giải nghĩa cú pháp, luồng trách nhiệm,
câu hỏi đổi yêu cầu và ô tự viết trống. Bản nháp code/thiết kế được lưu và
xuất/nhập cùng ghi chú. S0 có 11 bài gõ ngay trong mục, kiểm output và một
số điều kiện biến/bảng vết; kết quả khớp không tự đánh dấu đã hiểu.

F0 bổ sung destructuring/spread/import; chương 02 bóc generic/Promise/Axios;
chương 04 phân tích cú pháp LoginForm thật; G4.10 dạy chọn trách nhiệm, ranh
giới transaction và cấu trúc cho Vision LMS. Tự viết trong môi trường học;
những ô ghi bản nháp không chạy/chấm toàn bộ JS/TS/Python.

## Bộ mã thực hành

Trong sách chọn **Tải bộ mã thực hành (.zip)**. Bộ tải có source/tài liệu được
chọn của studio và workshop, giữ cấu trúc thư mục, kèm các bài Markdown.
Node_modules, venv, DB, token, account và kết quả riêng không nằm trong ZIP.
Giữ file HTML để dùng tương tác; nó không được lồng vào chính ZIP của mình.

Đọc [studio/README](studio/README.md) để thay đường dẫn sau giải nén. Source
nhỏ theo G1/G2/G3 giúp đối chiếu từng bước. [workshop](workshop/README.md)
có lớp học và core loop giao → nộp → chấm/công bố, HTTP/React/SQLAlchemy cùng
deployment/perf lab. Điểm danh G5 có nghiệp vụ và SQLite; API/UI là bài nối tiếp
cần tự làm. Các module toàn LMS được triển khai dần theo G5 và nghiệm thu
từng luồng; tài liệu không tự tạo sẵn mọi module trong ứng dụng sản phẩm.

Bắt đầu code trong thư mục riêng, tự viết trước khi mở lời giải. Mẫu dạy về
đường chạy và hợp đồng; không thay yêu cầu sản phẩm của dự án thật.

## Tự kiểm và kiểm thực tế

[G6](G6-tu-lam-va-duoc-phan-hoi.md) có bài review mẫu, mức hỗ trợ, rubric sửa
lỗi, gói nộp code và bài đổi miền. [VALIDATION](VALIDATION.md) ghi chính xác
các phép kiểm đã chạy và giới hạn môi trường. Chưa có kết quả đo tải đại diện
để công bố capacity; Docker/MySQL/restore cần được chạy ở môi trường phù hợp.

Ví dụ kiểm bộ nhỏ từ repo gốc, dùng Python phù hợp:

    python -m unittest discover -s docs/course/studio/backend -p test_use_cases.py -v
    .\.venv\Scripts\python.exe -m unittest discover -s docs/course/studio/attendance -p test_attendance.py -v

Kiểm/bảo trì sách: [BOOK_AUTHORING](BOOK_AUTHORING.md). Phần source sản phẩm
trong [CODE_GUIDE](../CODE_GUIDE.md) dùng để đối chiếu repo hiện có, tách khỏi
bài tự xây. Môi trường, lệnh và phụ thuộc của mỗi lab nằm tại README của lab.
