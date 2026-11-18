# Lịch sử phản biện khi học và code LMS

Điểm đánh giá chất lượng câu hỏi hoặc lập luận tại thời điểm trao đổi. Dựa vào việc câu hỏi có chạm đúng vấn đề, có căn cứ từ code hoặc nghiệp vụ, và có nêu điều kiện hoặc ca biên làm thay đổi kết luận hay không.

- **9–10** · Nêu đúng vấn đề, có căn cứ rõ và xử lý được điều kiện hoặc ca biên quan trọng.
- **7–8** · Có hướng lập luận tốt, còn thiếu một điều kiện hoặc bước kiểm tra.
- **5–6** · Nêu được vấn đề, nhưng căn cứ còn yếu hoặc kết luận đi xa hơn dữ kiện.
- **1–4** · Nhầm vấn đề chính hoặc dựa vào giả định sai làm đổi kết luận.

## 19/11/2026 · Nguyên nhân Output State nhận giá trị ban đầu là null

- **Phản biện giả định · 8/10.** Người dùng đặt giả định: output (`weeklySchedule`) ban đầu là `null` vì *"chưa có date nên chưa biết lấy mốc nào"*. Nhận xét rất nhạy bén khi nhìn ra sự bất đối xứng giữa hai state lúc khởi tạo. Tuy nhiên, giả định "chưa có date" bị lệch với code thực tế vì `selectedDate` đã có sẵn ngày hôm nay nhờ `new Date()`. Nguyên nhân thực sự của `null` không phải thiếu tham số, mà do độ trễ mạng bất đồng bộ (Network Latency): lúc React vẽ frame đầu tiên, request mới bắt đầu gửi đi và dữ liệu chưa kịp bay về.

## 19/11/2026 · Phân loại State thành Input và Output trong Data Fetching

- **Phản biện khái niệm · 9/10.** Người dùng chất vấn căn cứ phân loại: *"sao biết đây là input output cu"*. Câu hỏi truy tận gốc bản chất thay vì chấp nhận thụ động thuật ngữ. Căn cứ phân biệt nằm ở luồng dữ liệu của hàm và API: một biến đóng vai trò tham số đầu vào (`selectedDate` truyền vào hàm và biến thành Query Param `?week_start=...` gửi lên backend), còn một biến là kết quả phản hồi đầu ra (`data` nhận về từ response body để lưu vào state và đưa lên view).

## 19/11/2026 · Xử lý lỗi tải lịch ở frontend

- **Phản biện · 8/10.** Người dùng đặt câu hỏi vì sao Weekly chỉ có `catch (error)` trong khi backend có exception riêng. Câu hỏi chỉ ra khoảng cách giữa log thử request và cách xử lý lỗi cho người dùng. Cần phân biệt lỗi HTTP đã có ở Axios, biến nhận lỗi trong `catch` và trạng thái lỗi hiển thị trên Weekly.

## 19/11/2026 · Giá trị khởi tạo của State ngày xem lịch (Initial State & Domain Reality)

- **Phản biện thiết kế State · 9/10.** Người dùng chất vấn việc gán giá trị mặc định là chuỗi rỗng `useState('')`: *"ừm hiểu ý nma sao để useState(''"*. Lập luận rất sắc bén: chuỗi rỗng không đại diện cho bất kỳ ngày hợp lệ nào, vừa gây lỗi 422 khi gửi sang FastAPI vừa làm trống rỗng giao diện lúc khởi tạo. Giá trị khởi tạo của state phải phản ánh đúng nghiệp vụ: mở web lên là phải xem lịch tuần hiện tại (ngày hôm nay).

## 19/11/2026 · Phạm vi dùng lại của hàm định dạng ngày

- **Phản biện · 8/10.** Người dùng đặt lại phạm vi của `formatLocalDate` sau khi được hướng dẫn đặt hàm trong `WeeklyGrid.tsx`. Câu hỏi nhận ra hàm nhận `Date` và có thể dùng ở nhiều nơi. Cần đối chiếu thêm nơi gọi có dùng cùng múi giờ và cùng định dạng ngày hay không trước khi tách dùng chung.
- **Phản biện tiếp ngày 19/11/2026 · 8/10.** Người dùng yêu cầu xét các luồng sắp tới khi đặt hàm. Lịch tuần, đổi ca và điểm danh đều có thao tác theo ngày. Cần giữ phạm vi dùng chung ở việc chuyển ngày theo giờ địa phương sang `YYYY-MM-DD` và kiểm tra từng nơi gọi cần ngày, giờ hay thời điểm đầy đủ.
- **Phản biện tiếp ngày 19/11/2026 · 9/10.** Người dùng chỉ ra backend còn dùng lại mã ở ngoài `core` và `database`. Đối chiếu thấy Weekly dùng `ScheduleRepository` ở module cha và nhiều luồng Auth nhập `User` từ `app/models`. Ranh giới đặt mã phụ thuộc vào nghiệp vụ sở hữu mã và phạm vi sử dụng.

## 19/11/2026 · Gọi method trên object và trên class

- **Phản biện · 8/10.** Người dùng đối chiếu lời gọi `weeklyScheduleService.getWeeklySchedule(...)` với quy tắc gọi instance method của Java. Quy tắc tạo instance đúng với instance method. Còn thiếu trường hợp method `static` và việc nhận ra `weeklyScheduleService` đã là object được tạo bằng `{ ... }`. **Cần luyện.** Tự chỉ ra đối tượng bên trái dấu chấm trong `hello.run()`, `Hello.run()` với method `static`, và `weeklyScheduleService.getWeeklySchedule(...)`.

