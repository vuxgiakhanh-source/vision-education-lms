# Lộ trình học để tự phát triển Vision Education LMS

Ngày lập: 17/10/2026. Mục tiêu: đọc hiểu code hiện có, tự làm được một chức năng
đi qua frontend, backend và database, rồi mở rộng thành hệ thống học toán.

Các bài tập dưới đây là kế hoạch học và triển khai đề xuất. Những quy tắc
sản phẩm chưa được người dùng chốt phải được ghi rõ, không tự coi là yêu cầu đã duyệt.
Không đặt lịch hoàn thành theo tuần khi chưa biết thời gian học và mức nền tảng.

## Cách đi qua lộ trình

- Chọn một mã việc mỗi buổi. Có thể học nhiều buổi cho cùng một việc.
- Chỉ đánh dấu xong khi giải thích được và làm được bài kiểm tra của việc đó.
- Nếu kẹt kiến thức nền, quay lại đúng mục nhỏ; không cần học hết mọi tài liệu trước khi thực hành.
- Ghi điểm dừng vào [WORKLOG](WORKLOG.md); dùng [CODE_GUIDE](CODE_GUIDE.md) tìm file.
- Git, debug và ghi chú thực hành xuyên suốt, không để đến cuối mới học.
- Trước khi sửa code do AI viết: tự xác định file, đầu vào, đầu ra và cách kiểm tra.
  Có thể nhờ AI giải thích hoặc review; sau đó tự kể lại và thử thay đổi nhỏ.

## Bản đồ kiến thức

| Kiến thức | Dùng vào đâu trong LMS? |
|---|---|
| HTML, CSS, Flexbox/Grid | Form, danh sách, bố cục và responsive |
| JavaScript, TypeScript | Xử lý sự kiện, dữ liệu API, kiểm tra kiểu |
| React | Ghép giao diện, trạng thái, lấy dữ liệu và điều hướng |
| HTTP | Hiểu request, response, mã lỗi và Bearer token |
| Python, OOP cơ bản | Model, service, repository và xử lý lỗi |
| FastAPI, Pydantic | Viết endpoint, kiểm tra đầu vào, phụ thuộc |
| SQL, MySQL | Quan hệ lớp/học sinh/bài nộp và truy vấn báo cáo |
| SQLAlchemy, Alembic | Làm việc với DB và lưu lịch sử thay đổi bảng |
| Auth và phân quyền | Chỉ cho đúng người truy cập đúng dữ liệu |
| Kiểm thử | Xác nhận điểm số, hạn nộp, quyền và lưu dữ liệu |
| Triển khai, log, backup | Đưa hệ thống cho người khác dùng và xử lý lỗi |

## Chặng 0 — lấy lại bản đồ dự án

**Đầu ra:** giải thích được phần nào là giao diện mẫu, phần nào đã gọi API.

- [ ] **L00.1** Đọc bảng hiện trạng trong CODE_GUIDE; tự mở được từng nhóm file.
- [ ] **L00.2** Theo dõi luồng đăng nhập từ `LoginForm` đến repository và quay về.
- [ ] **L00.3** Kể lại luồng đổi mật khẩu: ai xác định user, chỗ nào lưu hash,
  chỗ nào bỏ cờ `must_change_password`.
- [ ] **L00.4** Tìm trong dashboard nơi lấy tên, điểm, lịch; giải thích vì sao
  chúng không đổi khi database thay đổi.
- [ ] **L00.5** Tự chạy frontend; nếu môi trường backend sẵn sàng, chạy API và
  kiểm tra `/docs`. Ghi riêng lỗi cấu hình nếu chưa kết nối DB được.

**Tự kiểm tra:** không nhìn tài liệu, chỉ ra được ba đường dẫn HTTP hiện tại
(`/login`, `/me`, `/change-password`), mục đích từng đường dẫn và file xử lý.
Chặng này không yêu cầu xây thêm module mới.

## Chặng 1 — đọc và sửa được frontend hiện tại

**Cần học:** hàm, object/array, destructuring, `map/filter`, module import/export,
Promise, `async/await`, `try/catch`; TypeScript `type/interface`, optional field,
union và kiểm tra null. React: props, state, event, render, `key`, form,
`useEffect` và cleanup; CSS: box model, Flexbox, Grid, breakpoint, overflow.

- [ ] **L01.1** Đọc `TaskListCard`: giải thích props, `tasks.map` và callback.
- [ ] **L01.2** Viết bộ lọc nhiệm vụ mẫu theo trạng thái trong một bài thực hành
  nhỏ; không thêm tính năng sản phẩm khi chưa chốt hành vi.
