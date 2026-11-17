# Hồ sơ dự án Vision Education LMS

Cập nhật ngày 15/11/2026. Dự án phục vụ trung tâm Toán của cô người dùng. Người dùng tự code khoảng một tiếng mỗi ngày, Codex hướng dẫn và review theo [luật làm việc](AGENTS.md).

Người dùng muốn LMS phục vụ công việc thật của trung tâm và làm tốt hơn các phần mềm bán sẵn trong những luồng cô thực sự cần. Luồng đổi ca tạm là đề xuất đầu tiên để đối chiếu với công cụ có sẵn và đo số bước cô phải xử lý thủ công.

## Mục tiêu học và phỏng vấn

- Người dùng làm LMS để tích lũy kinh nghiệm cho phỏng vấn xin thực tập, hướng tới các công ty công nghệ lớn, và ứng tuyển vào lab.
- Sau mỗi kiến thức hoặc phần code, liên hệ với câu hỏi phỏng vấn phù hợp dựa trên chính code LMS. Cho người dùng thử giải thích, truy vết luồng chạy hoặc dự đoán ca biên, rồi phản hồi để họ có thể tự trình bày quyết định và cách kiểm tra.
- Qua các phần của dự án, bao quát lý thuyết của toàn bộ framework, thư viện và công cụ thực tế đang dùng, từ frontend, backend và cơ sở dữ liệu đến công cụ phát triển, kiểm thử và vận hành. Mỗi phần liên hệ với công cụ đang dùng trong phần đó: cơ chế hoạt động, lý do chọn và ca biên hoặc cách kiểm chứng phù hợp cho phỏng vấn thực tập và ứng tuyển lab.
- Khi soạn câu hỏi, tham khảo tài liệu chính thức, mã nguồn, test, issue và PR trên GitHub, tài liệu nền tảng và hướng dẫn tuyển dụng hoặc tài liệu của lab khi phù hợp. Đối chiếu câu hỏi với code LMS và dẫn nguồn để người dùng đọc sâu. Giải thích cơ chế mới bằng đoạn code quen thuộc trước khi hỏi. Ưu tiên câu hỏi yêu cầu suy luận, giải thích quyết định hoặc đề xuất cách kiểm chứng, với độ khó tăng theo phần người dùng đã học.
- Khi mô phỏng phỏng vấn, người dùng muốn người hỏi khó tính để luyện tâm lý. Hỏi vặn khi câu trả lời mơ hồ, yêu cầu chỉ ra căn cứ trong code và đưa một ca biên để người dùng tự bảo vệ hoặc điều chỉnh lập luận. Cho người dùng trả lời trước rồi mới góp ý cụ thể.

## Nghiệp vụ đã chốt