## 19/11/2026 · File route và component màn hình

- **Phản biện · 7/10.** Người dùng đối chiếu Schedule với các màn hình khác để hỏi vì sao cần `page.tsx`. Hướng đối chiếu đúng, còn thiếu bước tìm trong `src/app`. **Cần luyện.** Mở file route của Dashboard và lần theo import đến component màn hình trong `src/features`.
- **Phản biện tiếp ngày 19/11/2026 · 9/10.** Người dùng chỉ ra route Schedule là file Codex thêm, làm rõ khác biệt giữa cây frontend trước và sau khi chuyển framework. `git status` xác nhận route đang là file chưa được Git theo dõi.

## 19/11/2026 · Kiểu ngày trong phản hồi Weekly

- **Phản biện · 7/10.** Người dùng hỏi vì sao trường ngày `week_start` được khai báo `string` ở frontend. Câu hỏi chỉ đúng trường cần đối chiếu và còn thiếu bước xem giá trị qua JSON. **Cần luyện.** Phân biệt kiểu `date` trong schema Python với chuỗi ngày trong phản hồi JSON. Tự kiểm tra bằng cách đọc dấu ngoặc kép quanh giá trị `week_start` trong phản hồi API.

## 18/11/2026 · Ngữ nghĩa của section và div

- **Phản biện · 8/10.** Người dùng nhận ra đổi `section` thành `div` trong khung Weekly có thể cho cùng giao diện. Kết luận còn thiếu điều kiện về ngữ nghĩa truy cập. **Cần luyện.** Phân biệt giao diện nhìn thấy với các vùng mà trình đọc màn hình nhận ra. So sánh hai thẻ khi dùng chung CSS, rồi thử gắn tên cho `section` và kiểm tra vai trò trong cây Accessibility.

## 18/11/2026 · Chọn công nghệ frontend theo phạm vi LMS

- **Phản biện · 9/10.** Người dùng chỉ ra đề xuất dùng Next.js cho website giới thiệu dựa vào một sản phẩm họ chưa định làm. Việc xác nhận phạm vi làm rõ rằng quyết định công nghệ phải được đánh giá trên các nhu cầu của chính LMS.

## 18/11/2026 · Phân biệt venv và Docker

- **Phản biện · 7/10.** Người dùng nhận ra cả hai đều có thể cô lập thư viện Python của ứng dụng. Còn gộp việc cô lập thư viện với đóng gói để chuyển môi trường chạy giữa các máy. **Cần luyện.** Phân biệt thư mục venv tạo từ Python có sẵn, Docker image và container chạy từ image. Tự kiểm tra bằng cách giải thích sẽ mang artifact nào và cần cài gì khi đưa FastAPI từ Windows lên VPS Linux.
- **Phản biện tiếp ngày 18/11/2026 · 8/10.** Người dùng đề xuất đưa FastAPI và Alembic vào Docker để bỏ nhu cầu dùng venv trên Windows. Phương án khả thi vì cả hai dùng chung runtime Python. Còn cần xét khác biệt giữa quy trình phát triển và triển khai, cùng địa chỉ MySQL khi backend chuyển qua mạng Compose.

## 18/11/2026 · Nhận thức quy trình Thiết kế mô hình trước khi viết mã (Design-First Mindset)

- **Nhận định quy trình kỹ nghệ · 9/10.** Người dùng chỉ ra chuẩn mực phát triển phần mềm: "thường thì người ta vẽ trước rồi mới code DB".
- **Lý do & Giá trị kỹ thuật**:
  1. *Quy tắc chi phí thay đổi (Cost of Change Curve)*: Sửa sai trên bản vẽ ERD chỉ tốn vài phút thảo luận; nhưng sửa sai cấu trúc DB khi code đã triển khai ra production phải đối mặt với rủi ro mất dữ liệu, viết script migration phức tạp và downtime.
  2. *Design-First vs. Code-First*: Trong các buổi phỏng vấn System Design tại Big Tech, 100% ứng viên phải phác thảo ERD trên bảng trắng (Whiteboard) để bảo vệ quyết định chuẩn hóa dữ liệu trước khi viết API hay câu truy vấn.
- [x] **Kỹ năng đã làm chủ — Tư duy kiến trúc Design-First (Thiết kế dữ liệu trước khi triển khai).**

## 18/11/2026 · Nhận diện luồng đọc và đổi lịch tuần từ mô hình ERD (Data-Model-Driven Thinking)

- **Nhận định & Liên hệ kiến trúc · 9/10.** Người dùng nhận ra rằng khi nhìn kỹ vào sơ đồ ERD (mối quan hệ giữa `students`, `class_enrollments`, `class_sessions` và `sessions_transfers`), ta có thể suy ra trọn vẹn luồng logic hiển thị lịch tuần sau khi đổi ca mà không bị dính bug.
- **Lý do & Giá trị kỹ thuật**:
  1. *Chuyển dịch tư duy (Mental Model Shift)*: Người dùng không còn nhìn tính năng như một chuỗi thao tác giao diện rời rạc, mà nhìn dưới góc độ quan hệ dữ liệu: Lịch tuần = (Lịch cố định từ `class_enrollments` $\setminus$ Ca đã đổi đi ở `original_session_id`) $\cup$ Ca học bù ở `replacement_sessions_id`.
  2. *Triệt tiêu bug logic*: Việc định danh buổi bằng ID cụ thể và tách biệt lần đổi ca giúp xử lý được các ca biên phức tạp: đổi ca xuyên tuần (cross-week), chuyển lớp cố định giữa tuần (`starts_at`/`ends_at`), và hủy ca tạm thời mà không làm xáo trộn lịch của các học sinh khác trong lớp.