- [ ] **L01.3** Dựng danh sách có trạng thái đang tải, rỗng và lỗi bằng dữ liệu mẫu.
- [ ] **L01.4** Giải thích tại sao đổi một biến thường không tương đương cập nhật state.
- [ ] **L01.5** Đọc tab Network/Console; tìm đúng request, payload và response.

**Tự kiểm tra:** tự thêm được một trường hiển thị từ type → dữ liệu → component;
giải thích được khi nào dùng state, khi nào tính trực tiếp từ props.
Phân biệt kiểm tra kiểu TypeScript với xác thực dữ liệu nhận từ mạng.

## Chặng 2 — Python, OOP và HTTP qua module auth

**Cần học:** list/dict, hàm, exception, type hint, module, class/object,
`self`, `__init__`, composition; GET/POST/PUT, JSON, header và HTTP status.
Đọc được `Session`, `Depends`, schema Pydantic và luồng tạo/đóng Session.

- [ ] **L02.1** Vẽ LoginService sử dụng LoginRepository như thế nào.
- [ ] **L02.2** Chỉ ra nơi schema kiểm tra kiểu, service kiểm tra nghiệp vụ,
  router đổi exception thành phản hồi HTTP.
- [ ] **L02.3** Giải thích vì sao kiểm tra form frontend không thay thế backend.
- [ ] **L02.4** Dùng `/docs` và Network kiểm tra đăng nhập đúng/sai, thiếu token,
  token không hợp lệ; ghi kết quả thực tế, không đoán status từ giao diện.
- [ ] **L02.5** Viết repository giả cho một bài kiểm thử LoginService;
  hiểu vì sao có thể kiểm thử nghiệp vụ mà không kết nối MySQL.

**Tự kiểm tra:** phân biệt xác thực danh tính với kiểm tra quyền; giải thích
JWT không phải chỗ lưu mật khẩu. Biết viết một service nhỏ và truyền dependency
vào, không phải tạo cây kế thừa cho mọi vai trò.

## Chặng 3 — SQL và thiết kế lớp học

**Cần học trước ORM:** SELECT, INSERT, UPDATE, DELETE; WHERE, JOIN, GROUP BY;
primary key, foreign key, UNIQUE, quan hệ nhiều-nhiều, transaction và rollback.
Sau đó học model/relationship, truy vấn SQLAlchemy và migration Alembic.

- [ ] **L03.1** Vẽ dữ liệu đề xuất cho lớp, người dùng và thành viên lớp.
  Chốt giáo viên/trợ giảng được gán theo lớp như thế nào.
- [ ] **L03.2** Tự viết SQL lấy học sinh thuộc một lớp và lớp của một học sinh.
- [ ] **L03.3** Chốt cách ngăn thêm một học sinh vào cùng lớp hai lần.
- [ ] **L03.4** Thiết kế migration và kiểm tra trên DB phát triển có thể tạo lại.
- [ ] **L03.5** Làm một lát cắt nhỏ: tạo lớp → xem danh sách lớp qua API → UI.

**Tự kiểm tra:** tải lại trang vẫn thấy dữ liệu; API từ chối dữ liệu không hợp lệ;
giải thích được JOIN và vì sao transaction không nên commit giữa một nghiệp vụ dang dở.

## Chặng 4 — nối tài khoản thật và phân quyền

**Cần học:** trạng thái đăng nhập, dữ liệu người dùng hiện tại, 401/403,
token hết hạn, route guard, kiểm tra quyền và quan hệ thành viên ở backend.

- [ ] **L04.1** Lấy hồ sơ từ `/me`, thay tên người dùng mẫu trên dashboard.
- [ ] **L04.2** Chốt và xử lý trạng thái đang tải, token lỗi/hết hạn, bị khóa,
  bắt đổi mật khẩu và đăng xuất; tránh vòng lặp chuyển trang.
- [ ] **L04.3** Bảo vệ route thật; giữ đường preview giao diện riêng để kiểm tra.
- [ ] **L04.4** Viết bảng quyền admin/teacher/teaching_assistant/student theo lớp.
- [ ] **L04.5** Backend kiểm tra quyền với từng endpoint lớp, không dựa vào việc ẩn nút.

**Tự kiểm tra:** học sinh không đọc dữ liệu lớp khác bằng cách thay id trong URL;
giáo viên không tự sửa lớp không được phân công; việc có token không đồng nghĩa
được phép thực hiện mọi hành động.

## Chặng 5 — hoàn thành một luồng giao/nộp/chấm bài