- Trung tâm thường tổ chức thi online. Người dùng ưu tiên máy chủ đủ tài nguyên cho các ca thi thật, đặc biệt khi nhiều học sinh mở đề và nộp bài cùng lúc. Chưa chốt cấu hình hoặc số học sinh thi đồng thời.
- Trung tâm chỉ dạy ba khối 10, 11 và 12. Cô nhập khối khi tạo hồ sơ học sinh và có thể xếp lớp sau. Khối của học sinh lấy từ hồ sơ `students.grade`. Học sinh chưa được xếp lớp vẫn xem được lịch cả khối. Mỗi khối có nhiều lớp. Khi đã xếp lớp, học sinh đăng ký một lớp với lịch cố định, chỉ học môn Toán, đúng một buổi mỗi tuần.
- **Ca** là khung giờ. **Lịch cố định của lớp** gồm thứ trong tuần và ca. **Buổi học** là lần học cụ thể, có ngày, giờ và nội dung, dùng để lập danh sách tham dự và điểm danh. Các khung giờ đã bàn để minh họa là sáng 07:30–10:30, chiều 14:00–17:00 và tối 18:00–21:00. Dữ liệu buổi học phân loại nội dung Toán bằng chủ đề (`topic`) và các cờ chuyên đề: Đại số (`has_algebra`), Hình học (`has_geometry`), Ôn tập (`is_review`).
- Trang **Lịch học** hiển thị số tuần học và khoảng ngày, cho học sinh chọn tuần. Người dùng xác nhận tuần trên lưới tính từ thứ Hai đến Chủ nhật. Học sinh xem các buổi theo ngày và ca, có giờ bắt đầu, giờ kết thúc và nội dung học. Giao diện chọn ca không cần hiện tên hoặc mã lớp.
- Khi bấm tuần trước hoặc tuần sau, học sinh phải thấy lịch mới nhất của đúng tuần đã chọn. Nếu giáo viên dời hoặc hủy buổi, hoặc học sinh đổi ca hay hủy lần đổi, lịch đang mở của học sinh bị ảnh hưởng phải tự cập nhật theo thời gian thực mà không cần tải lại trang.
- API `GET /schedule/weekly` nhận ngày được chọn qua `week_start`, kể cả các ngày giữa tuần. Service tính 00:00 thứ Hai của tuần chứa ngày đó và trả ngày thứ Hai trong response cùng `sessions`, `my_session_ids` và `transferred_session_ids`. Mỗi buổi chỉ gồm `id`, `topic`, `starts_at` và `ends_at` để dựng lưới. Khi nối thao tác chọn một ngày trên lịch mini, frontend có thể gửi ngày được chọn trực tiếp.
- Trên lưới tuần, buổi học học sinh sẽ tham dự được tô khác màu và có nhãn **Ca của bạn**. Người dùng muốn giữ hai thao tác: lấy danh sách buổi của cả khối và xác định buổi của học sinh trong tuần đang xem để phục vụ lưới và thẻ bên phải. Với ca đăng ký, người dùng đề xuất đối chiếu `class_id` của buổi với `class_id` trong đăng ký lớp. Frontend quyết định màu sắc hiển thị dựa trên buổi được xác định.
- Người dùng muốn giữ ô buổi gốc trên lưới và có dấu hiệu rõ ràng để học sinh nhận ra đây là ca đã đổi. Đề xuất dùng nhãn **Đã chuyển ca** kèm biểu tượng đổi lịch. Ca thay thế mang nhãn **Ca của bạn**.
- Người dùng xác nhận một học sinh có thể được xếp hai buổi trong cùng tuần trên lưới nếu hai buổi thuộc hai tuần dạy khác nhau. Nếu nhiều buổi đều khớp lịch lớp và cùng tuần dạy thì chỉ buổi được xếp mới có màu và nhãn **Ca của bạn**. Các buổi còn lại vẫn thuộc lịch cả khối. Đề xuất chờ chốt: để service chọn buổi có `starts_at` sớm hơn khi hai ca thường lệ cùng tuần dạy, rồi áp dụng lần đổi tạm hợp lệ nếu có.
- Nút **Đổi lịch học** cho chọn **đổi tạm thời** hoặc **đổi cố định**.
  - **Đổi tạm thời** chỉ áp dụng cho **buổi học tiếp theo của học sinh**. Học sinh chọn một buổi khác dạy cùng nội dung theo ngày, ca và giờ trên lưới tuần. Khi đổi thành công, cô thấy học sinh trong danh sách điểm danh buổi mới. Buổi gốc thể hiện học sinh đã chuyển buổi để cô phân biệt với vắng mặt. Lớp đăng ký được giữ và các tuần sau học theo lịch gốc.
  - Người dùng xác nhận cho đổi tạm sang tuần lịch sau nếu buổi thay thế thuộc cùng tuần dạy trong chương trình với buổi gốc. Lưới tuần gốc hiện **Đã chuyển ca** và lưới tuần đích hiện **Ca của bạn**. Cách lưu tuần dạy còn cần chốt.
  - Học sinh có thể đổi nhiều lần trong cùng một tuần, miễn lần đổi vẫn áp dụng cho buổi học tiếp theo và còn ca thay thế dạy cùng nội dung. Khi chọn lại ca thay thế cho cùng buổi gốc, cập nhật buổi đích trong lần đổi hiện tại để mỗi buổi gốc của học sinh có tối đa một ca thay thế đang được chọn.
  - Người dùng lưu ý có thể hết buổi dạy cùng nội dung để thay thế cho buổi tiếp theo. Cần chốt trạng thái giao diện khi danh sách ca thay thế trống.
  - **Đổi cố định** chuyển lớp hoặc ca đăng ký từ thời điểm có hiệu lực. Xác định lớp của học sinh theo đăng ký có hiệu lực lúc từng buổi bắt đầu. Các buổi sau theo lịch mới và lịch sử đã học được giữ.
