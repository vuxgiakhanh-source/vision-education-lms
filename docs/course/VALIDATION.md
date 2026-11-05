# Kiểm tra lần chỉnh 22/10/2026

- Đủ 41 bài có Cần nhớ/Phải tự làm/Cách kiểm, bài mổ xẻ cú pháp và trách
  nhiệm, ô nháp code/thiết kế; giữ id bài và storage key cũ.
- Bản đồ 29 nhóm kiến thức có 3 mức, liên hệ ứng dụng trong LMS, bằng chứng
  và link đến đúng mục. Builder/verifier kiểm match duy nhất và đủ mọi bài.
  Nhãn DÙNG TRONG DỰ ÁN có ở cả học từng bước/toàn bộ bài.
- Bổ sung giải thích F0 (cú pháp từ Python, destructuring/spread/import),
  02 (generic/Promise/Axios/narrowing), 04 (LoginForm), G4.10 (stack thật,
  trạng thái repo, trách nhiệm, transaction, import và nhiều request).
- Build HTML/ZIP và verifier qua: 41 bài, 162 quiz, 123 thẻ, 116 source,
  102 bảng Markdown render đúng. Tài nguyên offline, source hash và ZIP khớp.
- 133 snippet JS/TS/TSX parse qua; 13 file frontend xưởng strict type-check
  qua. Đây không phải bằng chứng mọi snippet có đủ context để chạy độc lập.
- 11 drill S0: đáp án, lỗi cú pháp, bài trống, chỉ in đáp án, biến cuối và
  thứ tự giá trị được kiểm; bounded interpreter không eval/Function.
- Runtime DOM double: 164 view bài + atlas/filter/link step, draft lưu/reload,
  escape HTML, feedback đổi khi sửa code, giữ ghi chú cũ. Kết quả drill không
  tự đánh dấu lesson hoàn thành. CSS được parse bằng Lightning CSS, 0 warning.
- **Chưa kiểm trực quan giao diện mới bằng trình duyệt trong lần sửa này**;
  các kiểm template/CSS không chứng minh layout/pixel, screen reader hoặc
  hành vi file-origin trong trình duyệt. Các ghi nhận browser bên dưới là
  của những lần trước, không dùng xác nhận giao diện vừa đổi.
- Không chạy đo tải/MySQL/production, migration/restore thật; không có công
  bố capacity hoặc chứng nhận người học chỉ từ việc đọc giáo án.

---

# Kiểm tra giáo án và ví dụ

Ngày: 17/10/2026. Phạm vi: tài liệu và ví dụ tham chiếu của khóa học, không phải
nghiệm thu toàn bộ chức năng Vision Education LMS.

## Đổi bảng màu theo lựa chọn người học — 18/10/2026

- Người học chọn trắng/xám và xanh dương. Đã đổi palette trong CSS nguồn,
  gồm nền/sidebar/card, nút/selection/focus, bảng, inline code và code block.
  Các nền đọc là trắng/xám; xanh dương tập trung vào hành động/trạng thái chọn.
- Chế độ tối dùng slate/navy với cùng hệ màu xanh dương. Kiểu chữ tiếng Việt,
  khoảng dòng và cấu trúc bảng đã sửa ở các lượt trước được giữ trong nguồn.
- Kiểm parse CSS, độ tương phản các cặp chữ/nền chính và đóng gói HTML được
  chạy lại. Chưa có ảnh xác nhận hiển thị thực tế cho palette mới.

## Sửa bảng hiện thành chữ thô — 18/10/2026

Ảnh người học cho thấy bảng ký hiệu trong chương22 không được dựng thành
table. Nguyên nhân là pipe trong code `|` và `||` bị hiểu thành dấu chia cột.
Đã biểu diễn pipe bằng HTML entity trong3 ô ở2 bảng thuộc chương19/22.
Bộ kiểm mới so số cột của từng hàng
Markdown và đối chiếu số bảng nguồn với số table HTML, cho mọi bài và source
Markdown nhúng. Ký hiệu trong HTML vẫn là pipe/operator thật, không lộ escape.
Phép kiểm bắt lại bản nguồn lỗi khi phục hồi pipe thô trong bộ nhớ; không cần dựa
vào kiểm đóng gói thành công để suy rằng Markdown đã được render đúng.