- [ ] **Cần luyện — Truy vết ca biên Buổi học bị hủy (Cancelled Session Edge Case).** Giả sử học sinh A đổi sang học bù vào buổi B, nhưng sau đó buổi B bị giáo viên hủy (`status = 'cancelled'`). Tự truy vết luồng trong service để xác định hệ thống nên báo trạng thái gì cho học sinh A trên lưới lịch tuần.

## 18/11/2026 · Bác bỏ việc ép co dãn chiều cao toàn màn hình (Vertical Over-stretching Antipattern)

- **Phản biện trực quan UI/UX · 9.5/10.** Người dùng lập tức tuýt còi và yêu cầu dừng ngay ("thôi, dừng sửa lại xấu thế ?") khi thấy giải pháp ép dãn lưới lịch theo toàn bộ chiều cao màn hình 24 inch (`h-full`, `1fr`).
- **Lý do & Giá trị kỹ thuật**:
  1. *Lỗi tư duy Responsive máy móc*: Một bảng lịch chỉ có 3 ca học (Sáng, Chiều, Tối). Nếu dùng `1fr` để ép nó dãn kín đáy màn hình 24 inch (cao 1080px hoặc 1440px), mỗi hàng sẽ bị kéo dãn tới hơn 260px–280px trong khi nội dung chỉ có 2 dòng chữ ("Hàm số bậc hai"). Hệ quả là 70% diện tích ô thành khoảng trắng rỗng tuếch, tỷ lệ ô bị biến dạng thành những "ống thang máy" dọc lêu nghêu cực kỳ mất thẩm mỹ.
  2. *Quy tắc vàng của Dashboard / Calendar UI*: Bảng dữ liệu dạng ma trận (grid matrix) cần giữ tỷ lệ khung hình cân đối (aspect ratio gần vuông hoặc hơi chữ nhật ngang nhẹ, chiều cao hàng 135px–145px). Khoảng trống bên dưới trên màn hình lớn là chuyện hoàn toàn bình thường trong thiết kế SaaS chuyên nghiệp (như Linear, Google Calendar) hoặc giải quyết bằng nội dung bổ trợ (thẻ ghi chú quy định đổi ca, thống kê), tuyệt đối không được ép dãn cơ học làm méo ô.
- [x] **Kỹ năng đã làm chủ — Giữ vững tỷ lệ thị giác (Visual Proportion) trước bẫy co dãn máy móc.**

## 18/11/2026 · Đồng bộ cấu trúc Frontend Feature theo Backend (Frontend-Backend Symmetry)

- **Đề xuất kiến trúc Frontend · 9.5/10.** Người dùng đề xuất phân chia thư mục Frontend `frontend/src/features/schedule/` tương ứng 1-1 với Backend và đồng bộ cấu trúc với `features/auth/`: tách thành 3 sub-feature `weekly/`, `temporary_transfers/`, `permanent_transfers/`.
- **Lý do & Giá trị kỹ thuật**:
  1. *Tính đối xứng kiến trúc (Architectural Symmetry)*: Giúp luồng code từ Backend sang Frontend có cùng một bản đồ tư duy. Khi cần sửa tính năng đổi ca tạm, lập trình viên biết ngay ở Backend là `modules/schedule/temporary_transfers` và ở Frontend là `features/schedule/temporary_transfers`.
  2. *Tránh Antipattern "Túi rác khổng lồ" (Junk Drawer)*: Thay vì nhét toàn bộ components của lưới tuần, modal đổi ca tạm và form xin chuyển lớp cố định vào chung một thư mục `components/` mười mấy file lộn xộn, mỗi sub-feature sẽ tự quản lý `components/`, `services/`, `types/` của riêng mình.
  3. *Trang chính `SchedulePage.tsx` đóng vai trò Container/Orchestrator*: Chỉ làm nhiệm vụ ghép nối Lưới tuần (`weekly`) với Nút/Modal đổi ca (`temporary_transfers`), giữ component trang chính ngắn gọn, dễ bảo trì.