- Khi giáo viên dời ngày hoặc giờ của cùng một buổi, học sinh đã đăng ký buổi đó đi theo lịch mới, kể cả học sinh đã chọn buổi đó khi đổi ca tạm. Cập nhật ngày giờ trên chính `ClassSession` để các liên kết theo ID buổi tiếp tục áp dụng.

## Phương án vận hành đã chốt

- Đăng ký một tên miền `.com`. Có thể dùng tên miền gốc cho website trung tâm và tên miền con `lms.` cho LMS. Chưa chọn tên cụ thể.
- Tự vận hành React, FastAPI và MySQL trên một VPS Việt Nam. Thử gói 4 vCPU / 8 GB với kịch bản 500 học sinh đăng nhập, mở đề, lưu đáp án và nộp dồn. Giữ gói nếu hệ thống phản hồi ổn, ghi đủ bài và còn dư tài nguyên. Gói 6 vCPU / 12 GB là phương án dự phòng nếu thử tải cho thấy cần nâng cấu hình. Kịch bản 400–500 người dùng đồng thời là mốc dự toán, lượng truy cập thực tế chưa được xác nhận.
- Sao lưu MySQL ngoài VPS mỗi đêm và ngay sau ca thi. Thử khôi phục trước khi dùng thật. Cloudflare R2 Standard là phương án lưu trữ dùng để dự toán. Thời gian giữ bản sao sẽ chốt khi triển khai.
- Video bài giảng đăng trên Google Drive hoặc YouTube và đưa liên kết vào LMS. Dự toán hạ tầng không có khoản phát video trực tiếp từ LMS. Chưa chốt nền tảng ưu tiên và quyền xem.
- Dự toán gồm VPS, tên miền và sao lưu ngoài VPS, với giả định tự vận hành. Khoảng 420.000đ/tháng cho gói thử, 670.000đ/tháng cho gói dự phòng và để ngân sách 700.000đ/tháng (8,4 triệu đồng/năm).
- Mức thu LMS là 50.000đ/học sinh/năm. Dự toán với 500 học sinh đóng đủ là 25 triệu đồng/năm. Sau khi trừ ngân sách hạ tầng 8,4 triệu đồng/năm, còn 16,6 triệu đồng trước khi tính công vận hành và các chi phí khác.

## Câu còn mở

- Khi đổi tạm qua tuần lịch, còn cần chốt lưới tuần gốc có hiển thị thêm ngày của ca đích bên cạnh nhãn **Đã chuyển ca** hay không.
- Cơ chế đẩy cập nhật lịch theo thời gian thực và cách đồng bộ lại khi kết nối gián đoạn còn cần chốt. Quy tắc tính buổi tiếp theo và quy tắc xử lý hủy buổi vẫn là các quyết định nghiệp vụ riêng.
- Người dùng nêu tình huống học sinh muốn hủy lần đổi tạm để quay lại buổi gốc và chọn cho `replacement_session_id` nhận `NULL` với giá trị mặc định là `NULL`. Cần chốt ý nghĩa nghiệp vụ của dòng có `NULL`, hạn hủy và có cần lưu lịch sử các lần đổi đã hủy hay không.
- Cần chốt cách thông báo khi giáo viên dời giờ hoặc hủy buổi đã có học sinh đăng ký. Khi buổi thay thế bị hủy, cần chốt cách xử lý lần đổi và ca gốc, đặc biệt nếu ca gốc đã qua. Hiện truy vấn loại buổi thay thế bị hủy khỏi lưới, còn ca gốc vẫn hiện **Đã chuyển ca** nếu lần đổi còn lưu.
- Người dùng cân nhắc gộp dữ liệu học sinh tham gia từng buổi với dữ liệu đổi ca và nhấn mạnh mục tiêu là biết học sinh được xếp vào buổi nào khi buổi diễn ra. Cần chốt cách lưu danh sách dự kiến và kết quả điểm danh thực tế, đồng thời phục vụ yêu cầu hiển thị **Đã chuyển ca** ở buổi gốc. Model đổi ca đã có, còn model điểm danh chưa được triển khai.
- Mốc tính **Tuần học 1**. Ngày khai giảng của từng khóa là một đề xuất đang chờ chốt.
- Người dùng muốn xác định mỗi lớp đang dạy đến buổi thứ mấy, đề xuất đếm theo tuần và cân nhắc lưu `week` ở model lớp. Codex đề xuất lưu tuần dạy trên từng `ClassSession` để so buổi gốc với buổi thay thế, vì các buổi của cùng một lớp có thể mang số tuần khác nhau. Còn cần chốt cách ghi tuần khi lớp nghỉ hoặc học bù và việc dùng tiến độ để kiểm tra lớp đích khi chuyển cố định.
- Thẻ **Buổi học tiếp theo** có dòng phòng học trong ảnh tham chiếu. Chưa chốt phòng được gán theo lớp hay theo buổi. Model `Class` và `ClassSession` hiện chưa có trường phòng.
- Quy trình **đổi cố định**. Cần xác nhận học sinh tự đổi hay cô hoặc trợ giảng duyệt. Người dùng nêu trường hợp cô duyệt lúc 15:00 và cho học sinh vào ngay buổi 14:00–17:00 của lớp đích, đồng thời hỏi có cần bản ghi riêng theo buổi. Phương án đang bàn là giữ mốc hiệu lực của đăng ký lớp và lưu thêm việc xếp học sinh vào đúng buổi đang diễn ra. Cần chốt có hỗ trợ trường hợp này và xử lý lịch hoặc điểm danh buổi lớp cũ ra sao nếu trùng giờ.
- Chuyển khối khi sang năm học mới. Người dùng đã cân nhắc tăng `grade` thêm 1 sau mỗi năm và quyết định để logic này làm sau khi có model `Student`. Chưa chốt mốc chuyển khối và cách thực hiện.