## Sửa lỗi tiêu đề theo ảnh người học — 17/10/2026

Ảnh người học cho thấy dấu ở chữ “thống” bị tách/vỡ khi dùng Georgia italic.
Đã bỏ kiểu serif nghiêng riêng ở tiêu đề, dùng cùng font sans như phần chữ
đang hiển thị đúng; giảm ép khoảng chữ và tăng chiều cao dòng. Build/CSS và
runtime checks xác nhận bản nguồn đã cập nhật; chưa có ảnh xác nhận sau sửa.

## Xây lại đường học và giao diện — bản hiện tại 17/10/2026

- Đường chính gồm14 bài: G0, F0/F2/F1, G1–G6 rồi P2–P5. Có27 chuyên đề
  tra cứu; giữ toàn bộ id/ghi chú cũ. G0–G6 có63 buổi H2, dự án từ thư mục
  trống, lời giải trước/sau khi tách, bài giảm gợi ý, tự làm và review.
- Sách41 bài,162 câu,123 thẻ;28 mốc/84 tiêu chí,13 mốc chính và15 mốc bổ
  sung.116 source nhúng gồm39 file studio theo allowlist. ZIP offline có
  source/tài liệu đã chọn, không có dependency cài sẵn/DB/secret/data riêng.
- G1/G2 có cùng Sổ lớp ở DOM và React. React strict+Vite build qua; fixture
  JS/TS kiểm query hoa/thường/khoảng trắng, list rỗng/không khớp, input giữ
  nguyên và biên tên100/101. Chưa suy từ đó thành kiểm browser UI đầy đủ.
- G3 có9 test qua. Điểm danh G5 có12 test qua; review/chuyển miền G6 có10
  test qua. Bản review sai cố ý exit1 với20.0 khác66.67; bản sửa exit0.
- Patch archive áp trên bản copy sạch có33 test qua/2 MySQL skip; đáp án
  tách feature có26 qua/2 skip. Hai suite dùng chung nhiều regression,
  không cộng để công bố số test độc lập. Frontend archive strict/build qua.
  Các bản copy kiểm không được nhúng hoặc đưa vào ZIP.
- Verifier kiểm đóng gói offline, id/route/prerequisite, AST Python, nguồn
  studio có thể mở trong sách, hash source, ZIP bytes/CRC/safe path và
  loại trừ dependency/DB/secret.110 snippet JS/TS/TSX parse,13 file FE
  workshop/studio strict qua. Đây không phải chạy mọi snippet trong browser.
- Runtime DOM double kiểm164 view theo4 chế độ, mọi mục G0–G6, pager
  chính/tham khảo, home/path, mở mục qua liên kết, Escape/resize menu,
  Blob ZIP, lưu/khôi phục tiến độ cũ và escaping.15 mô hình học, bộ luyện
  cú pháp và các worked JS/TS examples qua kiểm tra riêng.
- Giao diện mới có home/chặng/tiếp tục, thư viện thu gọn, reading sheet,
  code14px desktop/13px mobile, tab mobile2×2 và focus menu. CSS parse
  không warning; đã tính tương phản các cặp màu chữ/nền chính ở sáng/tối
  và sửa màu chữ phụ trên sidebar/nền nhạt. Chưa coi đây là audit a11y đầy đủ.

**Giới hạn lần này:** công cụ trình duyệt từ chối quyền quan sát URL localhost.
Chưa xác minh bằng thao tác/screenshot thực tế bố cục mới ở các viewport,
keyboard/screen reader, bản in/PDF, clipboard, tải ZIP và file-origin storage.
Runtime/CSS checks giúp bắt lỗi source và trạng thái, không thay kiểm layout.
Các kết quả browser ở mục lịch sử bên dưới thuộc giao diện trước lần xây lại.
MySQL đồng thời, Docker deployment, restore và capacity thực vẫn chưa có số
đo nghiệm thu; script/cấu hình tồn tại không chứng minh đã chạy môi trường đó.