- [x] **Kỹ năng đã làm chủ — Tư duy đồng bộ kiến trúc toàn hệ thống (Full-stack Architectural Symmetry).**
- **Phản biện tiếp ngày 18/11/2026 · 7/10.** Người dùng nhận thấy frontend vẫn thiếu nhất quán sau khi sắp xếp lại. Nhận định đúng ở ranh giới trách nhiệm vì bản C trong Weekly vẫn chứa giao diện đổi lịch mẫu. Còn thiếu ví dụ cụ thể trong lập luận. **Cần luyện.** Tách việc đối chiếu tên thư mục khỏi kiểm tra trách nhiệm trong code. Thử chỉ ra phần nào của `ScheduleOptionC.tsx` sẽ phải sửa nếu chỉ thay đổi cách đổi ca tạm.
- **Làm rõ ngày 18/11/2026 · 8/10.** Người dùng xác định yêu cầu nhất quán là mỗi chức năng frontend có năm tầng. Điều này làm rõ tiêu chí kiểm tra bên trong từng nhánh. Ca biên cần chốt là chức năng không có route riêng hoặc dữ liệu cần kiểm tra lúc chạy, như `auth/me` hiện chỉ có `services/` và `types/`.
- **Phản biện tiếp ngày 18/11/2026 · 7/10.** Người dùng chỉ rõ phạm vi so sánh là Auth, Dashboard và Schedule. Có chỗ lệch kiểm tra được ở độ sâu của `pages/`. **Cần luyện.** Dùng các import page từ `App.tsx` để chỉ ra điểm lệch, rồi kiểm tra quy tắc đề xuất trên feature có nhiều route và feature có một route.
- **Phản biện tiếp ngày 18/11/2026 · 9/10.** Người dùng chỉ ra từ ảnh bản 5179 rằng tiêu đề **Lịch học** nằm trong cùng khung trắng với điều hướng tuần và bảng lịch. Căn cứ trực quan khớp với cấu trúc HTML: ba phần cùng ở trong một `section`. Việc gom chúng vào khung Weekly giúp hướng dẫn dựng JSX sát bố cục người dùng chọn.
- **Phản biện tiếp ngày 18/11/2026 · 9/10.** Người dùng đưa ảnh chỉ rõ nút chuyển tuần chỉ hiện mũi tên trái và phải. Bản TSX tham chiếu dùng icon có tên truy cập riêng trên nút. Tự kiểm tra bằng cách xem nút chỉ hiện biểu tượng và vẫn được nhận diện là **Tuần trước** hoặc **Tuần sau** trong cây Accessibility.

## 18/11/2026 · Trách nhiệm của service đọc lịch tuần

- **Phản biện tiếp ngày 18/11/2026 · 8/10.** Người dùng yêu cầu nhãn khoảng ngày dùng dữ liệu thật thay cho chuỗi mẫu. Nhận định bắt được nguy cơ lưới và nhãn lệch nhau khi chuyển tuần. Cần chỉ ra trường làm căn cứ là `week_start` trong response, rồi tự thử một tuần bắc qua hai tháng.

- **Phản biện tiếp ngày 18/11/2026 · 9/10.** Người dùng đề xuất cho lịch mini gửi ngày thứ Tư hoặc thứ Năm để mở tuần chứa ngày đó. Chuyển phép tính về thứ Hai sang service giúp router gọi service trực tiếp và tránh trả `422` cho một ngày hợp lệ giữa tuần. Kiểm tra thêm Chủ nhật và thứ Hai kế tiếp để xác nhận hai mốc thuộc hai tuần khác nhau.
- **Phản biện · 8/10.** Người dùng chất vấn độ gọn của service mới và hỏi hàm đọc lịch tuần phục vụ mục đích gì. Câu hỏi làm rõ trách nhiệm của service và gợi rà lại tên hàm cũng như việc nó đang phụ thuộc vào hai repository.
- **Phản biện tiếp · 7/10.** Người dùng nêu nguy cơ gắn nhãn **Ca của bạn** lên buổi bị hủy và đề xuất kiểm tra trạng thái trong service. Truy vấn lịch đã loại buổi hủy trước vòng lặp. **Cần luyện.** Truy luồng dữ liệu từ repository tới service. Tự kiểm tra một buổi thường lệ bị hủy và so với ca gốc vẫn mở nhưng buổi thay thế bị hủy.
- **Phản biện tiếp · 8/10.** Người dùng chỉ ra ca 14:00–17:00 sẽ không được xếp khi đăng ký lớp đích có hiệu lực lúc 15:00. Phép so đúng và làm lộ quyết định nghiệp vụ còn thiếu về việc có cho chuyển vào buổi đang diễn ra hay không. **Cần luyện.** Tách giờ duyệt, giờ hiệu lực và quyền tham gia buổi cụ thể. Thử hai lớp cùng bắt đầu lúc 14:00 để thấy điều gì xảy ra nếu chỉ xét đăng ký giao với thời lượng buổi.
- **Phản biện tiếp · 9/10.** Người dùng đối chiếu router lịch với các router sẵn có, chỉ ra handler trong repo trả trực tiếp kết quả service. Căn cứ kiểm tra được ở `/me` và `/login`. Đã đưa việc dựng response vào service và để handler lịch trả thẳng kết quả sau khi kiểm tra đầu vào.

## 17/11/2026 · Khôi phục cấu trúc Package by Feature sạch và bắt đầu lại

- **Quyết định kiến trúc · 9/10.** Người dùng chủ động loại bỏ toàn bộ code AI sinh ra trước đó bị cồng kềnh, đưa codebase về commit gốc sạch sẽ trên GitHub, nhưng giữ lại cấu trúc thư mục Package by Feature (`weekly/`, `temporary_transfers/`, `permanent_transfers/`) ở dạng rỗng hoàn toàn để tự tay code từng dòng một cách sạch sẽ, không bị phụ thuộc vào code AI.

## 14/11/2026 · Dùng dữ liệu lưới tuần để lấy buổi sắp tới