## Thiết kế dữ liệu Lịch học đang bàn

- Người dùng chốt tên `students.student_id` cho khóa chính kiêm khóa ngoại đến `users.id`. `grade` là số nguyên bắt buộc và giới hạn ở 10, 11, 12. `classes.grade` xác định lớp thuộc khối nào. `class_enrollments` xác định ca của học sinh tại thời điểm buổi học.
- Các phương án đã cân nhắc cho đổi tạm: dùng dòng `ClassEnrollment` riêng theo giờ ca mới, hoặc đổi `class_id` theo khoảng thời gian rồi quay lại lớp cũ. ID lớp và `ends_at` cũng có thể thay đổi khi đổi lớp cố định. Nếu ca thay thế diễn ra trước ca gốc, chỉ dùng khoảng hiệu lực thì ca gốc có thể hiện lại sau khi ca thay thế kết thúc.
- Model đổi tạm đã lưu trong `backend/app/models/schedule.py` với tên hiện tại `SessionsTransfer`, bảng `sessions_transfers`. Đã kiểm tra metadata: `student_id` trỏ `students.user_id`, hai ID buổi trỏ `class_sessions.id`, khóa chính ghép `(student_id, original_session_id)`, và cột `replacement_sessions_id` cho phép `NULL`. Tên dự kiến từng bàn là `SessionTransfer`, `session_transfers` và `replacement_session_id`. Chưa có migration cho bảng này.
- Người dùng cân nhắc lưu lớp thường lệ trực tiếp trên hồ sơ học sinh khi đã có `SessionTransfer`. Nếu chỉ cần lớp hiện tại, có thể dùng `students.class_id` cho phép `NULL` khi chưa xếp lớp. Với nghiệp vụ giữ lịch sử khi đổi lớp cố định, `ClassEnrollment` lưu lớp thường lệ theo từng khoảng hiệu lực. Chưa chốt thay đổi schema theo hướng lưu trực tiếp.
- Các điểm đã được đề xuất để rà khi triển khai: cân nhắc cho `class_enrollments.student_id` trỏ đến `students.student_id`, kiểm tra khối của lớp khớp hồ sơ khi xếp lớp, tạo tài khoản và hồ sơ học sinh trong cùng transaction, và bổ sung hồ sơ cho tài khoản học sinh đã có bằng khối được xác nhận.
- Người dùng đề xuất gộp tra khối vào hai truy vấn buổi học trong repository để bỏ hàm `get_student_grade()` riêng. Phương án còn đang cân nhắc vì truy vấn gộp cần phân biệt thiếu hồ sơ học sinh với tuần không có buổi nếu vẫn dùng `StudentGradeNotFoundException`.

## Giao diện đang thử nghiệm