## Điều chỉnh theo nền Python người học — lịch sử trước bản xây lại

- Người học xác nhận biết cú pháp Python/biến/if/for/hàm, chưa tự viết JS, chưa
  biết TS/CSS và hay vướng API/tool. Thêm F0 đối chiếu Python→JS→TS, F1 HTML/
  CSS từ đầu, F2 đọc signature/import/input/output/tác dụng. S0 thành ôn tùy
  chọn; không gắn việc chưa biết frontend với chưa biết lập trình nói chung.
- Home/mục lục đưa F0–F2 lên đầu, mốc frontend/CSS trước các mốc hệ thống;
  JavaScript chi tiết nhận F0 làm prerequisite, CSS nhận F1. Giữ id và notes cũ.
- Thêm12 phiếu tra API từ khối code, gồm Python string/dict/path/inspect,
  JS map, Axios/Zod/React, FastAPI/Pydantic/SQLAlchemy và CSS. Phiếu ghi rõ
  dùng khi nào, signature, input/output, tác dụng, lỗi, ví dụ và nguồn chính thức.
  Đây là bộ chọn lọc, không hứa đã liệt kê mọi API của mọi thư viện.
- Khung CSS dùng iframe sandbox chỉ có HTML/CSS, CSP chặn mặc định tài nguyên;
  điều khiển bằng allowlist block/flex, direction, padding/gap. Chưa hỗ trợ CSS
  tùy ý. Browser đã đo hai item từ block khác y thành flex cùng y với gap12px;
  đổi column/gap24/padding24 cho đúng vị trí/khoảng cách đo từ DOM. Trang không
  tràn ngang ở viewport thực828px. Chưa suy rộng thành mọi breakpoint.
- Browser đã mở F0 qua nút đầu, dùng Tra hàm/tool tìm strip và đọc đúng phiếu;
  xem ví dụ Python/JS qua từng mục. Không gọi HTTP/DB từ các phiếu.
- Sách34 bài,141 câu,102 thẻ,21 mốc/63 tiêu chí. Kiểm đóng gói/source hash,
  AST phiếu Python,79 snippet JS/TS/TSX,136 view runtime và7 file FE strict qua.
  Runtime còn kiểm đổi CSS theo allowlist, tra API và giữ notes/storage cũ.

Các mục sau là lịch sử trước lần xác nhận mức Python/JS/TS/CSS mới nhất.

## Sửa đường học cho người chưa biết cú pháp — mới nhất

- Thêm S0 giải thích từ console.log(2); đến số/chuỗi, let/const, gán/cập nhật,
  phép tính/so sánh, báo lỗi và bài tự gõ3–4dòng. Buổi đầu chỉ cần mục2–7;
  chưa yêu cầu đọc project, React, API hoặc nhiều ngôn ngữ cùng lúc.
- Home và mục lục đặt S0 trước; bài login chuyển sau nền/auth trong thứ tự đọc.
  JavaScript học trước bài thuật toán tổng hợp, tránh yêu cầu biết vòng lặp/hàm
  trước khi học cú pháp. Id/quiz/ghi chú/thẻ cũ giữ nguyên.
- Sửa đầu chương JavaScript: if đơn trước hàm, array/index/length trước for,
  hàm cộng1 trước hàm trung bình, object/thuộc tính trước callback/rút gọn.
  Mỗi ý có giải thích dấu mới, dự đoán và bài biến thể; phần chọn giá trị nâng
  hơn đặt trong mục mở thêm để không buộc học tất cả cùng lúc.
- Bộ luyện S0 có6 bài từ đổi một số đến ô trống, output và trace từng câu lệnh.
  Parser/interpreter tự viết chỉ hỗ trợ scalar, let/const, assignment, arithmetic,
  comparison và console.log một giá trị; bắt buộc ; trong bộ luyện. Chưa hỗ trợ
  if/loop/function/array/object hay JavaScript đầy đủ. Không dùng eval/Function,
  không thực thi code trên DOM/mạng. Draft chỉ giữ trong tab, không tự lưu.