- **Nhận định** · Lưới tuần đã lấy danh sách buổi học, nên có thể dùng lại dữ liệu đó và bỏ hàm lấy 5 buổi riêng.
- **Điểm 8/10** · Bạn chỉ ra hai truy vấn có thể lấy dữ liệu trùng nhau và đề xuất dùng lại kết quả sẵn có. Lập luận đúng nếu thẻ chỉ tìm trong tuần đang xem.
- [x] **Cần luyện — Kiểm tra phạm vi dữ liệu.** Thử tình huống hôm nay là Chủ nhật và buổi tiếp theo của học sinh nằm vào thứ Ba tuần sau. Xác định thẻ có cần hiện buổi đó trước khi kết luận dữ liệu của một tuần là đủ.
- **Phản biện ngày 15/11/2026 · 6/10.** Người dùng nghi việc duyệt từng buổi để đánh dấu ca riêng chưa tối ưu. Câu hỏi chạm vào chi phí xử lý, nhưng chưa phân biệt phép so trong bộ nhớ với truy vấn lặp. **Cần luyện:** đếm số câu SQL khi tuần có 4 và 40 buổi, rồi so với số lượt duyệt danh sách.
- **Bổ sung ngày 15/11/2026 · 8/10.** Người dùng nhận ra khoảng ngày của lưới có thể chứa hai buổi của một học sinh khi lịch các ca thay đổi. Lập luận phát hiện giả định về số lượng của kết quả. **Cần luyện.** Tự rà ca một buổi từ tuần trước được dời sang tuần này và ca đổi tạm một buổi sang ca cùng bài để xác định những ô nào cần đánh dấu.
- **Phản biện tiếp ngày 15/11/2026 · 8/10.** Người dùng hỏi query đăng ký có thể dẫn tới hai buổi trong tuần khi ghép lịch lớp hay không. Có thể khi các buổi ở hai lớp đều khớp thời điểm hiệu lực, chẳng hạn chuyển lớp vào thứ Năm, nhưng kết quả còn tùy số đăng ký và buổi thực tế. **Cần luyện.** So hai trường hợp A thứ Ba và B thứ Sáu cùng dạy tuần 5, hoặc lần lượt dạy tuần 5 và 6, rồi xác định quy tắc với từng trường hợp.
- **Phản biện tiếp ngày 15/11/2026 · 9/10.** Người dùng chỉ ra hệ quả trên lưới: nếu hai buổi cùng tuần dạy đều được tô màu **Ca của bạn**, giao diện sẽ báo thừa một buổi phải đi học. Backend cần xác định đúng buổi được xếp trước khi frontend tô màu.
- **Phản biện ngày 15/11/2026 · 8/10.** Người dùng hỏi vì sao chỉ lấy ID thay vì bản ghi ORM như repository hiện tại. Câu hỏi làm rõ dữ liệu mà bước sau cần. **Cần luyện.** Thử đánh dấu ca từ lưới đã tải bằng ID buổi, rồi thử xác định ca từ ID của bản ghi đăng ký và xem trường nào còn thiếu.
- **Phản biện tiếp ngày 15/11/2026 · 9/10.** Người dùng chỉ ra trợ lý đổi từ truy vấn ID buổi sang truy vấn đăng ký lớp mà chưa đưa bằng chứng phương án sau nhanh hơn. Cả hai bản đơn giản đều có ba lượt truy vấn gồm tra khối và lấy lưới. Muốn so hiệu năng thì đo trên cùng dữ liệu và xem kế hoạch truy vấn.

## 15/11/2026 · Lọc đăng ký lớp giao với tuần