- **Trang Lịch học (`/schedule`)**: Lưu trữ 3 phương án tham chiếu theo tiến trình góp ý của người dùng:
  - **Mốc tham chiếu chuẩn đã xác nhận (Baseline Approved)**: Người dùng xác nhận hiển thị trên **laptop 15 inch 16:9 ở Chrome** là đạt chuẩn vừa mắt ("đang là ok") với chiều cao hàng ~142px, tỷ lệ ô cân đối (dạng card đứng nhẹ), khoảng thở đáy vừa vặn và panel bên phải chỉ gồm đúng 2 thành phần (*Buổi học tiếp theo* và *Đổi lịch học*).
  - **Kho lưu trữ 3 bản ưng ý**:
    - **Bản ưng số 1 (Full Height `flex-1` gốc)**: Lưu tại `frontend/public/schedule-mockup-v1.html` và [schedule_preview_v1.html](schedule_preview_v1.html).
    - **Bản ưng số 2 (Chuẩn 152px gốc)**: Lưu tại `frontend/public/schedule-mockup-v2.html` và [schedule_preview_v2.html](schedule_preview_v2.html).
    - **Bản ưng số 3 (Chuẩn 142px — Bản hoàn tác nguyên trạng)**: Lưu tại `frontend/public/schedule-mockup-v3.html`. Đang áp dụng làm mặc định tại `frontend/public/schedule-mockup.html`, [schedule_preview.html](schedule_preview.html) và component React [ScheduleOptionA.tsx](frontend/src/features/schedule/components/ScheduleOptionA.tsx).
  - **Bài học thiết kế Responsive trên màn Desktop 24 inch (1920×1080)**:
    - *Lỗi giãn đứng tràn màn hình (`flex-1` / `1fr`)*: Khiến 3 hàng ca bị kéo dài ngoằng tới ~280px mỗi hàng, ô biến thành khoảng trống rỗng khổng lồ với 80% diện tích trắng chết, tạo cảm giác rời rạc và lệch tỷ lệ hoàn toàn so với panel bên phải (vốn chỉ có 2 thẻ cao ~240px). Người dùng đã bác bỏ phương án này vì làm mất vẻ đẹp cân đối của Bản ưng 3.
    - *Lỗi giãn ngang không giới hạn với hàng cố định 142px*: Khi bề ngang tràn tới 1580px mà chiều cao giữ 142px, các ô bị bẹt ngang thành hình chữ nhật lùn ("béo phì"), đồng thời đáy màn hình 24" bị hẫng một mảng trống xám ~400px.
    - *Định hướng xử lý chuẩn cho màn hình lớn*: Giữ nguyên tỷ lệ ô vàng của Bản ưng 3 (~1 : 1.25 đến 1 : 1.35), dùng container có `max-w` hài hòa hoặc tỷ lệ co dãn tỷ lệ thuận (aspect-ratio bento) thay vì kéo dãn tự do một chiều gây biến dạng giao diện.
  - Phối màu và icon đặc trưng:
    - Ca 1 · Sáng (07:30–10:30): nền `#EAF2FF`, icon mặt trời mọc xanh biển.
    - Ca 2 · Chiều (14:00–17:00): nền `#FFF3E6`, icon mặt trời chiều màu cam hổ phách.
    - Ca 3 · Tối (18:00–21:00): nền `#ECECFE`, icon mặt trăng tím.
    - Cột T3 nổi bật với capsule gradient tím `#4543D4` đến `#312FB5`.
    - Buổi "Ca của bạn": viền `#3E3C8E`, nền `#EAE9FC`, badge tím đậm `#4341CC`.
    - Buổi "Cùng bài": dùng các tông màu pastel dịu (lavender `#ECEBFC`, amber `#FFF4E5`, mint `#ECFAF0`).
  - Panel bên phải: Thẻ Buổi học tiếp theo bo góc 22px với họa tiết sóng tím uốn lượn SVG ở góc trên, nút **Đổi lịch học** cao 52px với dải gradient `from-[#4543D0] via-[#4A48D6] to-[#3432B0]` và shadow tím 3D `shadow-[0_8px_20px_rgba(69,67,208,0.28)]`.
  - Sidebar: Giữ logo Vision Education và hình minh họa mũ cử nhân đặt trên sách ở góc dưới.
