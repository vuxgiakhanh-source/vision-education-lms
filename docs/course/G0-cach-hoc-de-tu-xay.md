# G0 — Từ biết Python đến tự thiết kế dự án

Giáo án này dành cho mày: đã viết được biến, if, for và hàm Python; chưa tự
viết JavaScript, chưa biết TypeScript/CSS và còn vướng cách dùng thư viện.
Mình giữ phần tư duy đã biết, học thêm từng công cụ khi có một việc cần làm.

Đích học là tự nhận một yêu cầu, làm rõ quy tắc, chọn dữ liệu và chỗ đặt code,
viết, kiểm tra, rồi sửa khi yêu cầu đổi. Đọc hết sách chỉ là một hoạt động
trong quá trình ấy. Mỗi chặng dưới đây có sản phẩm và một lần tự làm để kiểm.


> [!KEY]
> Mày đang học để tự xây **Vision Education LMS học toán/luyện thi**, dùng
> React + TypeScript + Vite + Tailwind và Python/FastAPI + SQLAlchemy + MySQL
> + Alembic. Không cần thuộc tên toàn bộ thư viện trước; cần tự viết cú pháp,
> hiểu hợp đồng API và quyết định trách nhiệm của từng phần.

**Điểm xuất phát:** đã biết biến, if, for, hàm trong Python; chưa tự viết JS,
TS hoặc CSS. Đi F0 → F2 → F1, rồi tự dựng G1. Các phần TS/React học tiếp ở G2.
Khi gặp khối **DÙNG TRONG DỰ ÁN**, đọc nó để biết kiến thức phục vụ hành động
nào; nhãn “trước khi có user” là chặng bắt buộc sau phần dựng nền, không có
nghĩa có thể bỏ qua lúc phát hành.

**Cách dùng mỗi bài:** nhìn Cần nhớ/Phải tự làm/Cách kiểm → học từng mục → mở
Cú pháp & kiến trúc để mổ xẻ ký hiệu và tự chọn nơi sửa → viết bài từ ô trống.
Source/ZIP là tài liệu đối chiếu và môi trường học. Đừng coi chạy nguyên mẫu
là bằng chứng mình tự viết được.

## Buổi 0.1 — Đề đầu tiên nhỏ đến mức có thể tự kiểm

Sản phẩm đầu: **Sổ lớp học**. Bản đầu chỉ thêm tên lớp, hiển thị danh sách và
tìm theo tên. Dữ liệu ở RAM; tải lại mất dữ liệu là hành vi đã chọn cho bản này.
Chưa có tài khoản, database hoặc triển khai. Ta thêm chúng sau khi hiểu được
việc một nút làm dữ liệu và màn hình thay đổi ra sao.

Trước khi code, viết ra ví dụ bằng tiếng Việt:

| Thao tác | Kết quả đã chọn |
|---|---|
| Thêm “  Toán 10  ” | Lưu tên “Toán 10”, hiện một lớp |
| Thêm toàn khoảng trắng | Báo lỗi, danh sách giữ nguyên |
| Tìm “toán” | Thấy “Toán 10” |
| Tìm “Sinh” khi chưa có | Hiện “Không có lớp phù hợp” |
| Thêm hai lớp trùng tên | Cho phép ở bài đầu; id vẫn khác nhau |

Vì sao cho trùng tên? Hai lớp có thể cùng học một môn. Nếu người dùng muốn
cấm trùng, cần xác định phạm vi: cùng giáo viên, cùng năm học hay toàn trường.
Tên biến và framework không tự trả lời câu hỏi sản phẩm này.

**Tự làm:** thêm một dòng ví dụ cho tên có chữ hoa và một dòng cho danh sách
rỗng. Nếu chưa biết kết quả cần là gì, chốt quy tắc trước khi chọn hàm.

## Buổi 0.2 — Đường học chính và lúc mở tài liệu chuyên sâu

Học theo các chặng trên trang chủ. Mỗi H2 là một buổi nhỏ; một buổi có thể
cần vài lần ngồi học. Đi tiếp khi tự làm được đầu ra, không theo số ngày cố định.

