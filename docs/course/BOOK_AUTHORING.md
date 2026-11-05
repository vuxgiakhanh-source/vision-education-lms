# Duy trì sách HTML

File để đọc: [GIAO-AN-LMS.html](GIAO-AN-LMS.html). Chỉ cần file này khi chuyển
sách sang máy khác. HTML/CSS/JavaScript và toàn bộ bài học được nhúng sẵn;
không có font/CDN, analytics hoặc tải nội dung từ mạng khi mở sách.

## Sửa nội dung ở đâu?

- `course-path.json`: đường học chính, G0–G6, các chặng, mốc chính và allowlist
  source studio. Build xếp 14 bài chính trước, còn lại thành thư viện chuyên đề;
  giữ id cũ để bảo toàn ghi chú. Bài chính có reference links theo ngữ cảnh.
- `studio/`: source nhỏ G1/G2/G3, đáp án patch G4 và điểm danh/review G5/G6.
  Chỉ thêm file cần giao cho người học vào sources; không quét thư mục tạm
  kiểm patch, node_modules, venv, DB, accounts hoặc results. ZIP offline giữ
  cây course với bài Markdown/source workshop/studio đã chọn, không lồng HTML
  vào chính ZIP. Verifier đối chiếu bytes, hash, tên file và danh sách nguồn.
- Các file Markdown của chương: bài giảng đầy đủ, code, bài tập, gợi ý/đáp án.
- `study-guide.json`: ba ưu tiên được viết riêng cho đủ 41 bài; guidance theo
  index mục S0 và 11 drill có starter/output/biến/bảng vết/gợi ý. Đáp án dùng
  kiểm lúc soạn; UI chỉ mở gợi ý. Không tự đánh dấu mastery khi output khớp.
- `study-focus.json`: bài mổ xẻ cú pháp và trách nhiệm cho mỗi lesson id;
  mẫu ngắn, từng token/ý nghĩa, quy tắc, lỗi dễ sai, bài tự viết và câu đổi
  yêu cầu. Mẫu một dòng có thể cần context, không hứa là file chạy độc lập.
- `project-knowledge.json`: nhóm kiến thức, mức cần dùng, ứng dụng cụ thể,
  lý do, bằng chứng và target lesson/tiêu đề mục. Builder đòi match đúng một
  mục; tránh prefix G4.1 khớp nhầm G4.10, viết đầy đủ dấu phân cách.
  Mỗi bài phải có liên hệ dự án. Nhãn xuất hiện trong cả read và learn;
  atlas dẫn đúng step. Nội dung target không được suy module đã có từ đề bài.
- `study-coach.js`: kiểm output/giá trị cuối/chuỗi giá trị của drill từ bounded
  interpreter. Không eval/Function, không chấm hiểu biết hay toàn bộ project.
- `book-content.json`: câu hỏi mở đầu, bản chất, ba bước tư duy, lỗi dễ nhầm,
  bài tự viết, câu hỏi trắc nghiệm, thẻ nhớ, nhóm, prerequisite và đầu ra mỗi bài.
- `advanced-content.json`: 6 bài P0–P5 và 6 mốc M12–M17, nối sau catalog/lộ trình
  nền khi build. Giữ id bài/câu/term cũ để bảo toàn ghi chú, đáp án và thẻ ôn.
- `beginner-content.json`: S0, ví dụ3 dòng và mốc cú pháp trước các mốc hệ thống.
  Build xếp JavaScript trước bài thuật toán thinking và chỉnh prerequisite,
  giữ nguyên id/quiz/thẻ cũ. Không đổi id để đổi thứ tự học.
- `frontend-path.json`: F0–F2 và các mốc cho nền Python, ghép trước phần còn lại;
  JavaScript yêu cầu F0, CSS chi tiết yêu cầu F1. S0 là ôn tùy chọn, không yêu
  cầu đọc lại biến từ số0 cho người đã biết Python.
- `api-guide.json`: phiếu tra tên/nguồn/signature/input/output/tác dụng/lỗi,
  ví dụ và link chính thức. Các phiếu chỉ hiển thị code, không chạy request.
  Bổ sung API theo nhu cầu thực, kiểm AST/Python và parse snippet JS/TS khi sửa.
- `syntax-lab.js`: parser/interpreter giới hạn cho S0, không eval/Function.
  Thêm cú pháp cần giữ lời giải thích giới hạn đồng bộ, test đối chiếu JavaScript
  cho phần được hỗ trợ; không tự nói nó chạy đủ ngôn ngữ.
- `teaching-content.json`: ví dụ giải thích từng dòng và sổ tra cú pháp.
  Mỗi ví dụ có `section` khớp một tiêu đề H2 của chương; `code` và `lines`
  phải có cùng số dòng, `trace` giữ cùng số cột, `predict` chứa câu hỏi/đáp án,
  `practice` có ba mức tự viết. Build highlight code và kiểm tra liên kết mục.
  `syntax` chứa token, tên, ý nghĩa, ví dụ và lỗi dễ nhầm.
- `learning-path.json`: 12 mốc/36 tiêu chí và yêu cầu biến thể/bằng chứng. Không
  tự chấm code; người học tự đánh dấu sau thực hành.
- `book-models.js`: các mô hình thuần dùng cho mô phỏng; kiểm tra bằng Node.
- `book.js`: điều khiển sách, ghi chú, tìm kiếm, quiz và giao diện mô phỏng.
  CSS lab tạo srcdoc sandbox không script/mạng từ HTML cố định và CSS allowlist;
  sổ API dùng text đã escape. Giữ các ranh giới này khi thêm điều khiển.