- Thiết kế và kiểm tra trang **Lịch học** đáp ứng tối ưu cả hai kích cỡ màn hình tỷ lệ **16:9**: laptop học sinh 14–15 inch (1366×768 / 1080p scale 125%) và màn hình desktop của người dùng 24 inch (1920×1080 scale 100%).
- Mục **Lịch học** ở sidebar và ô lịch mini trên Trang chủ đều mở cùng một trang. `/schedule` là đường dẫn dự kiến. Hai mũi tên trên lịch mini dành cho chuyển tháng.
- Dùng lại logo, sidebar và thanh trên của dashboard để trang Lịch học trông như một phần của cùng ứng dụng. Phần đầu trang dùng tiêu đề và điều hướng tuần gọn. Người dùng bỏ banner lớn ở trang con.
- Yêu cầu bắt buộc của người dùng: trang Lịch học dùng đúng nền và màu component của dashboard hiện tại. Dùng chung cách phối màu của thẻ, nút, viền và trạng thái chọn. Không tự thêm màu nền hoặc bảng màu riêng cho trang này. Đối chiếu code: nền `#F8FAFD`, thẻ trắng, viền `#EAEFF5`, màu chính `#5553E6` và nền nhấn `#EEF0FD`.

## Điểm dừng

- **Mở lại buổi sau:**
  1. Người dùng chạy `npm --prefix frontend run dev` hoặc mở [schedule_preview.html](schedule_preview.html) để xem và chọn 1 trong 3 phương án giao diện (A, B hoặc C).
  2. Trong [repository.py](backend/app/modules/schedule/repository.py#L30), `get_sessions_in_range()` đã dùng `ClassSession` ở cả hai mốc thời gian (`>= starts_from`, `< starts_before`) và trả danh sách qua `.all()`.
  3. `get_weekly_sessions(user_id, week_start)` đã lưu đúng luồng tra khối, ném `StudentGradeNotFoundException` khi `grade is None` và truyền đầu tuần cùng đầu tuần kế tiếp vào repository. Còn cần kiểm thử các ca thiếu khối, tuần trống và buổi đúng đầu tuần sau.
- Dashboard đã lấy hồ sơ qua `GET /me`. `MiniCalendarCard` đang hiển thị dữ liệu mẫu. Route `/schedule` đã được đăng ký và Sidebar đã điều hướng tới trang lịch.
- Đã có model và file migration cho `classes`, `class_enrollments` và `class_sessions`. Người dùng xác nhận mới tạo các migration này, chưa áp dụng vào MySQL. Các migration hiện tại chưa khai báo bốn cột của model `ClassSession` gồm `topic`, `has_algebra`, `has_geometry` và `is_review`.
- Người dùng quyết định hoãn áp dụng migration Lịch học vì chưa có dữ liệu thật.
- File `backend/app/models/student.py` đã có model `Student` với `CheckConstraint` giới hạn khối 10, 11, 12. Bản trên đĩa hiện vẫn đặt tên khóa chính là `user_id`. Chưa có migration `students`. Model `ClassEnrollment` đã trỏ `student_id` tới `students.user_id`, còn migration hiện tại vẫn trỏ tới `users.id`. Backend sản phẩm chưa có API tạo/import học sinh. Script seed tạo tài khoản `User` vai trò `STUDENT`.
- Repository lịch có `get_student_grade(user_id)` và `get_upcoming_sessions(grade, starts_from, limit=5)`. Hàm lấy tối đa 5 buổi theo khối hiện chưa có nơi gọi và người dùng xác nhận không cần cho phần đang làm. API lịch tuần đã đăng ký trong FastAPI và được kiểm tra qua HTTP với SQLite in-memory. Chưa kiểm tra trên MySQL.
- Người dùng chốt backend xác định ID buổi **Ca của bạn** và ID buổi **Đã chuyển ca** trên lưới tuần, gồm cả buổi đã qua và buổi sắp tới. Service dựa vào lịch cả khối và đăng ký lớp để tìm ca thường lệ, rồi áp dụng lần đổi tạm. Frontend đọc hai danh sách ID để tô màu và gắn nhãn.
- Người dùng mô tả luồng đọc lịch cá nhân: lấy các buổi `scheduled` đã được xếp, rồi thay buổi gốc bằng buổi đã chọn khi có lần đổi cùng tuần dạy. Khi áp dụng lần đổi đã lưu, đề xuất dùng `original_session_id` để xác định đúng buổi cần thay, dùng `week` để kiểm tra cùng nội dung và dùng ngày giờ của buổi cuối cùng để xác định nó có nằm trên lưới đang xem.
- `weekly/service.py` lấy lưới cả khối qua `WeeklyScheduleRepository`, dùng lại truy vấn đăng ký lớp và lần đổi ca từ `ScheduleRepository`, trả hai danh sách ID ca cá nhân. Đã kiểm tra trên SQLite việc đổi lớp đúng tại mốc hiệu lực, lần đổi xuất hiện đúng ở hai tuần, lần đổi có buổi thay thế `NULL`, dữ liệu của học sinh khác và tuần trống. Service đọc lần đổi đã lưu theo ID hai buổi. Model chưa có dữ liệu tuần dạy để xác thực điều kiện cùng tuần dạy khi lưu lần đổi.
- Phạm vi của thẻ **Buổi học tiếp theo** vẫn cần chốt khi tuần đang xem không còn buổi tương lai của học sinh: hiển thị trạng thái trống hay tìm tiếp ở tuần sau.
- Người dùng đang tự code tiếp tính năng **Lịch học**. Mốc giao diện đề xuất là dựng trang dùng chung khung dashboard, nối hai lối vào và hiển thị một tuần học mẫu. Kiểm tra bằng cách mở từ cả sidebar và lịch mini.

## Điểm dừng

- **Ngày 17/11/2026:** Người dùng chốt cấu trúc Package by Feature cho module Schedule, chia thành 3 sub-module chuyên biệt: `weekly/`, `temporary_transfers/`, và `permanent_transfers/`. Khởi tạo khung thư mục và các file rỗng chuẩn mực (`router.py`, `service.py`, `repository.py`, `schemas.py`) để người dùng tự tay viết code sạch sẽ từ đầu.

- **Mốc triển khai hiện tại:** Người dùng đồng ý bắt đầu từ luồng xem lịch tuần. Mốc hoàn thành khi học sinh mở `/schedule`, chuyển tuần và thấy đúng lịch của khối mình từ API. Ca cá nhân, buổi tiếp theo, đổi tạm và đổi cố định là các chức năng tiếp theo của trang.
- **Ngày 18/11/2026:** Người dùng ưu tiên làm đúng luồng chuyển tuần và đồng bộ các thay đổi ngay trên lưới đang mở. API đọc lịch tuần đã có, còn cần nối frontend và triển khai cơ chế đẩy cập nhật.
- **Điểm dừng:** Người dùng tự tạo bản giao diện Lịch học để tiếp tục phần frontend sau khi hoàn thành API đọc lịch tuần.
- **Phạm vi thử giao diện:** Người dùng chốt nối API lịch tuần với dữ liệu mẫu để kiểm tra hai nút chuyển tuần và xác nhận lưới hiển thị đủ các buổi của tuần đang xem.

## Điểm vào mã nguồn

- Frontend đăng ký route trong [App.tsx](frontend/src/App.tsx). Khung dashboard nằm ở [DashboardLayout.tsx](frontend/src/features/dashboard/components/DashboardLayout.tsx) và trang học sinh ghép các thẻ trong [StudentDashboardPage.tsx](frontend/src/features/dashboard/pages/StudentDashboardPage.tsx).
- Backend đăng ký router trong [main.py](backend/app/main.py). Luồng xác thực nằm trong [modules/auth](backend/app/modules/auth), còn truy vấn lịch ở [repository.py](backend/app/modules/schedule/repository.py). Model nằm trong [app/models](backend/app/models) và migration nằm trong [alembic/versions](backend/alembic/versions).

## Việc kỹ thuật để xử lý sau

Người dùng ưu tiên code trang **Lịch học** trước. Ba điểm dưới đây được ghi nhận qua review code, chưa kiểm thử tích hợp.

- **Tài khoản bị khóa:** `/auth/me` kiểm tra `is_active`, còn luồng đổi mật khẩu chưa kiểm tra. Xử lý trước khi đưa hệ thống cho học sinh dùng thật.
- **Đổi mật khẩu lần đầu:** Form đăng nhập điều hướng theo `must_change_password`, nhưng truy cập trực tiếp dashboard chưa áp dụng quy tắc này.
- **Dashboard khi lỗi tải hồ sơ:** Khi `/auth/me` lỗi mạng hoặc trả 500, giao diện có thể giữ trạng thái “Đang tải...”.

Nguồn trao đổi nghiệp vụ: chat [Review toàn bộ tools dự án](codex://threads/01a1a199-e1d5-7be3-99bb-4813519d8db1). [Roadmap](PROJECT_ROADMAP.md) mô tả phạm vi rộng hơn của sản phẩm.