- **Phản biện · 4/10.** Người dùng lập luận rằng không có ca quanh 00:00 nên lọc theo mốc kết thúc đăng ký trong tuần là đủ. Điều kiện về giờ ca không xử lý được đăng ký còn hiệu lực nhưng hết hạn sau tuần đó hoặc có `ends_at = NULL`.
- [ ] **Cần luyện.** Tách thời gian hiệu lực của `ClassEnrollment` khỏi giờ của `ClassSession`. Thử một lớp có buổi thứ Tư 18:00 và đăng ký kéo dài tới cuối tháng. Buổi vẫn là ca của học sinh trong tuần dù ngày kết thúc đăng ký nằm ngoài tuần.
- **Phản biện tiếp ngày 15/11/2026 · 4/10.** Người dùng hỏi liệu bộ lọc cũ đúng khi tuần tính thứ Hai đến Chủ nhật. Mốc tuần đã rõ, nhưng chưa xử lý trường hợp đăng ký bao trùm cả tuần hoặc mở vô thời hạn.
- **Đổi đề xuất nghiệp vụ ngày 15/11/2026 · 8/10.** Người dùng giới hạn thao tác tự đăng ký vào một buổi học tiếp theo cụ thể vì chọn khoảng thời gian gây phiền và dễ giữ hai ca. Đề xuất làm rõ thao tác của học sinh. **Cần luyện.** Giả lập hai yêu cầu chọn hai ca thay thế cho cùng buổi gốc và kiểm tra danh sách tham dự cuối cùng chỉ ghi nhận một ca.
- **Phản biện ngày 15/11/2026 · 8/10.** Người dùng chỉ ra rằng nếu ca tạm có bản ghi đăng ký riêng thì `ends_at` có thể lấy giờ kết thúc của buổi thay thế. Mốc này giới hạn bản ghi tạm trong một buổi. **Cần luyện.** Thử ca cố định thứ Ba được đổi sang thứ Năm và kiểm tra hệ thống xác định được buổi thứ Ba đã chuyển khi bản ghi tạm chỉ có hiệu lực vào thứ Năm.
- **Bổ sung ngày 15/11/2026 · 6/10.** Người dùng đề xuất ưu tiên lịch gốc khi chưa có lựa chọn thay thế và dùng ID lớp cùng `ends_at` để phát hiện ca tạm. Hướng ưu tiên lịch gốc hợp lý, nhưng tín hiệu được đề xuất cũng xuất hiện khi đổi lớp cố định. **Cần luyện.** So hai trường hợp cùng có lớp A kết thúc và lớp B có hiệu lực trong tuần, rồi xác định dữ liệu nào cho biết một buổi cụ thể đã được thay thế.
- **Phản biện ngày 15/11/2026 · 8/10.** Người dùng nhắc rằng đã có `class_enrollments` khi trợ lý đề xuất một bảng mới cho lần đổi ca. Có thể dùng lại bảng thông qua dòng tạm riêng nếu lưu được quan hệ giữa buổi gốc và buổi thay thế. Các trường hiện tại chỉ xác định lớp và thời gian hiệu lực.
- **Đề xuất tiếp ngày 15/11/2026 · 7/10.** Người dùng tận dụng `class_id` cho lớp tạm và đề xuất quay lại lớp cũ khi ca mới kết thúc. Việc tránh lưu hai ID lớp là hợp lý. **Cần luyện.** Thử đổi ca thứ Bảy sang thứ Năm, rồi xác định hệ thống dựa vào đâu để buổi thứ Bảy vẫn mang trạng thái đã chuyển sau khi học sinh học xong thứ Năm.
- **Phản biện ngày 15/11/2026 · 9/10.** Người dùng chỉ ra luồng đổi ca tạm đã chốt từ đầu nhưng bị bỏ sót khi trợ lý đánh giá schema ban đầu. Căn cứ là quy tắc điểm danh cần xác định buổi gốc và buổi thay thế của cùng học sinh.
- **Phản biện ngày 15/11/2026 · 8/10.** Người dùng hỏi liệu một lớp mặc định cùng `SessionTransfer` có thể thay `ClassEnrollment`. Phương án đủ nếu chỉ cần lớp hiện tại và các lần đổi tạm. Cần kiểm tra thêm ca chuyển lớp cố định rồi mở lại lịch tuần trước để xác định nhu cầu lưu lịch sử theo thời điểm.
- **Phản biện ngày 15/11/2026 · 8/10.** Người dùng đặt lại câu hỏi từ nhu cầu điểm danh: nếu mục tiêu là biết học sinh được xếp vào buổi nào, có thể gộp lần đổi với bản ghi tham dự. Cách này khả thi khi lưu danh sách dự kiến từng buổi. **Cần luyện.** Từ một dòng gộp, tự chỉ ra cách tra buổi học sinh cần đến và cách hiện **Đã chuyển ca** ở buổi gốc.
- **Phản biện ngày 15/11/2026 · 8/10.** Người dùng đề xuất để repository trả các buổi học sinh được xếp trực tiếp, vì service cần buổi để dựng lịch. Hướng này phù hợp với đầu ra cần dùng. **Cần luyện.** Khi nối theo lớp, lấy giờ bắt đầu của từng buổi để xét hiệu lực đăng ký. Thử một buổi lớp cũ sau thời điểm chuyển lớp để kiểm tra nó bị loại.
- **Phản biện tiếp ngày 15/11/2026 · 9/10.** Người dùng chỉ ra dữ liệu xếp lớp chỉ xác định ca thường lệ. Muốn đọc lịch học sinh sau khi đổi ca còn phải truy vấn `SessionsTransfer` để nhận diện buổi gốc và buổi thay thế.
- **Chốt lại yêu cầu ngày 15/11/2026 · 9/10.** Người dùng xác định đầu ra của hàm repo là lịch cá nhân trong khoảng, gồm các buổi đã qua và sắp tới, dù theo lớp hay đổi tạm. Điều này làm rõ hàm cần trả buổi học sau khi áp dụng lần đổi. Có thể kiểm tra bằng ca `101 → 108`: lịch cá nhân chứa `108`, còn dữ liệu lần đổi giúp nhận diện `101` đã chuyển.
- **Phản biện ngày 15/11/2026 · 7/10.** Người dùng nhắc cần xét `week` và dùng cụm “khác week”. Tuần dạy là điều kiện của ca thay thế; cần phân biệt ID buổi, tuần dạy trong chương trình và khoảng tuần của lưới lịch. Tự rà hai buổi khác ID nhưng đều dạy nội dung tuần 5.
- **Phản biện ngày 18/11/2026 · 9/10.** Người dùng chỉ ra service lịch tuần cần xét đổi lớp cố định có hiệu lực giữa hai tuần và đổi một buổi sang tuần lịch sau. Hai ca buộc xác định riêng lớp có hiệu lực, liên kết buổi gốc với buổi đích và trạng thái hiển thị ở từng tuần. Tự kiểm tra hai tuần liên tiếp từ cùng một lần đổi, rồi thử tuần đích có thêm buổi thường lệ thuộc tuần dạy khác.
- **Phản biện tiếp ngày 18/11/2026 · 9/10.** Người dùng chỉ ra nhãn số tuần dạy chung trên lưới dễ gây hiểu nhầm vì các lớp có thể dạy tới các tuần khác nhau trong cùng khoảng ngày. Quy tắc chọn khoảng lịch theo `week_start` dùng được cho cả khối, còn số tuần dạy gắn với từng buổi. Tự kiểm tra bằng cách đặt hai buổi thuộc hai tuần dạy vào cùng một lưới.
- **Phản biện ngày 15/11/2026 · 9/10.** Người dùng yêu cầu chứng minh thiết kế đổi ca đáp ứng nghiệp vụ và làm rõ cơ sở gọi một phương án là tối ưu. Khóa chính ghép và khóa ngoại đã thử trên SQLite trong bộ nhớ. Còn cần kiểm thử luồng đầy đủ sau khi viết service, và cần số đo để so hiệu năng với phương án khác.
- **Phản biện ngày 15/11/2026 · 8/10.** Người dùng hỏi vì sao phải đánh dấu hai cột làm khóa chính trong `SessionTransfer`. Luật nghiệp vụ cần cặp `(student_id, original_session_id)` duy nhất. Có thể dùng khóa chính ghép hoặc khóa chính `id` kèm ràng buộc `UNIQUE` trên cặp. Tự rà bằng hai học sinh cùng đổi một buổi và một học sinh đổi hai buổi khác nhau.
- **Phản biện ngày 15/11/2026 · 8/10.** Người dùng chỉ ra `replacement_session_id` có thể nhận `NULL`. Về schema, cột khóa ngoại ngoài khóa chính có thể khai báo `nullable=True`. SQLite đã chấp nhận dòng có `NULL` khi bật kiểm tra khóa ngoại. Cần định nghĩa ý nghĩa của dòng này khi dựng lịch và điểm danh.
- **Phản biện ngày 15/11/2026 · 6/10.** Người dùng nghi `id` và `class_id` lưu trùng thông tin. Trong `ClassSession`, `id` định danh buổi và `class_id` chỉ lớp tổ chức. **Cần luyện.** Vẽ hai buổi của cùng lớp, thử tìm cả hai buổi bằng `class_id` và chọn đúng một buổi bằng `id`.