- `syntax-lab.test.cjs` đối chiếu các chương trình hợp lệ trong tập hỗ trợ với
  JavaScript thật; kiểm thứ tự tính, string/số, trace7→8→8, const/gán lại, tên
  chưa có, thiếu nháy/ngoặc, duplicate declaration, giới hạn và mỗi lượt chạy mới.
- DOM double kiểm output/trace và escape HTML trong trace. Browser thực đã
  thử chọn bài, sửa/gõ ba dòng, output8/bảng biến đúng; thiếu nháy báo lỗi tiếng
  Việt, quay lại bài S0 từng mục được. Không tràn trang ở viewport thực755px;
  chưa suy rộng thành kiểm tất cả mobile/browser.
- Sách hiện31 bài,132 câu,93 thẻ,9 ví dụ giải thích từng dòng,19 mốc/57 tiêu chí.
  Kiểm đóng gói/links/hash/AST,124 view runtime và63 snippet JS/TS/TSX đã qua.
  Không chạy lại test sản phẩm/backend vì lần này chỉ đổi giáo án và UI sách.

Các mục dưới là lịch sử của phiên bản trước khi sửa đường học từ số0.

## Mở rộng P0–P5 — sản phẩm, clean code và vận hành

- Sách có 30 bài, 128 câu hỏi, 90 thẻ, 18 mốc/54 tiêu chí. Sáu bài mới có
  mục học nhỏ, ý chính, bài điền/trắng/sửa lỗi, quiz và sản phẩm cần nộp.
  Giữ id bài/câu/term và storage key cũ; mốc mới nối sau mốc cũ.
- Core loop tham chiếu đã thêm API/React/DB cho giao bài văn bản, nộp một bản
  cuối, chấm điểm nguyên0..10 và công bố/thu hồi hiển thị. Không có implementation
  đầy đủ mọi module LMS, login/refresh/reset production, upload hay job queue.
- Refactor ClassService nhận Transaction adapter thay gọi repository.db;
  composition root dùng cùng Session. Service vẫn dùng ORM model, không tuyên
  bố đã độc lập hoàn toàn framework.
- Bộ xưởng chạy 28 test: 26 qua và 2 MySQL concurrency skip vì chưa cấp DB riêng.
  Gồm8 acceptance tests workflow,17 test lớp/JWT/quyền và1 migration baseline
  upgrade/metadata/downgrade với SQLite trong bộ nhớ. Test lỗi sau flush kiểm
  lại bằng Session mới. Không chứng minh durability qua process hoặc locking MySQL.
- Chạy FastAPI tests ngoài sandbox Windows vì threadpool trong sandbox bị treo.
  Đổi SQLite test sang memory/StaticPool tránh lỗi Temp; cấu hình này chỉ dành
  cho tests tuần tự. Browser kiểm bằng SQLite file riêng, không dùng memory
  connection chung cho nhiều request đồng thời.
- Frontend lab đã npm ci với lockfile riêng, kiểm TS strict và Vite build.
  Compiler snippet kiểm47 đoạn JS/TS/TSX và7 file frontend xưởng. Package/libraries
  của sản phẩm không bị thay để thực hiện lab.
- Browser localhost đã thực hiện cô giao → học sinh nộp → cô chấm0 chưa công bố
  → học sinh không thấy điểm → cô công bố → refresh/nhập lại token học sinh thấy0.
  Đổi nội dung sau nộp nhận conflict, input giữ để sửa và bản gốc vẫn hiển thị;
  đổi sang người ngoài lớp xóa dữ liệu cũ và hiện lỗi scope. API/SQLite file
  riêng ở8003, frontend5175, tài khoản/secret giả dành riêng buổi kiểm.
