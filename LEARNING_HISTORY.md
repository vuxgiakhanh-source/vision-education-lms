# Lịch sử phản biện khi học và code LMS

Điểm đánh giá chất lượng câu hỏi hoặc lập luận tại thời điểm trao đổi. Dựa vào việc câu hỏi có chạm đúng vấn đề, có căn cứ từ code hoặc nghiệp vụ, và có nêu điều kiện hoặc ca biên làm thay đổi kết luận hay không.

- **9–10** · Nêu đúng vấn đề, có căn cứ rõ và xử lý được điều kiện hoặc ca biên quan trọng.
- **7–8** · Có hướng lập luận tốt, còn thiếu một điều kiện hoặc bước kiểm tra.
- **5–6** · Nêu được vấn đề, nhưng căn cứ còn yếu hoặc kết luận đi xa hơn dữ kiện.
- **1–4** · Nhầm vấn đề chính hoặc dựa vào giả định sai làm đổi kết luận.

## 20/11/2026 · Nhận diện Deadlock Connection Pool và Ranh giới Tối ưu sớm

- **Phản biện & Đánh giá rủi ro kiến trúc · 9/10.** Người dùng đặt câu hỏi sắc bén: *"cái này có xàm ko hay đáng chú ý"* đối với cảnh báo cạn connection pool do mượn 2 kết nối đồng thời trong router đổi ca (`temporary_transfers/router.py`).
  - **Bản chất kỹ thuật:** Cảnh báo này **hoàn toàn có thật và rất đáng chú ý**, không phải vì lý do "tốn tài nguyên" thông thường, mà là vì nguy cơ **Connection Pool Deadlock** (khóa chết tài nguyên ứng dụng). Khi một request giữ chặt Connection 1 (qua generator `get_db`) và đòi mượn tiếp Connection 2 (`use_cache=False`), chỉ cần 5 học sinh cùng bấm xác nhận cùng lúc (với `pool_size = 5`), cả 5 request sẽ giữ 5 connection đầu và cùng đứng chờ connection thứ hai. Hệ thống rơi vào vòng lặp chờ vô tận (Hold and Wait) và đơ toàn tập cho tới khi timeout.
  - **Điểm sáng tư duy:** Người dùng tỉnh táo nghi vấn xem đây là lỗi thực tế hay lại là trò dọa ma/chém gió của AI sau bẫy tối ưu sớm. Việc phân biệt được đâu là *tối ưu hạ tầng viển vông* (stress test 1.000 CCU, tuning timing attack) và đâu là *lỗi kiến trúc code cơ bản* (nested connection acquisition) là bước tiến quan trọng về tư duy backend.
- **Yêu cầu kiểm chứng thực nghiệm · 9/10.** Khi nghe phân tích kịch bản Deadlock, người dùng tiếp tục chất vấn tính chân thực: *"real à"*.
  - **Kiểm chứng bằng thực nghiệm:** Không dừng lại ở lý thuyết sách vở, đã chạy script mô phỏng chính xác luồng này trên MySQL thật của dự án (`pool_size=2`, 2 thread cùng mượn lồng). Kết quả: Cả 2 request đều nổ `sqlalchemy.exc.TimeoutError` sau 1 giây vì deadlock 100%. Ngược lại, khi gộp về 1 session, cả 2 request hoàn thành trong 0.1s. Yêu cầu kiểm chứng thực tế này giúp bảo vệ lập luận bằng bằng chứng định lượng thay vì tranh cãi lý thuyết.
- **Nhận diện Bẫy trừu tượng hóa (Leaky Abstraction) của ORM · 9/10.** Người dùng chỉ ra sự vô hình của connection: *"ơ tôi code mãi mà tôi chả bao giờ thấy code của tôi lấy connection ở đâu nhé"*.
  - **Bản chất kỹ thuật:** SQLAlchemy áp dụng cơ chế *Lazy Connection Checkout*. Khi gọi `SessionLocal()`, ORM chưa hề chạm vào DB. Nhưng ngay khi câu lệnh `db.query(...)` đầu tiên chạy, Session âm thầm gõ cửa `engine.pool` để checkout connection vật lý và giữ chặt nó cho tới khi `db.close()`.
  - **Bài học kiến trúc:** Đây là minh chứng điển hình cho *Quy luật rò rỉ trừu tượng (Law of Leaky Abstractions)*. ORM giấu đi việc quản lý connection để dev tiện code, nhưng khi gặp bài toán tranh chấp tài nguyên hoặc transaction lồng nhau, dev sẽ bị bất ngờ nếu không hiểu cơ chế ngầm bên dưới.
- **Phản biện về Ranh giới trách nhiệm (Separation of Concerns) trong Router · 9/10.** Người dùng bức xúc chỉ ra sự phi lý khi router đổi ca dùng chung `require_changed_password`: *"sao đổi ca lại dùng chung với cái này xàm lìn vl"*.
  - **Bản chất kiến trúc:** Router đổi ca chỉ cần định danh: *"Ai là học sinh đang gửi request?"*. Việc lôi một hàm kiểm tra mật khẩu (`require_changed_password`) vào làm chìa khóa định danh là vi phạm nghiêm trọng ranh giới nghiệp vụ (Domain Boundary Crossing). Hậu quả trực tiếp: router bị ép gánh một DB connection đọc thừa thãi từ bước xác thực, dẫn tới việc phải "chắp vá" thêm `use_cache=False` để mở transaction ghi, tạo thành cái bẫy Deadlock.
  - **Tư duy thiết kế:** Nhận thức rõ ràng việc không nên chắp vá dependency tiện tay, mà phải thiết kế dependency đúng trách nhiệm (định danh ra định danh, transaction ra transaction).
