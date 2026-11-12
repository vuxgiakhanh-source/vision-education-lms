# Hồ sơ dự án Vision Education LMS

Cập nhật ngày 13/11/2026. Dự án phục vụ trung tâm Toán của cô người dùng. Người dùng tự code khoảng một tiếng mỗi ngày, Codex hướng dẫn và review theo [luật làm việc](../AGENTS.md).

Người dùng muốn LMS phục vụ công việc thật của trung tâm và làm tốt hơn các phần mềm bán sẵn trong những luồng cô thực sự cần. Luồng đổi ca tạm là đề xuất đầu tiên để đối chiếu với công cụ có sẵn và đo số bước cô phải xử lý thủ công.

## Nghiệp vụ đã chốt

- Trung tâm thường tổ chức thi online. Người dùng ưu tiên máy chủ đủ tài nguyên cho các ca thi thật, đặc biệt khi nhiều học sinh mở đề và nộp bài cùng lúc. Chưa chốt cấu hình hoặc số học sinh thi đồng thời.
- Trung tâm chỉ dạy ba khối 10, 11 và 12. Cô nhập khối khi tạo hồ sơ học sinh và có thể xếp lớp sau. Khối của học sinh lấy từ hồ sơ `students.grade`. Học sinh chưa được xếp lớp vẫn xem được lịch cả khối. Mỗi khối có nhiều lớp. Khi đã xếp lớp, học sinh đăng ký một lớp với lịch cố định, chỉ học môn Toán, đúng một buổi mỗi tuần.
- **Ca** là khung giờ. **Lịch cố định của lớp** gồm thứ trong tuần và ca. **Buổi học** là lần học cụ thể, có ngày, giờ và nội dung, dùng để lập danh sách tham dự và điểm danh. Các khung giờ đã bàn để minh họa là sáng 07:30–10:30, chiều 14:00–17:00 và tối 18:00–21:00. Dữ liệu buổi học phân loại nội dung Toán bằng chủ đề (`topic`) và các cờ chuyên đề: Đại số (`has_algebra`), Hình học (`has_geometry`), Ôn tập (`is_review`).
- Trang **Lịch học** hiển thị số tuần học và khoảng ngày, cho học sinh chọn tuần. Học sinh xem các buổi theo ngày và ca, có giờ bắt đầu, giờ kết thúc và nội dung học. Giao diện chọn ca không cần hiện tên hoặc mã lớp.
- Nút **Đổi lịch học** cho chọn **đổi tạm thời** hoặc **đổi cố định**.
  - **Đổi tạm thời** áp dụng cho một buổi. Học sinh tự chọn một buổi khác dạy cùng nội dung và hệ thống ghi nhận ngay. Học sinh xem các lựa chọn theo ngày, ca, giờ và nội dung ngay trên lưới tuần. Cô thấy học sinh trong danh sách điểm danh buổi mới. Buổi gốc thể hiện học sinh đã chuyển buổi để cô phân biệt với vắng mặt. Lớp đăng ký được giữ và các tuần sau học theo lịch gốc.
  - **Đổi cố định** chuyển lớp hoặc ca đăng ký từ thời điểm có hiệu lực. Các buổi sau theo lịch mới và lịch sử đã học được giữ.

## Câu còn mở

- Vận hành LMS khi cô và học sinh dùng thật. Người dùng muốn đánh giá phương án triển khai theo nhu cầu thực tế của trung tâm và chi phí duy trì. Người dùng thấy mức 300.000đ/tháng tiền VPS quá đắt và đang cân nhắc gói 4 GB RAM với kịch bản khoảng 300 học sinh thi online cùng lúc. Đây là mốc để dự toán và thử tải, chưa xác nhận lượng truy cập thực tế hoặc cấu hình hosting.
- Mốc tính **Tuần học 1**. Ngày khai giảng của từng khóa là một đề xuất đang chờ chốt.
- Quy trình **đổi cố định**. Cần xác nhận học sinh tự đổi hay cô hoặc trợ giảng duyệt.
- Chuyển khối khi sang năm học mới. Người dùng đã cân nhắc tăng `grade` thêm 1 sau mỗi năm và quyết định để logic này làm sau khi có model `Student`. Chưa chốt mốc chuyển khối và cách thực hiện.

## Thiết kế dữ liệu Lịch học đang bàn

- Người dùng chốt tên `students.student_id` cho khóa chính kiêm khóa ngoại đến `users.id`. `grade` là số nguyên bắt buộc và giới hạn ở 10, 11, 12. `classes.grade` xác định lớp thuộc khối nào. `class_enrollments` xác định ca của học sinh tại thời điểm buổi học.
- Các điểm đã được đề xuất để rà khi triển khai: cân nhắc cho `class_enrollments.student_id` trỏ đến `students.student_id`, kiểm tra khối của lớp khớp hồ sơ khi xếp lớp, tạo tài khoản và hồ sơ học sinh trong cùng transaction, và bổ sung hồ sơ cho tài khoản học sinh đã có bằng khối được xác nhận.

## Giao diện đang thiết kế