- Rà browser tìm được form điểm không đồng bộ sau fetch; đã sửa key theo dữ
  liệu score/publish và kiểm input giữ0 sau lưu. Sáu bài mới đã mở ở chế độ đọc
  đầy đủ, H2/bảng/code render và không tràn toàn trang ở viewport desktop1280.
  Công cụ viewport không áp dụng được override mobile trong lượt này, nên không
  ghi đã kiểm lại mobile cho P0–P5. Kiểm mobile các bản trước nằm bên dưới.
- `verify_book.py` kiểm30 bài/128 câu/90 thẻ,18 mốc, source links/AST và SHA256
  từng source nhúng để phát hiện snapshot cũ. `book-runtime.test.cjs` kiểm120
  view bài học và54 tiêu chí, persistence/ghi chú cũ/escaping với DOM double.
- Script k6 có kiểm JSON/status/scope/owner/nội dung/điểm chưa công bố, threshold
  latency/lỗi/checks/dropped và chỉ cho localhost. Fake HTTP test đã kiểm các
  predicate từ chối response sai; đó không phải chạy k6 hay đo tải.
- Docker Compose config đã qua `config --quiet` bằng placeholder chỉ để validate.
  Docker Engine chưa chạy; không build/start image MySQL/Nginx/API, chưa chạy
  MySQL migration/concurrency, k6, backup/restore hay public staging/TLS.
  REPORT.md giữ CHƯA ĐO và không có capacity/user count được công bố.
- Có template CI, migration và runbook restore DB mới; CI chưa được kích hoạt
  trong repo sản phẩm. Image tags/Python transitive dependencies chưa lock hoàn
  toàn; cấu hình lab không phải xác nhận production hardening.

Lệnh chạy lại và giới hạn chi tiết: [README xưởng](workshop/README.md),
[deployment lab](workshop/deploy/README.md), [hướng dẫn soạn sách](BOOK_AUTHORING.md).
Các mục bên dưới là lịch sử kiểm trước lần mở rộng này, không thay kết quả mới.

## Bản học từng bước và giải thích từng dòng — mới nhất

- 24 bài có các mục học nhỏ được tách từ H2; giữ bản đọc đầy đủ và id cũ.
  HTML độc lập khoảng 2,9 MB, 52 tài liệu/source nhúng, 104 câu hỏi, 72 thẻ nhớ.
- Thêm 8 ví dụ bấm từng dòng tại đúng mục kiến thức, bảng theo dõi dữ liệu,
  câu hỏi dự đoán và ba mức thực hành; sổ tra 20 nhóm ký hiệu/cú pháp.
- `verify_book.py` kiểm đóng gói, mục học, mapping ví dụ/mục, số dòng giải thích,
  bảng trace, Python AST và liên kết. `verify_sources.cjs` kiểm cú pháp 47 snippet
  JS/TS/TSX và kiểm kiểu strict 5 file frontend xưởng.
- Runtime DOM double qua 96 view (24 × 4 chế độ), vị trí đọc/khôi phục/clamp,
  cập nhật giải thích theo dòng, 36 tiêu chí, ghi chú và storage bị chặn.
- Các kiểm tra JS ví dụ qua với dữ liệu/client giả. 4 unittest Python qua,
  gồm commit/rollback SQLAlchemy bằng SQLite trong bộ nhớ. Không suy rộng
  kết quả này thành kiểm thử MySQL hoặc request thật.
- Kiểm trực tiếp bản localhost cổng 8766: chọn mục, bấm dòng 4, mở bảng trace,
  mở đáp án dự đoán, tìm `=>` trong sổ cú pháp, khôi phục vị trí khi reload và
  khi chọn lại chương. Menu mobile mở/đóng sau khi chọn bài; nền tối hiển thị.
- Đã xem desktop 1536 × 1000, mobile 390 × 844 và 320 × 720. Không tràn ngang
  toàn trang ở hai cỡ mobile; code dài có vùng cuộn riêng. Rà mobile phát hiện
  tiêu đề ví dụ bị hẹp do cột gợi ý, đã chuyển gợi ý xuống dòng riêng ở ≤640px.