**Cần học:** thiết kế trạng thái, validation nghiệp vụ, thời gian/múi giờ,
transaction, xử lý gửi lặp, phân trang/lọc và upload nếu đã chọn nộp file.

- [ ] **L05.1** Chốt phạm vi loại bài đầu tiên; chọn nội dung văn bản hoặc file,
  không tự làm tất cả loại bài cùng lúc.
- [ ] **L05.2** Chốt hạn nộp, nộp muộn, thay bài, nộp lại, công bố điểm và sửa điểm.
- [ ] **L05.3** Thiết kế lớp bài tập, bài nộp, kết quả; đặt quy tắc trạng thái rõ ràng.
- [ ] **L05.4** Cô tạo nháp và giao cho lớp → học sinh mở và nộp → cô chấm → học sinh xem.
- [ ] **L05.5** Tính danh sách nhiệm vụ trên dashboard từ dữ liệu thật.
- [ ] **L05.6** Kiểm tra mất mạng, gửi hai lần, quá hạn và truy cập bài của người khác.

**Tự kiểm tra:** thao tác qua hai tài khoản khác nhau; tải lại trang vẫn đúng;
không đánh dấu nộp thành công khi server chưa xác nhận; điểm và phản hồi thuộc
đúng bài nộp. Nếu có file: kiểm tra quyền tải, giới hạn dung lượng và loại file.

## Chặng 6 — lịch, điểm danh, tài liệu và kiến thức tuần

**Cần học:** mô hình buổi học, thời gian hiển thị và thời gian lưu, lịch lặp nếu
thực sự cần, tính toàn vẹn dữ liệu, quyền truy cập tài liệu và truy vấn tổng hợp.

- [ ] **L06.1** Tạo buổi học, đổi lịch và xem lịch theo lớp/ngày.
- [ ] **L06.2** Điểm danh một học sinh một buổi đúng một bản ghi, có lịch sử chỉnh nếu cần.
- [ ] **L06.3** Đăng tài liệu/tóm tắt theo lớp hoặc tuần, kiểm tra quyền xem/tải.
- [ ] **L06.4** Gắn sự kiện lịch và tài liệu mới thật vào dashboard.
- [ ] **L06.5** Nếu thêm thông báo, bắt đầu với danh sách đã đọc/chưa đọc;
  chỉ thêm realtime sau khi việc phát sinh và nhận thông báo đã chạy đúng.

**Tự kiểm tra:** một lớp đổi lịch không đổi lớp khác; học sinh xem đúng giờ;
tài liệu nháp không lộ cho người chưa được xem.

## Chặng 7 — luyện thi toán

**Cần học:** cấu trúc câu hỏi/đáp án, công thức toán, lưu lượt làm, lưu tiến độ,
deadline phía server, chấm điểm có kiểm thử, phiên bản đề và công bố lời giải.

- [ ] **L07.1** Chọn một dạng câu hỏi đầu tiên; chốt cách chấm trước khi làm UI.
- [ ] **L07.2** Xây ngân hàng câu hỏi với chuyên đề/mức độ và lời giải.
- [ ] **L07.3** Tạo đề → bắt đầu lượt làm → lưu câu trả lời → nộp → chấm → xem kết quả.
- [ ] **L07.4** Kiểm tra refresh/mất mạng/hết giờ; server quyết định thời hạn,
  không chỉ tin đồng hồ trên trình duyệt.
- [ ] **L07.5** Thêm dạng câu hỏi tiếp theo; dùng đa hình/strategy khi các bộ chấm
  cần giao diện chung, không áp dụng chỉ để đủ bốn đặc tính OOP.
- [ ] **L07.6** Chốt đề/câu hỏi đã sửa ảnh hưởng lượt làm cũ thế nào;
  khi trộn đáp án, vẫn ánh xạ và chấm đúng đáp án gốc.

**Tự kiểm tra:** cùng một bài nộp không bị chấm thành nhiều kết quả khác nhau;
không trả đáp án chưa công bố trong payload cho học sinh. Không suy đoán quy tắc
chấm của kỳ thi cụ thể; xác nhận yêu cầu trước khi triển khai.

## Chặng 8 — báo cáo có ích cho cô và học sinh

**Cần học:** GROUP BY, mẫu số thống kê, lọc lớp/thời gian, tránh truy vấn lặp,
chỉ mục theo truy vấn thực tế và giải thích kết quả từ dữ liệu nguồn.

