# Bộ mã thực hành của đường học G0–G6

Đây là các bản đối chiếu sau khi tự làm, nằm riêng với ứng dụng sản phẩm.
Đọc [G0](../G0-cach-hoc-de-tu-xay.md) và làm theo từng buổi trong sách HTML.
Mỗi thư mục chỉ thêm một lớp kiến thức:

| Thư mục | Dùng sau bài | Có gì chạy được |
|---|---|---|
| frontend/vanilla | G1 | HTML/CSS/JS, thêm và tìm lớp trong RAM |
| frontend/react | G2 | Cùng nghiệp vụ, TypeScript/React, build riêng |
| backend | G3/G4 | Python một file và bản tách; patch lưu trữ lớp để đối chiếu |
| attendance | G5 | Nghiệp vụ/SQLite điểm danh, quyền, revision và transaction |

Mở README trong từng thư mục để biết lệnh, thư mục đứng và kết quả mong đợi.
Chạy code tham chiếu chứng minh được môi trường và hành vi mẫu trong phạm vi
đã kiểm. Muốn đánh giá tự làm, cần code riêng và bài biến thể của G6.

## Khi tải ZIP từ sách HTML

Giải nén vào thư mục học mới. ZIP có thư mục gốc lms-practice, các bài Markdown,
studio, workshop và ví dụ liên quan; giữ cây này để import và liên kết tương
đối có ý nghĩa. ZIP chỉ chứa source/tài liệu đối chiếu đã chọn, không có
node_modules, venv, database, thông tin tài khoản hoặc dữ liệu riêng.

Các lệnh trong bài minh họa đường dẫn của máy soạn. Nếu giải nén tại
D:\lms-practice, thay D:\vision-education-lms\docs\course bằng D:\lms-practice.
Ví dụ vào D:\lms-practice\studio\frontend\react rồi chạy npm.cmd ci và
npm.cmd run dev. Python không kèm venv trong ZIP: dùng interpreter phù hợp
hoặc tạo môi trường riêng theo README workshop và requirements của nó.

Giữ file GIAO-AN-LMS.html đã mở để học tương tác. File đó không được lồng vào
chính ZIP của nó; bản Markdown cũng đọc được bằng editor. Bản đồ source sản
phẩm và một số lệnh kiểm dành cho tác giả cần repo gốc, không nằm trong bộ
thực hành độc lập này. Các liên kết tài liệu bên ngoài cần mạng khi mở.

Để bắt đầu từ thư mục trắng, làm G1/G2 trước khi mở source cuối. Để chỉ kiểm
bản đối chiếu, dùng lệnh của từng README và ghi rõ đã chạy tham chiếu.