| Chặng | Bài chính | Việc tự làm sau chặng |
|---|---|---|
| Nối từ Python | [F0](F0-python-sang-js-ts.md), [F2](F2-doc-ham-va-tool.md), [F1](F1-html-css-tu-dau.md) | Viết JS if/for/hàm; đọc một API lạ; dựng một card |
| Web đầu tiên | [G1](G1-trang-web-tu-thu-muc-trong.md) | Tạo HTML/CSS/JS riêng, thêm/tìm lớp và sửa lỗi DOM |
| TypeScript/React | [G2](G2-tu-js-sang-react.md) | Tự tạo manifest/entry, chia component và giữ state đúng chỗ |
| Tổ chức Python | [G3](G3-python-tu-mot-file-den-module.md) | Viết bản một file rồi tự tách module, sửa import, giữ hành vi |
| Xuyên hệ thống | [G4](G4-thiet-ke-tinh-nang-xuyen-he-thong.md) | Lần được request, dữ liệu, quyền và transaction qua các file |
| Mở rộng LMS | [G5](G5-tu-lat-cat-den-toan-bo-lms.md) | Thiết kế điểm danh có hướng dẫn, rồi tự xây module mới |
| Tự làm và nhận phản hồi | [G6](G6-tu-lam-va-duoc-phan-hoi.md) | Nộp code và lý do thiết kế, sửa sau review, làm biến thể |
| Trước người dùng thật | P2 → P3 → P4 → P5 | Đo tải, dựng môi trường, thử phục hồi và nghiệm thu |

F0 có cả JS và TS. Lượt đầu học phần JS đến trước mục thêm kiểu; giữ phần
TS để quay lại ở G2. G1 nhắc lại những cú pháp cần ngay tại chỗ. Nếu callback
chưa hiểu, mở mục tương ứng của [01](01-javascript.md), thử ví dụ nhỏ rồi quay
lại G1. Không cần học hết Promise, SQL và OOP mới được làm trang đầu.

Các chương 00–28 là **thư viện chuyên đề**. Mở theo liên kết trong buổi đang
học hoặc khi cần đào sâu. Bài tập khó ở đó làm sau chặng hướng dẫn tương ứng.
[Xưởng 21](21-xay-tu-so-0.md) là lần xây lại tổng hợp sau G4, không còn là
điểm bắt đầu cho người chưa từng tạo frontend.

## Buổi 0.3 — Một bài phải trải qua bốn lần làm

Lấy việc thêm lớp làm ví dụ:

1. **Làm cùng:** đọc yêu cầu, dự đoán, tự gõ một đoạn; so đầu vào/đầu ra với
   bảng. Bài giảng giải thích vì sao chọn đoạn đó và lựa chọn khác gây gì.
2. **Bớt gợi ý:** đã có HTML và hợp đồng hàm, tự viết phần thân hàm hoặc nối
   sự kiện. Chỉ mở gợi ý thứ nhất khi đã có một lần thử và ghi chỗ vướng.
3. **Đề mới:** nhận “đổi tên lớp”, tự xác định dữ liệu nào đổi và file nào chịu
   trách nhiệm. Có tài liệu ngôn ngữ, chưa mở lời giải dự án.
4. **Thay yêu cầu:** “lớp đã lưu trữ vẫn đọc được nhưng cấm tạo bài mới”. Giải
   thích các đường ghi phải kiểm, sửa code và thêm ca kiểm tra.

Nếu mới làm được lần 1, ghi “làm có hướng dẫn”. Nếu cần xem lại một hàm API,
vẫn có thể tính là tự làm; ghi nguồn đã tra và hợp đồng đã hiểu. Nếu chép toàn
bộ lời giải, cần làm lại một biến thể trước khi ghi “tự làm được”.

**Đầu ra:** một thư mục học riêng và ghi chú cho biết đang ở lần nào. Code
tham chiếu trong sách dành cho đối chiếu sau khi thử; không thay code của mày.

## Buổi 0.4 — Tự chia cấu trúc bắt đầu từ một thay đổi cụ thể

Giả sử bản một file chứa: đọc input → kiểm tên → lưu list → in danh sách.
Với chương trình nhỏ này, giữ một file giúp nhìn toàn bộ đường chạy.

Giờ thêm HTTP và CLI cùng tạo lớp. Nếu mỗi nơi viết lại kiểm tên, lần đổi
“tên tối đa 120 ký tự” dễ chỉ sửa một bên. Ta rút quy tắc vào hàm dùng chung.
Giờ đổi RAM sang DB: nếu quy tắc chỉ cần “tìm lớp/lưu lớp”, mình tách cách lưu
ra để thay nó mà giữ quy tắc. Đây là hai áp lực dẫn tới ranh giới cụ thể.