- [ ] **L08.1** Sổ câu sai từ lượt làm thật; học sinh làm lại và xem lời giải.
- [ ] **L08.2** Báo cáo theo chuyên đề, câu lớp sai nhiều, bài chưa nộp.
- [ ] **L08.3** Chốt điểm trung bình tính từ đâu, trọng số gì, có tính bài chưa chấm không.
- [ ] **L08.4** Đề xuất bài ôn theo quy tắc rõ ràng từ kết quả thật.
- [ ] **L08.5** Đối chiếu từng chỉ số với vài bản ghi mẫu có thể tính bằng tay.

**Tự kiểm tra:** không kết luận một em yếu chỉ vì một câu; hiển thị đủ ngữ cảnh
số câu/lượt làm; giáo viên chỉ xem báo cáo trong phạm vi được giao.

## Chặng 9 — kiểm thử và đưa cho một lớp dùng thử

Kiểm thử đã bắt đầu từ các chặng trước. Chặng này tổng hợp các luồng cốt lõi.

**Cần học:** kiểm thử đơn vị/tích hợp, môi trường test độc lập, biến môi trường,
build, migration khi phát hành, HTTPS, log, backup và phục hồi; Git branch/commit/review.

- [ ] **L09.1** Tự động kiểm tra quyền, tính điểm, hạn nộp và lưu bài bằng dữ liệu test.
- [ ] **L09.2** Kiểm tra luồng cô giao → học sinh nộp → cô chấm → học sinh xem.
- [ ] **L09.3** Thiết lập kiểm tra build/lint/test khi đưa code lên kho.
- [ ] **L09.4** Chạy staging, migration và thử phục hồi từ backup trên môi trường thử.
- [ ] **L09.5** Cho một nhóm dùng thử; ghi lỗi có bước tái hiện, ưu tiên sửa trước khi mở rộng.

**Tự kiểm tra:** người khác làm theo README chạy được dự án; có cách phát hiện lỗi,
khôi phục dữ liệu và trở lại bản ổn định khi cần. Test không ghi vào DB đang dùng thật.

## Kiến thức học khi có nhu cầu thực tế

- WebSocket: khi làm hỏi đáp/chat trực tiếp và đã có API, quyền, lưu tin nhắn.
- Hàng đợi/background job: khi có tác vụ lâu hoặc cần retry ngoài request.
- AI: sau khi dữ liệu và quy tắc học tập cơ bản đã rõ; vẫn cần cách đánh giá kết quả.
- Thiết kế hệ thống phân tán: khi một yêu cầu cụ thể vượt khả năng cấu trúc hiện tại.

Giữ React/TypeScript và FastAPI/SQLAlchemy đang dùng để hoàn thành các chặng.
Việc học lại một framework khác có thể xem xét khi có yêu cầu rõ ràng.

## Tài liệu để tra theo từng chặng

Các trang chính thức đã mở kiểm tra khi lập lộ trình. Chọn phiên bản tài liệu
phù hợp môi trường đang cài; đọc mục cần dùng, không cần đọc toàn bộ trước.

| Nguồn | Phần nên đọc |
|---|---|
| [MDN JavaScript Guide](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide) | Objects, functions, arrays, modules, Promises và xử lý lỗi |
| [React Learn](https://react.dev/learn) | Component, props, state, events, quản lý state |
| [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html) | Kiểu dữ liệu, object, union và narrowing |
| [Python Tutorial](https://docs.python.org/3/tutorial/) | Hàm, module, exception và class |
| [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/) | Request/response, validation, dependencies và security |
| [MySQL Tutorial](https://dev.mysql.com/doc/refman/8.0/en/tutorial.html) | Tạo bảng và truy vấn dữ liệu |
| [SQLAlchemy ORM Quick Start](https://docs.sqlalchemy.org/en/20/orm/quickstart.html) | Model, Session, query, relationship và transaction |
| [pytest Getting Started](https://docs.pytest.org/en/stable/getting-started.html) | Assertion, exception và fixture |

## Lần học tiếp theo: L00.2

1. Mở `LoginForm.tsx`, tìm `onSubmit`.
2. Mở `loginService.ts` frontend, tìm payload thực tế gửi đi.
3. Mở `axios.ts`, chỉ ra base URL và cách gắn token.
4. Mở router → service → repository backend của login.
5. Quay về form, chỉ ra nơi lưu token và quyết định trang tiếp theo.
6. Đóng code, tự viết lại sơ đồ luồng; ghi chỗ chưa hiểu vào WORKLOG.

Kết thúc bài khi tự trả lời được: dữ liệu đi đâu, đổi tên ở đâu, lỗi phát sinh
ở đâu, ai tạo token và ai điều hướng. Sau đó mới chuyển mã việc tiếp theo.