- `book.css`: bố cục đọc, responsive, nền tối và bản in.
- `build_book.py`: ghép bài học, highlight code và nhúng các file nguồn được
  liên kết rõ trong CODE_GUIDE. Không đọc file môi trường/bí mật.
  Source deploy/perf của xưởng chỉ nhúng theo danh sách tên cụ thể; không quét
  backups, accounts.json, DB hoặc results. Sau thêm file source, cập nhật cả
  danh sách allowlist và verify_book. Lockfile frontend được nhúng để tái lập lab.

Không sửa tay file HTML đã sinh; sửa nguồn rồi build lại để tránh mất thay đổi.
Trong ô bảng Markdown, pipe là dấu chia cột ngay cả khi ở inline code. Viết
HTML code với entity số &#124; nếu cần hiển thị toán tử pipe trong ô; cách
này giữ dấu đúng và không lộ backslash với bộ render hiện tại. verify_book
kiểm số cột và số bảng đã render để bắt bảng rơi thành chữ.
Các đoạn code dự án nhúng trong sách là snapshot tại lần build, không cập nhật
tự động khi code sản phẩm thay đổi. Khi sửa flow đăng nhập, kiểm tra cả bài mẫu
và mô phỏng tương ứng.

## Build và kiểm tra

Từ thư mục gốc repo, dùng system Python hiện có `mistune` và `pygments`:

```powershell
python docs/course/build_book.py
python docs/course/verify_book.py
node --check docs/course/book.js
node --check docs/course/book-models.js
node docs/course/examples/book-models.test.cjs
node docs/course/examples/book-runtime.test.cjs
node docs/course/examples/teaching-examples.test.cjs
node docs/course/examples/perf-script.test.cjs
node docs/course/examples/syntax-lab.test.cjs
node docs/course/examples/study-coach.test.cjs
.\.venv\Scripts\python.exe -m unittest discover -s docs/course/examples -p test_teaching.py -v
node docs/course/verify_sources.cjs
python -m unittest discover -s docs/course/studio/backend -p test_use_cases.py -v
.\.venv\Scripts\python.exe -m unittest discover -s docs/course/studio/attendance -p "test_*.py" -v
.\.venv\Scripts\python.exe -m unittest discover -s docs/course/workshop -p test_workshop.py -v
.\.venv\Scripts\python.exe -m unittest discover -s docs/course/workshop -p "test_*.py" -v
```

Hai gói Python chỉ dùng lúc soạn/build, không cần ở máy người đọc. Venv backend
hiện tại không chứa hai gói này; không thêm chúng vào dependency sản phẩm.

Khi cần bản localhost, phục vụ trực tiếp thư mục `docs/course` bằng HTTP server
chỉ bind `127.0.0.1`. Có thể mở trực tiếp file HTML; nếu dùng localhost, dùng đúng cổng server
đang chạy. Không cần copy sách vào frontend. Server chỉ phục vụ tài liệu, không phải một chức năng sản phẩm.

Build tách bài tại các H2 để tạo chế độ học từng bước; nội dung trước H2 đầu
được đặt tên “Trước khi bắt đầu”. Giữ id bài để bảo toàn ghi chú. Vị trí đọc là
index mục: khi sắp lại H2, vị trí cũ có thể chuyển ý; runtime chặn index quá phạm vi.

Sau thay đổi cần thử: điều hướng chương, đọc bài dài/code/bảng, câu hỏi sau khi
đổi lựa chọn, mô phỏng đã sửa, tìm kiếm, lưu rồi tải lại ghi chú, desktop/mobile
và chế độ tối. Phần kiểm tra đã làm được ghi ở [VALIDATION](VALIDATION.md).

Nút In/PDF mở hộp thoại trình duyệt; người đọc chọn máy in hoặc Save as PDF.
Không có PDF dựng sẵn kèm lần phát hành này. Bản in gồm bài đọc và lời giải;
các thao tác tương tác cần dùng bản HTML.

`verify_sources.cjs` dùng compiler/dependency hiện có ở frontend để parse snippet
và kiểm kiểu strict source frontend xưởng. Không cài package của xưởng khi
chạy kiểm tra này. `book-runtime.test.cjs` dùng DOM double cho template/state,
không xác minh layout,accessibility hoặc hành vi browser/file-origin.

Các id bài gốc và storage key được giữ khi mở rộng. Không đổi id để sắp lại
chương vì làm mất liên hệ ghi chú cũ; đổi order trong catalog. Schema lưu mới
thêm skills/evidence; import chỉ nhận id/kiểu đã biết. Source xưởng được nhúng
từ danh sách file cụ thể, không quét DB/env/node_modules hoặc dữ liệu học.


## Nhấn đúng kiến thức quan trọng

Dùng blockquote marker `[!KEY]`, `[!TASK]`, `[!CHECK]`, `[!NOTE]`,
`[!WARNING]` cho ý nhớ, bài tự viết, cách kiểm, cơ chế và chỗ dễ sai. Các đoạn
bắt đầu bằng nhãn in đậm Đích/Tự làm/Đầu ra/Nếu kẹt cũng có style riêng.
Không bọc mọi đoạn thành callout. Project relevance lấy từ bản đồ được soạn
rõ, không tự suy tầm quan trọng bằng từ khóa. Mã giảng hơn 18 dòng trong ngôn
ngữ ứng dụng thu gọn thành đối chiếu; lệnh môi trường vẫn đọc trực tiếp.
Không thêm nút copy vào luồng bài giảng. Giữ nền trắng/xám + xanh dương,
nhãn có chữ và trạng thái focus rõ, layout chuyển một cột ở màn hẹp.