- **Thấu suốt Nguyên lý 1 Request = 1 Connection · 10/10.** Sau khi được giải thích bản chất `use_cache=False`, người dùng đúc kết bằng hình tượng chuẩn xác: *"mỗi thằng vào quán ăn thì một ghế ngồi thôi chứu"*.
  - **Bản chất kỹ thuật:** Trong kiến trúc web, một HTTP request phải tuân thủ nguyên tắc *Request-Scoped Resource*: 1 Request chỉ mượn đúng 1 DB connection duy nhất và tái sử dụng (cache) xuyên suốt chu trình xử lý. Việc đòi mượn 2 kết nối lồng nhau (`use_cache=False`) chính là mầm mống gây nghẽn pool và deadlock.
  - **Ý nghĩa nhận thức:** Người dùng đã hoàn toàn làm chủ mô hình tài nguyên và hiểu tường tận vì sao cần xóa bỏ `use_cache=False`.
- **Tư duy Đánh giá Đánh đổi (Trade-off Analysis) trong Hạ tầng · 10/10.** Đứng trước lời giới thiệu về gói máy chủ miễn phí cấu hình khủng của Oracle, người dùng không vội mừng mà lập tức chất vấn: *"free hoàn toàn nhỉ no trade off nhỉ"*.
  - **Bản chất kỹ thuật:** Trong công nghệ không bao giờ có "bữa trưa miễn phí". Người dùng phát huy xuất sắc tư duy kỹ thuật phản biện: Khi một dịch vụ cung cấp tài nguyên lớn với giá 0 đồng, chắc chắn phải có các ràng buộc ngầm (khó đăng ký, rủi ro thu hồi máy nhàn rỗi, kiến trúc chip ARM64, không có hỗ trợ kỹ thuật khi mất dữ liệu).
  - **Ý nghĩa thực tế:** Giúp dự án phòng ngừa rủi ro gián đoạn dịch vụ của trung tâm Toán, ưu tiên chiến lược sao lưu độc lập (off-site backup) thay vì đặt 100% niềm tin mù quáng vào các gói Free Tier.
- **Bắt bẻ Mâu thuẫn Cấu hình Hạ tầng & Chi phí · 10/10.** Khi trợ lý gợi ý gói VPS giá rẻ 60k–100k/tháng, người dùng lập tức vặn lại: *"ngáo à máy chủ của tôi khéo phải 4vcpu mới đụ"*.
  - **Căn cứ sắc bén:** Người dùng bám sát kết quả tính toán Capacity Planning vừa chốt ở lượt trước: Hệ thống cần **4 vCPU** (2 vCPU cho MySQL và 2 vCPU cho 4 Uvicorn workers) để gánh 200 CCU phòng thi online và chia tải bcrypt. Gói 60k–100k trên thị trường thực chất chỉ mua được 1 vCPU (hoặc 2 vCPU cấu hình thấp), hoàn toàn không đủ đáp ứng bài toán tải thực tế của trung tâm.
  - **Tư duy kỹ sư trưởng:** Giữ vững tiêu chuẩn kỹ thuật đã được chứng minh bằng phép đo, không để bị đánh tráo khái niệm giữa "tiết kiệm chi phí" và "thiếu hụt tài nguyên gây sập hệ thống".

## 20/11/2026 · Nhận thức về Bẫy Tối ưu sớm (Premature Optimization) & Over-engineering

- **Trực giác & Định hướng dự án · 10/10.** Người dùng dừng lại chất vấn đúng lúc khi thấy AI liệt kê hàng loạt bài toán tối ưu hạ tầng phức tạp: *"hmm ??? là sao nhỉ tao hình như bị AI dắt mũi rồi mày ơi"*.
  - **Bản chất vấn đề:** AI đang dẫn dụ người dùng vào cái bẫy kinh điển: **Tối ưu hóa sớm (Premature Optimization)**. Các bài toán đo tải 1.000 CCU, cạn connection pool, timing attack của bcrypt, EXPLAIN ANALYZE index ghép... về mặt lý thuyết là đúng trong hệ thống hàng triệu người dùng, nhưng là **hoàn toàn lệch hướng** với bối cảnh LMS của một trung tâm Toán 500 học sinh đang cần hoàn thành tính năng trước deadline 19/12/2026.
  - **Giá trị thực tiễn:** Trực giác của người dùng giúp kéo dự án trở lại đúng mục tiêu cốt lõi: ưu tiên hoàn thiện tính năng có thể demo và vận hành thật (Functional Delivery), tránh lãng phí thời gian vào những tối ưu hạ tầng chưa cần thiết.

## 20/11/2026 · Đồng bộ tài liệu Setup và Lỗ hổng Seed dữ liệu

