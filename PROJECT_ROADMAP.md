# Roadmap Vision Education LMS

LMS dành cho trung tâm Toán khối 10–12. Mốc đang triển khai là học sinh xem lịch đúng khối và chuyển tuần từ dữ liệu thật.

[Hồ sơ dự án](PROJECT_CONTEXT.md) · [Thiết kế tổng thể](docs/design/architecture.md) · [Thiết kế dữ liệu](docs/design/database.md) · [Design system](docs/design/design-system.md) · [Đặc tả Weekly](docs/design/weekly.md) · [Sprint Weekly](docs/planning/weekly-sprint.md)

---

## Phạm vi tính năng

Danh sách này gồm cả các tính năng đang làm và các ý tưởng cho mốc sau. Dùng bảng mốc bên dưới để xem thứ tự triển khai đề xuất.

### 1. 🛡️ Module 1: Authentication & Phân quyền (RBAC)
- **Vai trò trong model hiện tại** gồm quản trị viên, giáo viên, trợ giảng và học sinh. Quyền chi tiết của từng vai trò cần xác định theo luồng.
- Xác thực số điện thoại & mật khẩu băm Bcrypt, cấp mã JWT Token.
- Bảo vệ chống quét tài khoản (Enumeration Attack) & Axios Request/Response Interceptors.

---

### 2. 🏛️ Module 2: Phòng Luyện đề & Thi ảo THPTQG (CBT Engine)
- **Luyện đề thi thử chuẩn quốc gia:**
  - Đồng hồ đếm ngược (Countdown Timer) + Tự động nộp bài khi hết giờ.
  - Bảng điều hướng câu hỏi trực quan (Đã làm / Chưa làm / Đánh dấu xem lại).
  - Hỗ trợ công thức Toán/Lý/Hóa sắc nét với `KaTeX`.
  - Hỗ trợ 3 định dạng đề mới: Trắc nghiệm 4 đáp án, Đúng/Sai, Điền số ngắn.
- **Trộn đề ngẫu nhiên:** Đảo thứ tự câu hỏi và đảo thứ tự đáp án (A, B, C, D) cho từng học sinh.
- **Thống kê & Đánh giá chuyên sâu (Exam Analytics):**
  - **Leaderboard:** Bảng xếp hạng điểm số theo **Tuần / Tháng / Năm**.
  - **Phân tích lỗ hổng kiến thức:** Chỉ rõ phần kiến thức học sinh còn yếu cần cải thiện (Weakness Gap Analysis).
  - **Đánh giá độ khó:** Phân loại câu hỏi theo 4 mức độ (Nhận biết, Thông hiểu, Vận dụng, Vận dụng cao).
  - **Item Analysis:** Thống kê câu hỏi nào học sinh trong lớp/khối làm sai nhiều nhất để giáo viên chữa bài.

---

### 3. 🗺️ Module 3: Lộ trình Học tập & Tóm tắt Kiến thức (Roadmap & Weekly Summary)
- **Tổng hợp lộ trình theo tuần:** Lộ trình chi tiết từng tuần của khóa học (Tuần 1, Tuần 2, ...).
- **Tóm tắt kiến thức theo tuần:** Bản tóm tắt lý thuyết, mindmap, công thức cốt lõi sau mỗi tuần học.
- **Thảo luận dưới bài học / bài tập:** Học sinh có thể bình luận, hỏi đáp và trao đổi dưới từng bài tập hoặc từng tuần học.

---

### 4. 📅 Module 4: Lịch học, Điểm danh & Thông báo Lớp học
- **Thời khóa biểu theo khối:** Lịch học chi tiết chia theo từng khối (Khối 10, Khối 11, Khối 12).
- **Điểm danh buổi học:** Ghi nhận chuyên cần từng buổi (Có mặt, Đi muộn, Vắng mặt).
- **Hệ thống thông báo thời gian thực:** Bắn thông báo ngay lập tức khi giáo viên đổi lịch hoặc dời lịch học.
- **Lịch sử lớp học:** Xem lại nhật ký các buổi học đã diễn ra, nội dung đã dạy và tài liệu đính kèm.

---

### 5. 💬 Module 5: Kênh Chat & Cộng đồng Học tập
- **Kênh Chat theo Khối:** Phòng chat chung cho toàn bộ học sinh trong cùng khối (VD: Kênh Khối 12).
- Trao đổi học tập, chia sẻ tài liệu và hỏi bài trực tiếp với bạn bè & trợ giảng.

---

### 6. 🏆 Module 6: Bảng Thành tích & Vinh danh (Hall of Fame)
- **Bảng vàng thành tích các năm:** Tôn vinh các thủ khoa, á khoa, học sinh đạt điểm cao trong các kỳ thi THPTQG các năm trước.
- Tạo động lực và mục tiêu học tập cho học sinh khóa sau.

---

## Thứ tự triển khai đề xuất

| Mốc | Kết quả có thể demo | Việc cần có trước |
| --- | --- | --- |
| Nền tảng | Học sinh đăng nhập, đổi mật khẩu và mở Dashboard có thông tin hồ sơ. | Đã có API tài khoản và route Next.js. Rà các ca quyền truy cập và tài khoản bị khóa trước khi dùng thật. |
| **Weekly · đang làm** | Học sinh mở `/schedule`, xem lịch đúng khối và chuyển tuần bằng dữ liệu MySQL dev. | Hoàn thiện schema dev, nối lưới với API và kiểm tra theo [sprint Weekly](docs/planning/weekly-sprint.md). |
| Ca cá nhân và buổi tiếp theo | Học sinh thấy ca của mình, ca gốc đã chuyển và thẻ buổi tiếp theo. | Chốt cách tìm buổi tiếp theo và cách xử lý buổi bị dời hoặc hủy. |
| Đổi ca và cập nhật lịch | Học sinh đổi tạm hoặc đổi cố định theo quy tắc của trung tâm. Lịch đang mở cập nhật khi có thay đổi liên quan. | Chốt tuần dạy, quyền duyệt, quy tắc hủy và cách đồng bộ lại sau mất kết nối. |
| Điểm danh | Giáo viên mở buổi, thấy đúng danh sách dự kiến rồi ghi kết quả thực tế. | Có cách xác định ca sau đổi và phạm vi quyền giáo viên hoặc trợ giảng. |
| Nội dung học | Học sinh xem lộ trình, tóm tắt, bài tập và tài liệu của chương trình. | Chốt cách gắn tài liệu với chương trình và tuần dạy. |
| Thi online | Học sinh mở đề, lưu đáp án, nộp bài và nhận kết quả. Luồng lưu và nộp đã được thử khi tải dồn. | Chốt dữ liệu đề, lượt thi và cách xử lý mất mạng. |
| Phân tích, cộng đồng và vinh danh | Có thống kê thi, chat theo khối và bảng vinh danh theo phạm vi đã chọn. | Có kết quả thi và quy tắc công bố, quyền xem và quản trị nội dung. |

Khi chọn sprint mới, lấy một kết quả có thể demo từ bảng này. Ghi dữ liệu cần chuẩn bị, việc phụ thuộc và các ca nghiệm thu. Sau demo, cập nhật [hồ sơ dự án](PROJECT_CONTEXT.md) với kết quả đã kiểm tra và quyết định còn mở.