- Người dùng không hài lòng với bản phác lịch tràn viền và yêu cầu thiết kế lại từ đầu. Các ghi chú về bố cục và phong cách của những bản trước là tham chiếu cho quá trình thử, chưa phải yêu cầu cho hướng mới.
- Sau bản thử thiết kế lại, người dùng gửi một ảnh khác làm gốc cho lượt chỉnh trực tiếp. Ảnh này có lưới tuần bên trái, chi tiết buổi Toán bên phải và dùng logo Vision Education hiện tại. Đây là mẫu cho lượt chỉnh ảnh, bố cục cuối chưa được chốt.
- Thiết kế và kiểm tra trang **Lịch học** trước trên màn laptop học sinh 14–15 inch, với bản phác đúng tỷ lệ **16:9**.
- Mục **Lịch học** ở sidebar và ô lịch mini trên Trang chủ đều mở cùng một trang. `/schedule` là đường dẫn dự kiến. Hai mũi tên trên lịch mini dành cho chuyển tháng.
- Dùng lại logo, sidebar và thanh trên của dashboard để trang Lịch học trông như một phần của cùng ứng dụng. Phần đầu trang dùng tiêu đề và điều hướng tuần gọn. Người dùng bỏ banner lớn ở trang con.
- Yêu cầu bắt buộc của người dùng: trang Lịch học dùng đúng nền và màu component của dashboard hiện tại. Dùng chung cách phối màu của thẻ, nút, viền và trạng thái chọn. Không tự thêm màu nền hoặc bảng màu riêng cho trang này. Đối chiếu code: nền `#F8FAFD`, thẻ trắng, viền `#EAEFF5`, màu chính `#5553E6` và nền nhấn `#EEF0FD`.
- Lưới tuần là phần chính, chiếm gần hết chiều ngang và chiều cao vùng nội dung bên phải sidebar. Ô ngày và ô ca rộng, với lề ngoài mỏng. Bản tham chiếu ngày 11/11/2026 được dùng để lấy phong cách bo góc và màu sáng, đặc biệt là màu pastel trong các ô ca.
- Lưới tuần hiển thị buổi Toán đã đăng ký và các ca dạy cùng bài để học sinh thấy ngay lựa chọn đổi tạm. Bản phác phân biệt các ca sáng, chiều và tối bằng màu, đồng thời dùng nhãn và kiểu viền để phân biệt ca của học sinh với ca tương đương. Dữ liệu minh họa chỉ dùng môn Toán.

## Điểm dừng

- Dashboard đã lấy hồ sơ qua `GET /me`. `MiniCalendarCard` đang hiển thị dữ liệu mẫu. Sidebar đã có mục **Lịch học**. Trang `/schedule` và luồng đổi lịch chưa được triển khai.
- Đã có model và file migration cho `classes`, `class_enrollments` và `class_sessions`. Người dùng xác nhận mới tạo các migration này, chưa áp dụng vào MySQL. SQL sinh offline đến `head` chưa có bốn cột mà model `ClassSession` khai báo: `topic`, `has_algebra`, `has_geometry` và `is_review`. `ScheduleRepository.get_student_upcoming_sessions()` mới viết dở và chưa có API lịch học.
- Người dùng quyết định hoãn áp dụng migration Lịch học vì chưa có dữ liệu thật.
- File `backend/app/models/student.py` đã có model `Student` với `CheckConstraint` giới hạn khối 10, 11, 12. Bản trên đĩa hiện vẫn đặt tên khóa chính là `user_id`. Chưa có migration `students` và repository lịch chưa có hàm lấy khối. `class_enrollments.student_id` đang trỏ tới `users.id`. Backend sản phẩm chưa có API tạo/import học sinh. Script seed tạo tài khoản `User` vai trò `STUDENT`.
- Người dùng đang tự code tiếp tính năng **Lịch học**. Mốc giao diện đề xuất là dựng trang dùng chung khung dashboard, nối hai lối vào và hiển thị một tuần học mẫu. Kiểm tra bằng cách mở từ cả sidebar và lịch mini.

## Việc kỹ thuật để xử lý sau

Người dùng ưu tiên code trang **Lịch học** trước. Ba điểm dưới đây được ghi nhận qua review code, chưa kiểm thử tích hợp.

- **Tài khoản bị khóa:** `/auth/me` kiểm tra `is_active`, còn luồng đổi mật khẩu chưa kiểm tra. Xử lý trước khi đưa hệ thống cho học sinh dùng thật.
- **Đổi mật khẩu lần đầu:** Form đăng nhập điều hướng theo `must_change_password`, nhưng truy cập trực tiếp dashboard chưa áp dụng quy tắc này.
- **Dashboard khi lỗi tải hồ sơ:** Khi `/auth/me` lỗi mạng hoặc trả 500, giao diện có thể giữ trạng thái “Đang tải...”.

Nguồn trao đổi nghiệp vụ: chat [Review toàn bộ tools dự án](codex://threads/01a1a199-e1d5-7be3-99bb-4813519d8db1). [Roadmap](../PROJECT_ROADMAP.md) mô tả phạm vi rộng hơn của sản phẩm.