## 15/11/2026 · Phản biện ca biên dữ liệu nhạy cảm (Password Hash) khi query ORM

- **Phản biện / Bắt bẻ ca biên · 9/10.** Người dùng chất vấn sắc bén: nếu bảng có trường nhạy cảm như password, liệu việc query toàn bộ model Entity có an toàn không. Lập luận chạm trúng bài toán bảo mật dữ liệu nhạy cảm kinh điển trong thiết kế Backend và ORM.
- **Giả định nhầm lẫn tiếp theo · 3/10.** Người dùng cho rằng framework "tự nhìn thấy tên `hashed_password` rồi tự động giấu đi". Đây là giả định sai về cơ chế tự động (Framework Magic) rất nguy hiểm trong bảo mật backend.
  - **Lý do**: Framework không tự đọc tên biến để đoán ý đồ lập trình viên. Nếu không tự tay viết lệnh `defer(User.hashed_password)` thì SQLAlchemy vẫn `SELECT` nguyên cột mật khẩu lên RAM; và nếu trong Pydantic Schema vô tình khai báo cột đó thì toàn bộ hash mật khẩu sẽ bị phơi bày ra JSON cho Client xem. Mọi cơ chế bảo mật đều phải do kỹ sư chủ động kiểm soát.
- [ ] **Cần luyện — Kỹ năng phòng thủ theo chiều sâu (Defense in Depth) cho dữ liệu nhạy cảm.**
  - **Điểm mấu chốt**: Không bao giờ để rò rỉ password ra ngoài. Có 2 tuyến phòng thủ:
    1. *Tuyến DB (Query level)*: Dùng `defer(User.hashed_password)` trong SQLAlchemy để loại bỏ cột password ngay từ câu `SELECT` khi không cần xác thực.
    2. *Tuyến API (Serialization level - Quan trọng nhất)*: Dùng Pydantic Response Schema chỉ whitelist các trường an toàn (`id`, `email`, `full_name`). Cho dù RAM backend có giữ hash password thì API cũng không bao giờ serialize trả về cho Client.
  - **Cách tự kiểm tra**: Viết một endpoint `GET /me` hoặc `GET /users`, kiểm tra response JSON trả về xem có bất kỳ trường nào chứa `hash`, `password` hay `secret` không.

## 15/11/2026 · Khóa ngoại và giới hạn số lượng trả hàng

- **Trả lời phỏng vấn · 4/10.** Người dùng cho rằng khóa ngoại sẽ chặn hai lượt trả hàng làm tổng vượt số lượng đã giao. Hai lượt đều tham chiếu một dòng giao có thật, nên khóa ngoại chấp nhận cả hai. Thử trên SQLite với khóa ngoại bật cho kết quả giao 6 và trả 8.
- [ ] **Cần luyện.** Phân biệt ràng buộc tham chiếu với quy tắc về tổng của nhiều dòng. Tự thử so hai ca: ID dòng giao không tồn tại và ID tồn tại nhưng tổng số trả vượt số đã giao.

## 15/11/2026 · Nguy cơ bị nhà tuyển dụng đánh đồng với dự án đại trà

- **Lo ngại / Phản biện · 9/10.** Người dùng chỉ ra nỗi sợ thực tế: nhà tuyển dụng chỉ lướt nhanh và rất dễ đánh đồng dự án với hàng ngàn đồ án LMS tầm thường khác nếu không có cách thể hiện khác biệt. Lập luận chạm đúng thực tế tuyển dụng (vòng quét CV 10 giây).
- [ ] **Cần luyện — Kỹ năng đóng gói sản phẩm (Project Packaging).** Nhận diện cách tạo sự khác biệt ngay từ cái nhìn đầu tiên: đặt tên định vị dự án (không dùng chữ LMS chung chung), nêu số liệu người dùng thật (500 học sinh) và bài toán hạ tầng/concurrency trong CV, xây dựng file README có sơ đồ kiến trúc và ERD thay vì chỉ để code thô.