| Trước khi tạo file mới, hỏi | Bằng chứng cần có |
|---|---|
| File này chịu trách nhiệm gì? | Một câu như “kiểm và thực hiện lưu trữ lớp” |
| Ai gọi nó, nhận/trả gì? | Tên hàm và ví dụ input/output |
| Nó cần biết công nghệ nào? | Hàm nghiệp vụ cần biết SQL hay chỉ thao tác kho? |
| Khi quy tắc đổi, phải sửa đâu? | Chỉ ra những file liên quan và lý do |
| Có thêm tầng mà chỉ chuyển tiếp không? | Giữ chung nếu chưa có lợi ích rõ |

[G3](G3-python-tu-mot-file-den-module.md) thực hiện đầy đủ lần tách này, cả
cây trước/sau và import. [G4](G4-thiet-ke-tinh-nang-xuyen-he-thong.md) nối
tiếp sang API/DB/UI. Không có một cây thư mục duy nhất đúng cho mọi dự án;
cần giải thích được ranh giới và thay yêu cầu mà vẫn giữ hành vi đã chọn.

**Tự kiểm:** nếu chuyển từ in terminal sang web, quy tắc tên rỗng có đổi không?
Nếu câu trả lời là không, hãy khoanh phần quy tắc có thể giữ chung.

## Buổi 0.5 — Chạy code ở đâu và làm gì khi chưa chạy được

Trước G1, mở PowerShell và kiểm công cụ đang có:

```powershell
Get-Location
python --version
node --version
npm.cmd --version
```