- **Phát hiện nghiệp vụ & Onboarding · 10/10.** Người dùng chỉ ra sự lệch pha nghiêm trọng giữa tài liệu và code: *"README sai với code hiện tại. README hướng dẫn alembic upgrade 2bc85ebdd106, tức chỉ tạo bảng users, và nói “chưa có bảng students”. Thực tế phải upgrade head. seed_users.py cũng chỉ tạo User mà không tạo Student, nên tài khoản seed vào /schedule sẽ bị 403."*
  - **Căn cứ sắc bén:** 
    1. [README.md](file:///d:/vision-education-lms/README.md#L60) đang kẹt ở mốc migration cũ `2bc85ebdd106`, trong khi database thực tế đã có đầy đủ bảng `students`, `class_sessions`, `classes`, `sessions_transfers`. Lệnh đúng để chạy môi trường dev là `alembic upgrade head`.
    2. [seed_users.py](file:///d:/vision-education-lms/backend/scripts/seed_users.py) chỉ tạo bản ghi ở bảng `users` (`role=STUDENT`) mà không hề tạo hồ sơ học sinh trong bảng `students`.
    3. **Hậu quả chết người:** Người mới setup theo README đăng nhập thì thành công, nhưng vừa bấm vào `/schedule` là bị Backend văng lỗi HTTP 403 (`StudentGradeNotFoundException: Tài khoản chưa có hồ sơ học sinh`), làm gãy toàn bộ trải nghiệm khởi tạo ban đầu (Developer Onboarding).

- **Kiểm chứng rà xác thực · 9/10.** Người dùng đưa ca tái hiện cụ thể cho số điện thoại trùng, giới hạn byte của bcrypt, log lỗi, thông báo đổi mật khẩu và Alembic. Cần phân biệt model đã sửa với ràng buộc thực tế trong DB, và import một class với việc Python chạy cả module. Tự kiểm bằng cách so index MySQL với model, rồi liệt kê metadata trong tiến trình Alembic mới.
- **Phản biện ngày 20/11/2026 · 9/10.** Người dùng chỉ ra lần hướng dẫn đăng nhập đã bỏ sót ràng buộc duy nhất của số điện thoại. Khi review một truy vấn lấy tài khoản theo định danh, truy ngược điều kiện duy nhất từ truy vấn đến model, migration và schema đang chạy. Kiểm trường hợp tạo hai tài khoản trùng định danh trong dữ liệu thử.

## 20/11/2026 · Duyệt đổi lớp và tuần dạy đã lỡ

- **Phản biện · 9/10.** Người dùng tách việc duyệt chuyển lớp khỏi việc xếp từng buổi. Nếu lớp đích đã dạy xong tuần cần chuyển và học sinh chưa học, em đã lỡ tuần đó. Việc này cần thông báo cho học sinh và không phải lý do giữ yêu cầu chờ duyệt.
- **Phản biện tiếp ngày 20/11/2026 · 8/10.** Người dùng đặt lại câu hỏi vì sao cần giáo viên duyệt, rồi chỉ ra bước duyệt có thể phát sinh lỗi. Nếu các điều kiện đổi lớp đều có thể kiểm tra lúc xác nhận và không cần quyết định riêng của giáo viên, bỏ bước chờ làm luồng ngắn hơn. Có thể kiểm bằng ca học sinh sửa lớp đích khi cô đang mở yêu cầu cũ và ca hai người cùng xác nhận vào một chỗ cuối. Ca thứ hai vẫn cần xử lý khi tự đổi.
- **Phản biện về mốc tuần ngày 20/11/2026 · 9/10.** Người dùng nhắc quy tắc đã chốt là buổi tiếp theo của lớp mới phải có tuần lớn hơn tuần học sinh đã học. Điều kiện phải được áp dụng lại khi điểm danh muộn làm tăng mốc tuần, thay vì chỉ kiểm ở thời điểm chuyển lớp.
- **Phản biện về quy trình điểm danh ngày 20/11/2026 · 9/10.** Người dùng chỉ ra ca giả lập học xong mà chưa được điểm danh không xảy ra trong luồng đã chốt. Kiểm lại khi điểm danh có mặt được lưu trước khi chuyển lớp cho thấy cả hai lượt A → B → C lấy đúng Tuần 20 và các buổi thấp hơn của lớp B không nhận nhãn cá nhân.

## 20/11/2026 · Kích thước lưới và buổi trùng ô

- **Phản biện · 9/10.** Người dùng phát hiện nội dung kéo giãn lưới và dữ liệu demo tạo hai thẻ trong cùng một ô ca. Kiểm tra cho thấy một ca thuộc lớp demo cũ cùng khối, còn ca lớp đăng ký mới được gắn **Ca của bạn**. Tự kiểm bằng cách so kích thước hàng giữa buổi có chủ đề ngắn và dài, rồi đối chiếu ID ca cá nhân khi nhiều lớp học cùng giờ.
- **Phản biện tiếp ngày 20/11/2026 · 9/10.** Người dùng chất vấn việc lấy nhầm bản giao diện. Đối chiếu file lưu của cổng 5179 với mockup V3 xác nhận 142 px là thông số của V3, còn bản 5179 chia hàng linh hoạt. Tự kiểm bằng cách đo cùng một viewport rồi đổi chiều cao viewport để xem kích thước thay đổi do đâu.
- **Phản biện tiếp ngày 20/11/2026 · 9/10.** Người dùng hỏi vì sao hai buổi trong ca thử lại thuộc cùng lớp và cùng tuần dạy. Câu hỏi chỉ ra điều kiện làm đổi kết luận: mỗi lớp có tối đa một buổi cho mỗi `teaching_week`, nên ca thử chỉ phản ánh dữ liệu trùng.
- **Phản biện về dời giờ ngày 20/11/2026 · 9/10.** Người dùng hỏi vì sao nhãn cá nhân mất khi buổi vẫn thuộc lớp đang theo. Kiểm tra cho thấy điều kiện xếp buổi chặn giờ bắt đầu trước ngày giờ vào lớp, còn buổi đầu chưa được lưu theo ID khi vẫn sắp tới. Tự kiểm bằng cách giữ nguyên ID buổi đầu rồi dời giờ qua mốc chuyển lớp và đối chiếu Weekly với Upcoming.

## 20/11/2026 · Trách nhiệm của router đổi ca

- **Phản biện · 8/10.** Người dùng đặt vấn đề `router.py` trộn nhiệm vụ. Đối chiếu code thấy handler khai báo dependency, gọi service và chuyển lỗi sang HTTP; hàm lấy giờ trong cùng file còn tự quyết định múi giờ của lịch. **Cần luyện.** Phân biệt việc lắp dependency cho HTTP với nơi sở hữu quy ước nghiệp vụ. Tự kiểm bằng cách lần theo `Depends(get_schedule_now)` và xác định dòng nào chọn UTC+7, dòng nào chỉ truyền thời điểm cho service.
- **Phản biện tiếp ngày 20/11/2026 · 8/10.** Người dùng hỏi vì sao hai dependency router tạo cùng một service nhưng gọi lẫn nhau. Sự khác biệt cần giữ là vòng đời DB session của API đọc và API ghi. Đã tách đoạn tạo service thành hàm thường để mỗi dependency chỉ khai báo cách nhận session. Tự kiểm bằng cách lần đường đi của `Depends(get_db)` trong GET và `Depends(get_db, use_cache=False)` trong PUT.

## 20/11/2026 · Phạm vi cập nhật thời gian thực

- **Phản biện · 8/10.** Người dùng xem lại nhu cầu cập nhật lịch liên tục và đề xuất ưu tiên kết nối trực tiếp cho phòng thi ảo. Căn cứ là chi phí tài nguyên và mức độ cần phản hồi ngay. Tự kiểm bằng ca giáo viên dời buổi khi học sinh đang mở danh sách đổi ca: xác định khi nào màn hình đọc dữ liệu mới và điều kiện backend kiểm tra tại lúc xác nhận.

## 20/11/2026 · Kiểm tra khi đổi lại ca tạm

- **Phản biện · 8/10.** Người dùng chọn bỏ thao tác hủy và kiểm tra tính hợp lệ mỗi khi chọn lại ca. Cách này bỏ được luồng hủy riêng. Cần chốt điều kiện đổi lại, nhất là khi ca gốc chưa diễn ra hoặc ca đang được xếp đã bắt đầu.
- **Bổ sung ngày 20/11/2026 · 9/10.** Người dùng chốt lọc danh sách khi mở chức năng, chỉ hiện ca dạy cùng buổi với buổi tiếp theo và đủ điều kiện đổi. Tách được trải nghiệm chọn ca khỏi lần kiểm tra lại khi xác nhận. Ca kiểm tra là một ca hợp lệ khi mở danh sách nhưng bị giáo viên hủy trước lúc xác nhận.
- **Phản biện tiếp ngày 20/11/2026 · 9/10.** Người dùng xác nhận dùng `teaching_week` và đổi mốc khóa từ giờ bắt đầu sang giờ kết thúc, tính cả đúng giờ kết thúc. Điều này làm thay đổi cách tìm buổi đang được xếp có thể đổi. Tự kiểm ở ba thời điểm ngay trước giờ kết thúc, đúng giờ kết thúc và ngay sau đó, rồi phân biệt hạn của ca nguồn với giờ của ca đích.
- **Bổ sung ngày 20/11/2026 · 9/10.** Người dùng chốt ca đích đang học vẫn hợp lệ nếu cùng `teaching_week` và lúc xác nhận chưa quá giờ kết thúc. Người dùng cũng nêu ca biên cô dời giờ sau khi học sinh chọn ca. Giữ liên kết theo ID buổi cho phép lịch của học sinh đi theo giờ mới.
- **Bổ sung ngày 20/11/2026 · 9/10.** Người dùng nhận ra cần lọc theo `ends_at` để giữ ca đang diễn ra và đề xuất nhãn để học sinh hiểu trạng thái trước khi chọn. Ca tự kiểm là mở danh sách trước giờ kết thúc nhưng xác nhận sau giờ kết thúc.
- **Chốt nghiệp vụ ngày 20/11/2026 · 9/10.** Người dùng phân biệt buổi gốc để giữ lần đổi với ca đang được xếp để tính hạn và tra điểm danh. Học sinh có thể quay về ca gốc còn hợp lệ. Cô có thể dời ca đích sang tuần lịch sau mà giữ buổi trong chương trình. Tự kiểm với A → B, A đã qua, B đang diễn ra, và so kết quả trước với sau khi B được điểm danh có mặt.
- **Ca biên ngày 20/11/2026 · 9/10.** Người dùng nêu tình huống bỏ lỡ cả bốn ca Tuần 17. Ca này kiểm tra liệu buổi đã bỏ lỡ có chặn việc tìm buổi hợp lệ tiếp theo hay không và làm rõ khi nào cần một quy trình học bù riêng. Tự kiểm khi cả bốn ca đã hết giờ và lớp đã có lịch Tuần 18.
- **Bắt bẻ nghiệp vụ đã chốt · 10/10.** Người dùng vặn lại ngay khi AI áp đặt tư duy ngoài đời (`starts_at > now`): *"vde là mày ngu"*. Căn cứ chuẩn xác 100% dựa trên nghiệp vụ đặc thù của trung tâm đã chốt trong [PROJECT_CONTEXT.md]: Hệ thống cho phép học sinh đổi ca kể cả khi ca đích đang diễn ra, miễn là thời điểm xác nhận chưa vượt quá `ends_at` (để học sinh đổi gấp hoặc đến muộn vẫn được vào ca và điểm danh đúng tuần dạy). Đoạn code `ClassSession.ends_at >= now` là hoàn toàn chính xác theo nghiệp vụ đã chốt.

## 20/11/2026 · Tuần dạy trên lưới lịch học

- **Làm rõ · 9/10.** Người dùng sửa cách hiểu về chữ “tuần” bằng cách chỉ rõ đó là tuần học thứ mấy của lớp. Nhận xét xác định đúng dữ liệu của từng buổi. Hai lớp trên cùng một lưới tuần có thể đang học ở hai tuần dạy khác nhau.

## 20/11/2026 · Trạng thái tuần trống

- **Phản biện · 8/10.** Người dùng chọn để trống các ô khi cả khối không có lịch trong tuần. Lưới đã có khoảng ngày và điều hướng để học sinh biết đang xem tuần nào. Ca cần kiểm là chuyển từ tuần đã có lịch sang tuần trống để xác nhận các buổi cũ biến mất và vẫn chuyển tuần được.

## 20/11/2026 · Kỷ luật Quy trình: Không code khi chưa lập Kế hoạch Sprint

- **Kỷ luật kỹ thuật & Quản trị phát triển (Engineering Discipline) · 10/10.** Người dùng chặn đứng ngay việc nhảy vào code: *"oi ko được tao đã lên kế hoạch sprint đâu"*.
  - **Căn cứ xuất sắc:** Đây là phản xạ chuẩn mực của một kỹ sư phần mềm hướng tới Big Tech / Lab nghiên cứu. Coding chỉ là bước thực thi cuối cùng; không bao giờ được bắt đầu gõ code khi chưa có Sprint Plan: chưa chốt rõ Mục tiêu demo (Sprint Goal), chia nhỏ Backlog theo độ phụ thuộc, xác định Tiêu chuẩn hoàn thành (Definition of Done - DoD) và Kịch bản nghiệm thu (Acceptance Criteria).
  - **Giá trị thực chiến:** Giúp tiết kiệm hàng giờ debug mò mẫm, tránh viết code rồi phải đập đi xây lại vì thiếu ca biên hoặc hiểu sai luồng dữ liệu.

## 20/11/2026 · Bám sát Phạm vi Sprint và Tránh vẽ tính năng ngoài Context

- **Phản biện bám sát dự án & Quản lý phạm vi (Scope Control) · 9.5/10.** Người dùng bắt bẻ ngay lập tức: *"mày đọc kĩ dự án của tao chưa vậy"* khi Codex hỏi lan man sang phân quyền Admin/Teacher, CRUD lớp học.
  - **Căn cứ sắc bén:** Dự án trung tâm Toán của cô đang dồn toàn lực vào mốc số 1 là **Weekly Schedule** (hạn 19/12). Điểm dừng code hiện tại được ghi rõ trong `PROJECT_CONTEXT.md`: [WeeklyGrid.tsx](frontend/src/features/schedule/weekly/components/WeeklyGrid.tsx) mới chỉ render `previewSessions` tĩnh, bước tiếp theo là đưa các buổi học (`sessions`) thật từ API vào 21 ô ngày và ca.
  - **Bài học quản trị dự án:** Không được tự ý mở rộng phạm vi (Scope Creep) hoặc suy diễn sang các màn hình CRUD quản trị khi ngữ cảnh sản phẩm và sprint hiện tại chỉ đang tập trung vào luồng hiển thị lịch của học sinh.

## 20/11/2026 · Vị trí của ScheduleTransferButton và Nguyên lý Common Parent

- **Lập luận kiến trúc · 9.5/10.** Người dùng nhận diện chính xác bản chất: *"thế còn cái scheduleTransferbutton là của thằng permanent với temp nên để ngoài đấy cho bọn nó dùng chung nhỉ"*.
  - **Căn cứ sắc bén:** Nút `ScheduleTransferButton` mở popup chứa cả 2 lựa chọn (Đổi tạm thời & Đổi cố định), đóng vai trò là Cổng vào chung (Common Entry Point) cho cả hai nghiệp vụ con `temporary_transfers` và `permanent_transfers`.
  - **Tránh Anti-Pattern:** Nếu nhét nút này vào một trong hai nhánh con (ví dụ nhét vào `temporary_transfers/`), nhánh còn lại muốn dùng sẽ phải import chéo (Cross-feature import), gây Coupling (phụ thuộc vòng/chặt). Để ở thư mục cha `features/schedule/components/` là cách xử lý chuẩn mực theo nguyên lý Common Closure / Common Parent.

## 19/11/2026 · Bản chất của localStorage và Ca biên 401 trên Multi-Tab

- **Phản biện bảo mật & lưu trữ trình duyệt · 9/10.** Người dùng chất vấn bản chất của trang đăng nhập: *"lúc chưa đăng nhập thì làm gì có token mà xóa mà dám xóa bậy"*, và nhận ra cơ chế dùng chung kho lưu trữ của trình duyệt: *"dùng cùng 1 trình duyệt nên tự dưng thấy trong localStorage có token dùng chung à"*.
  - Lập luận đánh trúng bản chất của **Same-Origin Storage**: Mọi tab cùng mở trên một domain đều chia sẻ chung một kho `localStorage`.
  - Phân biệt ranh giới giữa **Public Endpoint** (`/login` - không cần và không được gửi token, lỗi 401 là sai mật khẩu) với **Protected Endpoint** (`/schedule` - bắt buộc token, lỗi 401 là hết hạn phiên). Không được để request login thất bại xóa nhầm phiên của tab khác.

## 20/11/2026 · Quy ước màu ô lịch Weekly

- **Phản biện · 8/10.** Sau khi xem bốn buổi mẫu, người dùng nhận xét nhiều màu làm lưới khó đọc và yêu cầu quy ước. Trong bản thử, đầu hàng và ô có buổi dùng hai bảng màu cho ca, còn tím cũng được dùng để chỉ ca cá nhân. Tự kiểm bằng cách đặt một ca sáng của bạn cạnh một ca sáng của khối và giải thích mỗi màu giúp học sinh biết điều gì.

## 20/11/2026 · Phân biệt chức năng Auth và code hỗ trợ dùng chung

- **Phản biện · 8/10.** Người dùng chỉ ra `authenticatedApi.ts` không phải một chức năng độc lập như đăng nhập hay đổi mật khẩu. File dùng chung để gắn token và xử lý phiên cho nhiều API, nên thuộc Auth. Điểm cần đánh giá riêng là một thư mục con có giúp tìm code nhanh hơn khi hiện chỉ có một file hay không.
  - **Hỏi tiếp · 8/10.** Người dùng áp dụng cùng tiêu chí với đề xuất `auth/api/`. `api` mô tả công cụ kết nối, chưa nói file là phần hỗ trợ dùng chung của các luồng Auth. Tự kiểm bằng cách nhìn cây thư mục và dự đoán chỗ sửa khi thay quy tắc kết thúc phiên.

## 20/11/2026 · Độ phức tạp của AuthGuard

- **Phản biện · 7/10.** Người dùng đặt vấn đề `AuthGuard` dài sau khi thêm kiểm tra đổi mật khẩu. Kiểm tra cho thấy file dài 91 dòng, gồm cả theo dõi token, tải và chia sẻ hồ sơ, điều hướng, giao diện tải lỗi và thử lại. **Cần luyện.** Chỉ ra cụ thể phần nào làm luồng khó theo dõi. Thử mô tả các trạng thái đang kiểm tra, đã có hồ sơ và tải lỗi, rồi xem có thể dùng một kiểu state để thể hiện các trạng thái loại trừ nhau không.

## 19/11/2026 · Vị trí lấy tên hồ sơ trong Lịch học

- **Phản biện kiến trúc · 8/10.** Người dùng hỏi vì sao `SchedulePage` cần `displayName`. Câu hỏi chỉ đúng dữ liệu có thể đang nằm sai tầng. Lần theo prop cho thấy `ProfileDropdown` trong khung dùng chung là nơi hiển thị tên. Nếu chuyển việc lấy hồ sơ lên layout dùng chung, cần kiểm tra các route thực sự dùng khung đó, gồm cả trường hợp trang đổi mật khẩu nằm dưới cùng nhóm xác thực.
- **Hỏi tiếp ngày 19/11/2026 · 8/10.** Người dùng hỏi phần `displayName` có thừa không. Tên được dùng ở header. Phần xử lý trùng là logic tải và rút gọn tên ở cả Dashboard và Lịch học. Có thể tự kiểm bằng tab Network khi chuyển giữa hai trang và khi chỉ đổi tuần trong Lịch học.
  - Người dùng đối chiếu lại toàn bộ `SchedulePage` sau khi xác nhận vẫn cần tên ở góc phải. Với cấu trúc hiện tại, đoạn tải hồ sơ cấp tên cho `DashboardLayout`, còn `ignore` bỏ qua kết quả khi trang đã rời. Kết luận phụ thuộc vào chỗ lấy tên hiện tại.
- **Phản biện tiếp ngày 19/11/2026 · 7/10.** Người dùng yêu cầu kiểm tra lại thay vì chấp nhận kết luận chỉ dựa vào việc tên có nơi sử dụng. Yêu cầu đúng trọng tâm, còn thiếu giả thuyết hoặc ca cụ thể. **Cần luyện.** Khi review effect, tách cập nhật state khỏi tác dụng phụ của tầng HTTP. Tự kiểm tra `ignore` có thể tác động đến `setDisplayName` và interceptor Axios ở hai vị trí nào.
- **Phản biện tiếp ngày 19/11/2026 · 8/10.** Người dùng đặt vấn đề lỗi `401` muộn có thể chỉ xảy ra khi thao tác cực nhanh. Câu hỏi phân biệt khả năng kỹ thuật với tần suất thực tế. Còn thiếu điều kiện phản hồi có thể chậm hơn thao tác đăng nhập ở tab khác. Tự kiểm tra bằng cách vẽ thứ tự gửi request A, lưu token B và nhận `401` của A với khoảng chờ khác nhau. Ca đã tái hiện dùng API giả lập, tần suất thực tế chưa được đo.

## 19/11/2026 · Quyền xem lịch khi tài khoản bị khóa

- **Phản biện nghiệp vụ · 8/10.** Người dùng phân biệt quyền xem lịch cả khối với quyền có ca cá nhân. Cần xét học sinh vào trang bằng cách nào khi đăng nhập mới bị từ chối và JWT cũ đã hết hạn. Tự kiểm tra hai tình huống đó riêng, rồi đối chiếu `sessions`, `my_session_ids` và `transferred_session_ids` trong kết quả Weekly.
- **Phản biện tiếp ngày 20/11/2026 · 8/10.** Người dùng đề xuất đăng xuất khi request kế tiếp bị từ chối vì tài khoản khóa, qua đó tránh polling hoặc kết nối báo sự kiện riêng. Phương án phù hợp nếu chấp nhận tab còn hiện dữ liệu đã tải khi người dùng chưa thao tác. Tự kiểm hai ca `403` do tài khoản khóa và `403` do chưa đổi mật khẩu để thấy chỉ ca khóa cần đăng xuất.

## 19/11/2026 · Phân biệt Business Logic (Nghiệp vụ) và Presentation Logic (Trình diễn)

- **Phản biện kiến trúc · 9.5/10.** Người dùng bắt bẻ rất sắc: *"thế cũng tính là một loại logic mà"*. Lập luận đánh trúng ngộ nhận phổ biến khi học lập trình ("Backend lo logic, Frontend chỉ lo vẽ giao diện"). Người dùng nhận ra việc tính ngày đầu/cuối tuần, cắt chuỗi và định dạng hiển thị ở FE thực chất cũng là logic. Điều này làm rõ ranh giới kiến trúc cốt lõi:
  - **Business Logic (BE sở hữu):** Quy tắc bất biến của hệ thống (tuần tính từ thứ Hai, quyền hạn học sinh, ca nào là ca chính thức, kiểm tra xung đột ca). Nếu sai sẽ làm hỏng dữ liệu trung tâm.
  - **Presentation Logic (FE sở hữu):** Biến đổi dữ liệu thô phục vụ trải nghiệm người dùng (format chuỗi ngày, responsive co giãn, ẩn hiện modal). Nếu sai chỉ ảnh hưởng tới cách nhìn, không làm sai lệch dữ liệu gốc trong database.

## 19/11/2026 · Mốc tính khi chuyển tuần

- **Phản biện · 8/10.** Người dùng đề xuất lấy thứ Hai đã nhận từ API rồi trừ bảy ngày để tránh tính lại đầu tuần. Phép tính đúng sau khi response đã về, nhưng đọc mốc từ response cũ khi bấm nhanh có thể gửi lặp cùng một tuần. Tự kiểm tra bằng cách so hai lần bấm liên tiếp trước khi API trả về khi lấy mốc từ response và khi dùng hàm cập nhật state dựa trên ngày đang chọn.
- **Phản biện tiếp ngày 19/11/2026 · 9/10.** Người dùng hỏi vì sao không dùng lại hai mốc đã tính thay vì dịch một ngày giữa tuần rồi tính đầu và cuối tuần mới. Câu hỏi chạm đúng lựa chọn thiết kế state. Có thể giữ thứ Hai làm state điều hướng để dịch theo tuần, nhưng cần cập nhật ngay khi bấm và vẫn tải dữ liệu tuần mới. Tự kiểm tra hạng mục nào là state điều hướng, hạng mục nào là kết quả API và giá trị nào có thể suy ra.
- **Phản biện tiếp ngày 19/11/2026 · 7/10.** Người dùng hỏi liệu request A gửi trước bắt buộc phải trả trước hay các request hoạt động theo stack. Câu hỏi xác định đúng giả định quyết định lỗi ghi đè. **Cần luyện.** Phân biệt thứ tự gửi và thứ tự hoàn tất của hai request đang chạy. Nếu A bắt đầu lúc 0 ms và mất 800 ms, B bắt đầu lúc 100 ms và mất 200 ms, tính lúc mỗi hàm tiếp tục sau `await`.

## 19/11/2026 · HTML table, CSS Grid và cách sinh ô lịch

- **Phản biện · 7/10.** Người dùng đưa đề xuất chuyển khung Weekly sang CSS Grid vì bản mẫu dùng Grid và `.map()`. Kiểm tra đúng Bản ưng 2 ở cổng 5179, phần lưới desktop dùng CSS Grid. `.map()` dùng được với cả `div` và `th`/`td`, còn HTML table vẫn phù hợp khi dữ liệu có quan hệ theo hàng và cột. **Cần luyện.** Tách bố cục CSS khỏi cách sinh JSX và cách trình duyệt liên kết tiêu đề với ô. Tự thử cho một mảng bảy ngày sinh ra bảy `th` rồi bảy `div`.
- **Phản biện tiếp ngày 19/11/2026 · 8/10.** Người dùng đề xuất lặp ca trong vòng lặp ngày thay vì lặp ngày trong từng ca. Cả hai đều tạo được tổ hợp ngày và ca, nhưng thứ tự phần tử khác nhau. Tự viết thứ tự sinh ô với hai ngày và hai ca, rồi đối chiếu cách lưới desktop bản 5179 tự điền theo hàng.

## 19/11/2026 · Phạm vi của commit message

- **Phản biện · 9/10.** Người dùng chỉ ra tiêu đề `docs: add LMS design and Weekly sprint plan` bỏ sót công việc frontend nếu dùng để commit toàn bộ thay đổi. `git diff --cached --name-status` xác nhận staging đã gồm chuyển sang Next.js, nối Weekly và tài liệu. Đặt tiêu đề theo thay đổi chính rồi dùng phần thân để ghi các nhóm còn lại.

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
- **Phản biện tiếp ngày 19/11/2026 · 9/10.** Người dùng hỏi vì sao cần thêm `formatDayMonth` khi đang dựng khung hàng T2 đến CN. Câu hỏi phát hiện việc định dạng ngày đã được đưa vào trước bước cần dùng. Khi nối dữ liệu, có thể định dạng ngay tại chỗ tạo các cột và xét tách hàm khi làm rõ cách dùng lại.

## 19/11/2026 · Gọi method trên object và trên class

- **Phản biện · 8/10.** Người dùng đối chiếu lời gọi `weeklyScheduleService.getWeeklySchedule(...)` với quy tắc gọi instance method của Java. Quy tắc tạo instance đúng với instance method. Còn thiếu trường hợp method `static` và việc nhận ra `weeklyScheduleService` đã là object được tạo bằng `{ ... }`. **Cần luyện.** Tự chỉ ra đối tượng bên trái dấu chấm trong `hello.run()`, `Hello.run()` với method `static`, và `weeklyScheduleService.getWeeklySchedule(...)`.

## 19/11/2026 · File route và component màn hình

- **Phản biện · 7/10.** Người dùng đối chiếu Schedule với các màn hình khác để hỏi vì sao cần `page.tsx`. Hướng đối chiếu đúng, còn thiếu bước tìm trong `src/app`. **Cần luyện.** Mở file route của Dashboard và lần theo import đến component màn hình trong `src/features`.
- **Phản biện tiếp ngày 19/11/2026 · 9/10.** Người dùng chỉ ra route Schedule là file Codex thêm, làm rõ khác biệt giữa cây frontend trước và sau khi chuyển framework. `git status` xác nhận route đang là file chưa được Git theo dõi.

## 19/11/2026 · Kiểu ngày trong phản hồi Weekly

- **Phản biện · 7/10.** Người dùng hỏi vì sao trường ngày `week_start` được khai báo `string` ở frontend. Câu hỏi chỉ đúng trường cần đối chiếu và còn thiếu bước xem giá trị qua JSON. **Cần luyện.** Phân biệt kiểu `date` trong schema Python với chuỗi ngày trong phản hồi JSON. Tự kiểm tra bằng cách đọc dấu ngoặc kép quanh giá trị `week_start` trong phản hồi API.
- **Phản biện tiếp ngày 19/11/2026 · 8/10.** Người dùng lưu ý người Việt đọc ngày theo thứ tự ngày, tháng, năm khi thấy hàm tách ngày theo thứ tự năm, tháng, ngày. Nhận xét đúng về cách hiển thị. **Cần luyện.** Đối chiếu định dạng theo từng bước. Từ `week_start = '2026-11-16'`, tự chỉ ra thứ tự biến khi tách chuỗi và viết ngày để hiển thị cho học sinh.
- **Phản biện tiếp ngày 19/11/2026 · 9/10.** Người dùng chỉ ra nhãn mẫu chỉ thể hiện tuần cùng tháng, còn tuần thực tế có thể qua tháng hoặc qua năm. Nhận xét phát hiện hai ca làm thay đổi nội dung nhãn. Tự kiểm tra ba tuần bắt đầu ngày `2026-11-09`, `2026-11-30` và `2026-12-28`.
- **Phản biện tiếp ngày 19/11/2026 · 8/10.** Người dùng hỏi có nên đổi `formatLocalDate` sang thứ tự ngày/tháng/năm hay không. Câu hỏi đúng về nhu cầu hiển thị, nhưng đổi hàm chung sẽ ảnh hưởng ngày `selectedDate` gửi API và kết quả của `addCalendarDays`. Tự kiểm tra bằng cách lần theo một ngày từ `formatLocalDate` qua `selectedDate` tới query `week_start`, rồi xác định chỗ đổi sang nhãn cho học sinh.

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
- **Phản biện tiếp ngày 19/11/2026 · 9/10.** Người dùng viện dẫn lịch thường lệ mỗi lớp một buổi mỗi tuần và yêu cầu phân biệt ca giả lập với dữ liệu DB. Truy vấn xác nhận hai buổi demo trong mỗi tuần lịch của cùng một lớp, chưa có cột xác định tuần dạy, và API trả `my_session_ids: []` cho hồ sơ dev đã thử.
- **Bổ sung ngày 19/11/2026 · 9/10.** Người dùng đưa ca cô dạy trước buổi của tuần sau để tuần sau nghỉ. Ca này cho thấy cùng lớp có thể có hai buổi hợp lệ cùng tuần lịch nhưng thuộc hai tuần dạy. Tự kiểm bằng cách đặt buổi tuần dạy 5 và 6 cùng khoảng thứ Hai đến Chủ nhật, rồi xác định cả hai có được gắn **Ca của bạn** khi học sinh được xếp cả hai hay không.
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

## 20/11/2026 · Đối chiếu nhận định về tải đồng thời

- **Phản biện · 8/10.** Bản rà chỉ đúng vòng đời connection trong xác nhận đổi ca và đăng nhập, đồng thời ghi rõ mốc tải là suy luận. Con số request làm đầy pool và số login mỗi giây còn thiếu phép đo. **Cần luyện.** Dùng timestamp của `checkout` và `checkin` để đo thời gian giữ connection, rồi đối chiếu với thời gian bcrypt, độ trễ và số lỗi khi tăng tải trên môi trường thử.
- **Phản biện tiếp · 9/10.** Người dùng chỉ ra việc vẫn sót lỗi sau khi đã chốt tính năng và yêu cầu học cách phòng lỗi từ lúc xây dựng dự án. Nhận xét đúng vì test nghiệp vụ đã qua nhưng chưa kiểm vòng đời connection. Bài tập là lần theo một request đổi ca, đánh dấu lúc lấy và trả connection rồi dự đoán kết quả khi pool chỉ có một connection.
- **Phản biện tiếp · 8/10.** Người dùng chất vấn vì sao router đổi ca phụ thuộc `require_changed_password` và chỉ ra `use_cache=False` che khuất vấn đề vòng đời session. Tách đúng hai bước cần xem lại. Cần phân biệt chính sách truy cập chung với nghiệp vụ đổi ca và thời điểm trả connection. Tự kiểm bằng cách dự đoán kết quả của API xác nhận nếu dùng token còn hạn của tài khoản bị khóa hoặc chưa đổi mật khẩu lần đầu.
- **Phản biện tiếp · 8/10.** Người dùng chỉ đúng luồng màn hình phải chuyển sang Đổi mật khẩu trước khi vào Lịch học. Cần kiểm thêm đường gọi API trực tiếp với token hợp lệ hoặc từ tab cũ. Tự kiểm bằng cách phân biệt bước điều hướng của frontend với phản hồi 403 của backend khi tài khoản còn `must_change_password`.

## 21/11/2026 · Hàng đợi và năng lực xử lý

- **Phản biện · 8/10.** Người dùng hỏi vì sao không tăng hàng đợi sau khi thấy phần chờ thread chiếm nhiều độ trễ. Hỏi đúng nơi quan sát được thời gian chờ. Cần phân biệt số request được chờ, số lượt được chạy đồng thời và số lượt hoàn tất mỗi giây. Tự kiểm bằng cách giữ quota 4 vCPU, dự đoán kết quả nếu tăng limiter login từ 8 lên 16, rồi so p95 HTTP, tỷ lệ lỗi và mức chạm quota của cả login lẫn đổi ca.
- **Phản biện tiếp · 8/10.** Người dùng hỏi có còn tối ưu được code hay chỉ còn nâng máy. Câu hỏi phân biệt đúng hai nhóm can thiệp. Tự kiểm bằng cách so hai kịch bản trên cùng server, 500 lần xác minh mật khẩu mới và 500 lượt mở LMS trong đó 450 phiên còn hiệu lực. Đếm số lần bcrypt chạy và đo riêng độ trễ của thao tác đổi ca.
- **Phản biện tiếp · 9/10.** Người dùng yêu cầu giải thích cách hệ thống lớn chịu được đợt xác thực bắt buộc khi mọi người cùng vào, sau đề xuất đăng nhập trước giờ. Chỉ đúng chỗ đề xuất giảm tải chưa đáp ứng tình huống bắt buộc. Tự kiểm bằng cách đổi mục tiêu p95 2 giây cho 500 lượt đến dồn thành ít nhất 475 lượt hoàn tất trong 2 giây, rồi xác định tài nguyên nào phải được dành riêng và cấp sẵn trước giờ cao điểm.