- Các kiểm tra browser ở đây dùng HTTP localhost; không mở được `file://`
  bằng công cụ browser. Chưa kiểm đầy đủ screen reader, PDF, nhiều trình duyệt,
  hoặc React frontend xưởng trong browser.

## Lần mở rộng trước đó theo mục tiêu tự xây hệ thống

- Hiện tại có 24 bài (23 bài chính + bài mẫu đăng nhập), 104 câu hỏi, 72 thẻ
  ôn, 11 mô phỏng; HTML độc lập khoảng 2 MB. Lộ trình 12 mốc có 36 tiêu chí
  tự đối chiếu, biến thể, sản phẩm nộp và ghi bằng chứng; không tự chấm code.
- `verify_book.py`: đóng gói/JSON/count/heading id/liên kết/prerequisite/
  milestone references và câu hỏi không lặp nguyên văn trong bài đã qua.
  Kiểm AST snippet Python và source xưởng; không nhúng env/DB/token thật.
- `verify_sources.cjs`: 43 snippet JS/TS/TSX được parse/transpile; 5 file
  TS/TSX frontend xưởng được kiểm kiểu strict với dependency frontend hiện có.
  Đây không phải runtime test mọi snippet hoặc clean install package xưởng.
- `book-runtime.test.cjs`: 72 view bài học (24 × 3 mode), path/home/review,
  36 tiêu chí, lưu bằng chứng, giữ id/ghi chú cũ, escape nội dung người học
  và storage bị chặn đã qua với DOM double. Không chứng minh layout/browser.
- `node --check` qua cho script sách. Chạy lại 15 nhóm model check, 24 assertion
  TypeScript và 28 unittest domain đã qua.
- Xưởng backend: 17 unittest qua FastAPI ASGI trong process + SQLite tạm.
  Kiểm JWT thiếu/sai/hết hạn/thiếu expiry, user không có/bị khóa, create/trim/
  persistence, schema lỗi, student không được tạo, list/detail/rename đúng
  scope, cô khác lớp, pagination/id dương, giới hạn Unicode 200/201 code point,
  FK/UNIQUE và rollback sau flush có lỗi. Không dùng DB sản phẩm hoặc TCP.
- Sandbox Windows chặn Temp trong lần thử đầu của tests SQLite; chạy lại
  ngoài sandbox với database tạm đã qua. Không đổi quyền/config DB sản phẩm.
- Chưa chạy frontend xưởng trong browser, MySQL/migration/concurrency hoặc
  phát hành thật. Source frontend qua kiểm kiểu; đó chưa phải bằng chứng
  Network/CORS/multi-account/refresh đã được nghiệm thu.
- Lần mở rộng này chưa kiểm trực quan lại: công cụ browser chặn URL file://
  đang mở vì chỉ cho http/https. Không dùng đường vòng để vượt chặn trang đó.
  Template/state được kiểm riêng bằng unit test. Các kiểm tra browser ở mục
  phía dưới thuộc bản trước lần mở rộng; ảnh book-preview.jpg cũng thuộc lần đó.

Giữ id bài gốc và storage key; thêm skills/evidence vào dữ liệu lưu. Những
câu hỏi mới nối sau câu hỏi cũ để giảm thay đổi key đáp án đã lưu. Không xóa
ghi chú khi cập nhật. Đọc sách hoặc tick tiêu chí không tự chứng minh năng lực;
người học cần tự thực hiện checkpoint và biến thể.

## Đã thực hiện

- 28 test unittest Python cho SubmitService, deadline, phạm vi lớp, tài khoản,
  chuẩn hóa nội dung, retry, giữ bản gốc, điểm 0 và parsing số đã qua.
- 24 assertion TypeScript cho lọc/đếm/cập nhật không sửa gốc, trung bình giữ 0,
  parse unknown và dữ liệu không hợp lệ đã qua.