Python phải in số phiên bản; bản lab đã được kiểm bằng Python 3.12. Node/npm
chỉ cần từ G2; môi trường soạn đang dùng Node 24. Nếu đã có công cụ chạy được,
giữ nguyên để học. Khi thiếu Node, mở [trang tải chính thức](https://nodejs.org/en/download),
chọn Windows và bản LTS tương thích, chạy bộ cài rồi mở terminal mới và kiểm
lại node/npm. [Vite ghi yêu cầu Node tại đây](https://vite.dev/guide/); đối chiếu
trước cài, vì toolchain có thể nâng yêu cầu. Nếu PowerShell chặn npm.ps1, dùng
npm.cmd cùng các đối số, ví dụ npm.cmd run dev; chưa cần đổi execution policy.

Nếu chưa có Python, theo [hướng dẫn Windows chính thức](https://docs.python.org/3/using/windows.html).
Giữ interpreter đang học Python nếu nó đáp ứng dependency của lab; khi có nhiều
bản, đọc đường dẫn bằng Get-Command python. Nếu lệnh python mở Microsoft Store
hoặc trỏ nhầm bản, dùng đường dẫn interpreter thật thay cho python trong các
lệnh bài học. Cần một editor lưu file UTF-8, hiện extension thật: index.html
không được thành index.html.txt. Tạo một file, lưu rồi xem tên bằng Get-ChildItem.

File HTML cuốn sách đọc được offline. Code ứng dụng thực hành cần lưu thành
file và chạy ở môi trường riêng; nút sao chép không tự tạo dự án hay khởi động
server. Mỗi buổi thực hành ghi thư mục đứng, lệnh chạy và kết quả mong đợi.

Tạo một thư mục như <code>D:\lms-tu-hoc</code> do mày quản lý. Bắt đầu rỗng;
đừng sửa sản phẩm thật để thử một khái niệm. G1/G2 dạy tạo từng file. Nếu đang
có source khóa học trên máy, thư mục <code>docs/course/studio</code> chứa các
bản đối chiếu nhỏ; workshop chứa bản xuyên hệ thống lớn hơn.

Ba tầng đọc lỗi:

| Quan sát | Kiểm trước | Việc sửa đầu tiên |
|---|---|---|
| Không tìm thấy file/module | Thư mục terminal, tên file, import | So cây thư mục thực với cây trong buổi |
| Lệnh không được nhận diện | Python/Node đang có trên máy | Theo phần kiểm môi trường của G1/G2 và [công cụ](16-cong-cu.md) |
| Trang mở nhưng bấm không đổi | Console, sự kiện, dữ liệu trước/sau | Đặt một log ở handler rồi theo từng bước |
| Màn hình báo lỗi HTTP | Network: URL/method/status/body | Theo G4 để xác định request dừng ở đâu |

Ghi nguyên thông báo lỗi đã bỏ thông tin riêng, file/dòng, lệnh vừa chạy và
mong đợi. Mỗi lần kiểm một giả thuyết. Nếu chưa có Python/Node hoặc mạng để
cài thư viện, vẫn đọc và làm phần Python/HTML cơ bản trước; giữ chặng React
ở trạng thái chưa chạy, không đánh dấu đã kiểm.

## Buổi 0.6 — Khi gặp một hàm hoặc công cụ lạ

Đọc đoạn đang học, gạch tên chưa biết. Với mỗi tên, viết một phiếu:

| Câu hỏi | Ví dụ <code>title.trim()</code> |
|---|---|
| Nó từ đâu? | Method của chuỗi JavaScript |
| Dùng lúc nào? | Bỏ khoảng trắng ở hai đầu tên |
| Nhận gì? | Chuỗi bên trái dấu chấm; không truyền đối số ở lần này |
| Trả gì? | Chuỗi mới |
| Thay đổi gì? | Không sửa biến title nếu chưa gán kết quả |
| Thử nhỏ nhất? | “  Toán  ” trở thành “Toán” |
| Biến thể để hiểu? | Khoảng trắng giữa “Toán  10” vẫn còn |

Tra [F2](F2-doc-ham-va-tool.md) và nút **Tra hàm/tool**. Nếu bộ tra không có
tên đó, lần về import/định nghĩa hoặc tài liệu chính thức đúng thư viện. Đọc
được cú pháp chưa cho biết return, lỗi hoặc tác dụng của một API cụ thể.

**Bớt gợi ý:** điền phiếu cho <code>document.querySelector</code> trong G1,
rồi cho <code>useState</code> ở G2. Giữ cùng cách tra khi sang Python ORM.

## Buổi 0.7 — Phản hồi phải chỉ ra bước sửa tiếp theo

Sau buổi học, lưu bốn thứ: đề/quy tắc, code tự viết, kết quả kiểm, điều chưa
giải thích được. Ghi chú trong sách lưu tại trình duyệt; dùng Xuất ghi chú để
có bản sao. File code phải được lưu trong thư mục học của mày.

Ví dụ phản hồi có ích: “Tên rỗng vẫn thêm được vì handler lưu trước validation.
Hãy đặt phép kiểm trước append, rồi chứng minh danh sách không đổi khi bị từ
chối.” Phản hồi “code chưa clean” không chỉ ra việc nào cần sửa.

[G6](G6-tu-lam-va-duoc-phan-hoi.md) có bài review mẫu, thang nhận xét theo
bằng chứng và mẫu gửi bài. Sách HTML kiểm được câu trắc nghiệm/mô phỏng của
nó; nó chưa tự đọc/chấm dự án riêng. Muốn nhận xét code thực, gửi các file và
kết quả kiểm cho người review hoặc trợ lý trong cuộc trao đổi học tiếp theo.
Sửa nhận xét xong, thử một trường hợp mới để kiểm lại lời khuyên.

**Bài buổi đầu:** mở F0 phần JS, viết một hàm nhận list điểm và trả list điểm
từ 5 trở lên bằng for/if. Thử list rỗng, điểm 0 và điểm đúng 5. Giải thích
return ở đâu. Khi làm được, chuyển F1 rồi G1; không mở sẵn toàn bộ đáp án G1.

## Buổi 0.8 — Từ dự án học đến hệ thống có người dùng thật

Một bản UI/API/DB chạy ở máy là mốc đầu. Toàn LMS còn cần chốt và làm lần lượt
các module ở G5. Sau đó thực hành [P2](25-hieu-nang-chiu-tai.md),
[P3](26-trien-khai-ci-cd.md), [P4](27-bao-mat-va-van-hanh.md) và
[P5](28-do-an-va-nghiem-thu.md). Chặng vận hành bắt đầu với một luồng đã đúng.

Chọn một hành động như học sinh nộp bài. Viết workload và mục tiêu cần phục vụ,
chạy baseline, đọc latency/lỗi/DB locks, sửa một nguyên nhân rồi đo lại cùng
điều kiện. Đọc migration/backup/restore trước một lần phát hành. Xác định session,
quyền, lỗi người dùng nhìn thấy và nơi theo dõi sự cố. Ghi giới hạn chưa đo.

Các source lab của sách có thể hỗ trợ việc học ấy; chúng không tự chứng minh
sản phẩm của mày đã chịu tải hoặc đủ an toàn. Cả lượng người dùng đáp ứng được
và chất lượng dự án cần bằng chứng từ chính code/môi trường của mày.

**Điều kiện hoàn thành khóa:** tự làm một tính năng mới, giải thích được cấu
trúc, sửa được yêu cầu thay đổi, bàn giao để người khác chạy, và có hồ sơ kiểm
chức năng/vận hành tương ứng phạm vi đã công bố. G6 và P5 giúp đối chiếu từng
điều kiện bằng sản phẩm cụ thể.
