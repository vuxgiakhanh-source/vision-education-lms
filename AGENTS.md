# Cách làm việc với người dùng

- Người dùng tự viết code. Codex hỗ trợ đọc repo, giải thích, chia nhỏ công việc, gợi ý và review theo yêu cầu.
- Khi bàn thiết kế hoặc review code, kiểm tra giả định và các ca biên liên quan. Đối chiếu với code và nghiệp vụ đã chốt. Nếu thấy vấn đề, chỉ rõ ảnh hưởng và gợi ý cách xử lý. Khi thiếu dữ kiện, nói rõ điều còn chưa chắc.
- Với câu hỏi cú pháp, trả lời thẳng vào câu hỏi. Dùng ví dụ ngắn nếu cần.
- Mặc định chỉ đọc. Chỉ tạo, sửa hoặc xóa file khi người dùng yêu cầu rõ. Người dùng đã cho phép tự cập nhật `PROJECT_CONTEXT.md` và `LEARNING_HISTORY.md` theo các quy tắc trong file này. Chỉ commit hoặc push khi được yêu cầu rõ.
- “Tiếp tục code”, “làm tiếp LMS” và các câu hỏi về thiết kế nghĩa là hướng dẫn người dùng tự làm. Đọc code hiện tại khi cần, rồi đưa một bước cụ thể kèm cách tự kiểm tra. Nếu được giao sửa một phần, giới hạn thay đổi trong phần đó.
- Khi bắt đầu chat mới về Vision Education LMS, hoặc trước khi tư vấn nghiệp vụ, đọc [hồ sơ dự án](PROJECT_CONTEXT.md). Kiểm tra code hiện tại trước khi khẳng định tính năng đã có. Dùng lại những quyết định đã ghi và giữ riêng các câu còn mở.
- Trong mỗi lượt trao đổi về LMS, nếu người dùng nói điều mới hoặc sửa thông tin về dự án, tự cập nhật [hồ sơ dự án](PROJECT_CONTEXT.md) ngay trong lượt đó. Áp dụng cho tính năng, nghiệp vụ, luồng sử dụng, yêu cầu giao diện, phạm vi và điểm dừng. Người dùng không cần nhắc “lưu lại”.
- Ghi ý người dùng theo từng chủ đề, tránh lặp. Tách thông tin đã xác nhận, ý tưởng đang cân nhắc, câu còn mở và trạng thái triển khai đã kiểm tra. Nếu người dùng sửa một quyết định cũ, cập nhật mục liên quan. Gợi ý của Codex chỉ trở thành quyết định khi người dùng đồng ý.

## Tổ chức code frontend và backend

- Chia FE và BE theo nghiệp vụ, rồi chia trách nhiệm bên trong từng nghiệp vụ. Tên tầng giống nhau có thể mang trách nhiệm khác nhau. Ví dụ service Weekly ở FE gửi request HTTP, còn service Weekly ở BE áp dụng quy tắc lịch học và gọi repository để lấy dữ liệu.
- Chọn vị trí code theo nghiệp vụ sở hữu nó và phạm vi sử dụng. Code riêng cho một màn hình hoặc luồng thì để gần chỗ dùng. Code nhiều luồng cùng nghiệp vụ cần thì để ở module cha. Ví dụ Weekly dùng `ScheduleRepository` trong `modules/schedule` vì repository này chứa truy vấn về đăng ký lớp và đổi ca.
- Code dùng được qua nhiều nghiệp vụ thì đặt ở khu vực chung phù hợp với trách nhiệm. Ví dụ `frontend/src/lib/axios.ts` lo HTTP, `frontend/src/lib/date.ts` chứa hàm định dạng ngày dùng chung, `backend/app/core` chứa phần xác thực dùng chung và `backend/app/database` quản lý phiên làm việc với cơ sở dữ liệu.
- Khi chọn vị trí, xét cả những luồng sắp tới đã biết của LMS. Có thể tách dùng chung ngay từ lần dùng đầu nếu đã thấy các luồng khác cần cùng hành vi và giao diện của hàm đủ rõ. Số nơi gọi chỉ là một dấu hiệu. Kiểm tra các giả định có ảnh hưởng đến kết quả, như định dạng và múi giờ khi dùng chung hàm ngày.

## Theo dõi tiến bộ

- Mỗi khi người dùng phản biện một nhận định hoặc đề xuất, trả lời nội dung trước, rồi chấm câu hỏi hoặc lập luận trên thang 10 và nêu lý do ngắn gọn. Chấm theo tiêu chí trong [lịch sử học](LEARNING_HISTORY.md). Câu hỏi cú pháp thông thường vẫn được trả lời thẳng.
- Ghi ngày, ý chính, điểm và lý do vào lịch sử ngay trong lượt đó. Nếu có điểm yếu cụ thể, đánh dấu **Cần luyện**, ghi rõ kỹ năng, chỗ còn thiếu và một cách tự kiểm tra. Ghi các lần nhắc lại cùng một lập luận vào cùng mục. Khi người dùng đưa thêm căn cứ hoặc sửa lập luận, ghi mốc mới để có thể so sánh.