## 15/11/2026 · Đánh giá "độ nặng" của dự án khi ứng tuyển công ty công nghệ lớn (Tier 1 / Big Tech)

- **Trăn trở / Nhận định · 8/10.** Người dùng đặt câu hỏi thẳng thắn: dự án LMS này liệu có đủ "nặng" để vượt qua vòng lọc CV và thuyết phục nhà tuyển dụng ở các công ty lớn. Câu hỏi chạm đúng mục tiêu cốt lõi của việc học và tích lũy kinh nghiệm, nhận thức được tiêu chuẩn khắt khe của vòng phỏng vấn kỹ thuật.
- **Phản biện ngày 15/11/2026 · 8/10.** Người dùng chất vấn vì sao đổi ca và điểm danh được coi là điểm nổi bật khi chức năng cơ bản dễ triển khai. Phản biện đúng về giá trị của tên tính năng trên CV. Khi đánh giá bản triển khai, cần chỉ được yêu cầu cụ thể và bằng chứng về giá trị sử dụng hoặc cách xử lý ca biên.
- [ ] **Cần luyện — Tư duy "Độ sâu kỹ thuật" thay vì "Độ rộng tính năng" (Engineering Depth vs. Feature Breadth).**
  - **Điểm mấu chốt**: Công ty lớn không đánh giá Intern/Junior qua việc làm được bao nhiêu trang CRUD hời hợt, mà đánh giá qua độ chắc của nền tảng: kiến trúc 3 lớp phân tách rành mạch, tính toàn vẹn dữ liệu (ACID transaction, constraints), xử lý tranh chấp tài nguyên (Concurrency / Race conditions khi đổi ca, nộp bài thi) và đo lường chịu tải (Load testing cho 500 học sinh đồng thời).
  - **Cách tự kiểm tra**: Đứng trước một tính năng, tự hỏi: "Nếu có 500 người cùng bấm nút này trong 1 giây, hệ thống chết ở đâu và database có bị sai lệch dữ liệu không?" Nếu trả lời và chứng minh được bằng code + test, dự án đó thừa sức thuyết phục kỹ sư cty lớn.
- **Phản biện tiếp · 6/10.** Người dùng cho rằng "có người dùng thực tế là ăn chặt rồi". Nhận định nêu được một lợi thế lớn, nhưng kết luận đi quá xa so với thực tế tuyển dụng kỹ sư.
  - **Lý do**: Người dùng thật giúp vượt qua vòng lọc CV và kích thích trí tò mò của nhà tuyển dụng (Điều kiện cần). Nhưng trong phòng phỏng vấn kỹ thuật, nó lập tức trở thành "con dao hai lưỡi" (Điều kiện đủ): nếu có 500 người dùng nhưng không có tư duy vận hành (không log lỗi, không sao lưu dữ liệu, không xử lý tranh chấp khi thi, không test tải) thì sẽ bị đánh giá là "làm liều, cẩu thả".
  - [ ] **Cần luyện — Phân biệt "Bối cảnh thực tế" và "Giải pháp kỹ thuật".** Người dùng thật chỉ tạo ra bài toán thật; thứ giúp bạn "ăn chặt" là cách bạn giải bài toán đó bằng kỷ luật kỹ thuật (Production Mindset).

## 15/11/2026 · Phản biện lỗi Responsive máy móc làm hỏng giao diện chuẩn (Bản ưng số 3)

- **Phản biện · 9/10.** Người dùng thẳng thắn bác bỏ việc ép dãn giao diện theo toàn bộ chiều cao/chiều rộng màn hình lớn 24 inch, chỉ ra việc này làm ô bị méo mó ("béo phì" hoặc rỗng ruột) và phá vỡ vẻ đẹp cân đối đã đạt được ở Bản ưng 3.
- **Lý do**: Lập luận chạm trúng lỗi sai kinh điển trong thiết kế UI/UX frontend: nhầm lẫn giữa *Responsive thích ứng* (adaptive/proportional) với *kéo dãn cơ học vô tội vạ* (blind stretching). Khi màn hình quá lớn mà nội dung bên trong ít, kéo dãn `1fr` khiến ô cao tới 280px biến thành hang rỗng, còn cố nới ngang khiến ô bẹp dí.
- [ ] **Cần luyện — Tư duy Responsive bento trên màn hình lớn (Large Display UX).**
  - **Điểm mấu chốt**: Trên màn hình lớn (24"+), ưu tiên bảo vệ **Tỷ lệ khung hình (Aspect Ratio)** của component (~1 : 1.25 đến 1 : 1.35) bằng container có `max-w` hài hòa và khoảng đệm tự nhiên, thay vì ép `flex-1` / `100vh`.
  - **Cách tự kiểm tra**: Mở devtools đổi viewport từ 1366×768 lên 1920×1080: nếu ô nội dung tăng gấp đôi chiều cao nhưng chữ chỉ có 2 dòng làm thừa 80% khoảng trắng chết, đó là lỗi responsive ép dãn sai quy cách.