- Compiler frontend đã kiểm tra strict hai file TypeScript ví dụ, không emit.
- 24 đoạn JS/TypeScript/TSX trong tài liệu đã được parse/transpile bằng compiler
  TypeScript đang cài. Đây là kiểm tra cú pháp/chuyển đổi, không phải chứng minh
  logic runtime của tất cả đoạn.
- 6 ví dụ React hoàn chỉnh trong chương 03–04 đã được kiểm tra kiểu strict với
  React/React Hook Form/Zod đang cài, bằng compiler host trong bộ nhớ.
- Các đoạn Python được kiểm tra cú pháp bằng AST; các mẫu schema được kiểm tra
  thêm với Pydantic đang cài. Đoạn minh họa truy vấn chưa được gọi đến MySQL.
- Liên kết file nội bộ và định dạng UTF-8 được rà sau khi viết tài liệu.

## Cách chạy lại các kiểm tra ví dụ

Xem lệnh cụ thể trong [examples/README](examples/README.md).
Không cần cài thêm gói để chạy unittest Python và các assertion TS với môi
trường Python 3.12/Node 24/TypeScript hiện có được ghi trong mục lục khóa học.

## Sách HTML: kiểm tra trước lần mở rộng

- Build được một file HTML khoảng 1,24 MB: 15 chương + bài mẫu, 32 câu hỏi,
  48 thẻ nhớ và 30 tài liệu/source được nhúng. Không có asset ngoài cần tải
  khi mở sách; liên kết tài liệu web chỉ mở khi người đọc chọn.
- `python docs/course/verify_book.py` đã kiểm tra đóng gói, JSON nhúng,
  số bài/câu/thẻ, heading id duy nhất và đích liên kết nội bộ.
- `node --check` đã qua cho `book.js` và `book-models.js`.
- `node docs/course/examples/book-models.test.cjs`: 15 nhóm kiểm tra qua cho
  login, tham chiếu, state queue, JOIN, transaction, quyền, deadline/retry,
  chuẩn hóa số, mẫu số báo cáo và ước tính viewport.
- Qua trình duyệt tại bản copy tạm do Vite phục vụ: mở đủ 16 bài đọc đầy đủ,
  hiển thị các khối code; thử các nhánh đăng nhập và từng dòng giải thích,
  copy nông/immutable, state queue, JOIN, rollback và retry sau hạn.
- Đã mở 11 màn mô phỏng; các model của chúng là mô hình thuần trong bộ nhớ.
  Không thực hiện SQL/HTTP sản phẩm hoặc chạy React renderer trong sách.
- Đã thử quiz sai/đúng, đổi lựa chọn để xóa feedback cũ, tìm kiếm không dấu,
  xem source nhúng, lật thẻ, và ghi chú còn sau khi reload. Kiểm tra menu mobile,
  bài code ở 390px, không tràn toàn trang ở 320px, chế độ tối ở 1366px.
  Không thấy console error trong lần rà này.
- Chưa xuất/kiểm tra PDF thành phẩm; nút In/PDF dùng trình duyệt. Chưa kiểm tra
  mọi tổ hợp màn hình, screen reader, nhập/xuất JSON qua nhiều trình duyệt hoặc
  hành vi lưu của từng trình duyệt khi mở `file://`. Storage có xử lý lỗi và có
  chức năng xuất ghi chú để người học giữ bản sao.

Cách duy trì và build lại: [BOOK_AUTHORING](BOOK_AUTHORING.md).

## Chưa xác nhận bằng lần kiểm tra này

- Cú pháp/hành vi SQL trên MySQL, migration thực tế, locking và request cạnh tranh.
- Login/JWT/quyền của các endpoint sản phẩm qua HTTP với database hiện tại.
- UI React trong trình duyệt, khả năng truy cập đầy đủ hoặc tích hợp API thật.
- Upload, WebSocket, email, backup, staging hoặc vận hành production.

Những phần trên có bài tập và tiêu chí kiểm tra trong các chương tương ứng.
Fake repository chỉ kiểm tra quy tắc thuần; không phải bằng chứng database
hoặc hệ thống triển khai đã đáp ứng mọi điều kiện.
