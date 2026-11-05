# G6 — Tự làm, nhận review và chứng minh mình đã hiểu

Mày đã đi từ Python quen thuộc sang HTML/CSS, JS, React, rồi một luồng UI →
HTTP → Python → DB. Bài cuối của tuyến chính không yêu cầu đọc thêm một stack.
Ta dùng chính những thứ đã học để kiểm ba việc: tự phân tích một yêu cầu mới,
chọn nơi đặt code có lý do, và sửa một lời giải sai bằng bằng chứng.

**Đọc hết chương, tick xong hoặc quiz đúng chưa chứng minh tự xây được LMS.**
Một dấu hiệu đáng tin hơn là: nhận đề chưa có cây file, viết fixture, tự làm
một lát cắt, tái hiện được lỗi, giải thích được thiết kế và đổi được quy tắc.
Nếu cần mở gợi ý, ghi tầng đã mở. Đó là dữ liệu để biết luyện tiếp ở đâu.

Code đối chiếu của ví dụ review ở
[review_lab.py](studio/attendance/review_lab.py), bài chuyển miền ở
[renewal_reference.py](studio/attendance/renewal_reference.py), kiểm tra ở
[test_review_lab.py](studio/attendance/test_review_lab.py). Chúng là ví dụ
nghiệp vụ độc lập. Chưa có route/UI/library DB hoặc load test cho phần này.

## Phiên 1 — Nhìn một lời giải chạy được và tìm điều nó hiểu sai

**Đầu ra:** một lỗi có input, expected, actual và lời giải thích bằng quy tắc.

Đề mới: “Báo cáo tỷ lệ đi học của một danh sách lượt điểm danh”. Ta hỏi và
chốt chính sách cho bài này trước khi chọn công thức:

| Trạng thái | Có trong mẫu số? | Có trong tử số? |
|---|---|---|
| `present` — có mặt | Có | Có |
| `late` — đi muộn | Có | Có |
| `absent` — vắng | Có | Không |
| `excused` — vắng có phép | Không | Không |
| `None` — chưa ghi | Không | Không |

Tỷ lệ là `số lượt đi học / số lượt được tính × 100`, làm tròn hai chữ số khi
trả kết quả. Không có lượt được tính thì trả `None`, để UI hiện “Chưa có dữ
liệu tính tỷ lệ”. Nó khác `0.0`: đã có lượt được tính và tất cả đều vắng.
Đây là chính sách bài học, không mặc định đúng với mọi nhà trường.

Một người gửi lời giải sau và nói “chạy ra số rồi”:

```python
def bad_attendance_rate(statuses):
    present = 0
    for status in statuses:
        if status == 'present':
            present += 1
    return round(present * 100 / len(statuses), 2)
```

Code này hợp cú pháp. `round(value, 2)` trả số làm tròn; `len` đếm mọi phần tử.
Không có lỗi syntax không đồng nghĩa với đúng yêu cầu. Trước khi sửa, tính
tay fixture: `['present', 'late', 'absent', 'excused', None]`.

| Đại lượng | Đúng theo đề | Code trên đang tính |
|---|---|---|
| Tử số | 2: present + late | 1: chỉ present |
| Mẫu số | 3: present + late + absent | 5: tất cả |
| Kết quả | 66.67 | 20.0 |

Từ gốc **D:\vision-education-lms**, cố ý chạy lời giải sai:

```powershell
.\.venv\Scripts\python.exe docs/course/studio/attendance/review_lab.py bad
```

Phải thấy `actual: 20.0 expected: 66.67`, rồi `AssertionError`; lệnh kết thúc
không thành công là **bằng chứng đã tái hiện lỗi có chủ đích**. Đừng sửa
expected thành20.0. Đừng gửi ảnh một số20.0 rồi nói chương trình đã đúng.
Nếu máy chưa có venv của xưởng, dùng interpreter Python3.10+ của repo học;
ví dụ này chỉ dùng standard library, chưa cần SQLAlchemy hay FastAPI.

**Tự làm trước khi đọc tiếp:** viết thêm input làm hàm trên ném lỗi khác thay
vì trả sai số. Ghi dự kiến trước khi chạy.

<details><summary>Đối chiếu lỗi thứ hai</summary>

`[]` làm phép chia cho0 và ném `ZeroDivisionError`. `[None, 'excused']` trả
0.0 nhưng phải là None. Cần cả test danh sách rỗng lẫn danh sách có hàng mà
không có hàng đủ điều kiện; chúng giống đầu ra nhưng đi qua dữ liệu khác.

</details>

**Nếu kẹt:** quay phần điều kiện/vòng lặp ở [F0](F0-python-sang-js-ts.md) hoặc
[tư duy đầu vào/đầu ra](17-tu-duy-lap-trinh.md). Chưa thêm biểu đồ để che một
công thức chưa tính đúng bằng tay.

## Phiên 2 — Sửa từ quy tắc, theo dấu biến rồi mới rút gọn

**Đầu ra:** một hàm thuần đúng với fixture, rỗng, biên và dữ liệu không hợp lệ.

Ta cần hai biến, vì tử số và mẫu số không đếm cùng thứ. Trước mỗi vòng lặp,
`attended/eligible` phản ánh những hàng **đã duyệt**. Một hàng chưa ghi/vắng
có phép không làm đổi biến nào. Một hàng vắng tăng eligible nhưng không tăng
attended. Một hàng có mặt/đi muộn tăng cả hai.

```python
def attendance_rate(statuses):
    attended = 0
    eligible = 0
    for status in statuses:
        if status is None or status == 'excused':
            continue
        if status not in ('present', 'late', 'absent'):
            raise ValueError('Unknown attendance status')
        eligible += 1
        if status in ('present', 'late'):
            attended += 1
    if eligible == 0:
        return None
    return round(attended * 100 / eligible, 2)
```

`continue` bỏ phần còn lại của lượt hiện tại, không thoát toàn bộ hàm.
`is None` kiểm giá trị không có dữ liệu. `in` kiểm một giá trị có trong tập
giá trị đã chọn. `raise` dừng và báo dữ liệu vi phạm hợp đồng: không âm thầm
đổi `'unkown'` thành vắng. Hàm nhận sequence trạng thái đã lấy từ dữ liệu có
phạm vi hợp lệ; nó không tự xác thực người gọi hay query DB.

Theo dấu fixture ở phiên1:

| Sau hàng | attended | eligible | Vì sao |
|---|---|---|---|
| present | 1 | 1 | Tính cả hai |
| late | 2 | 2 | Đi muộn vẫn là một lượt đi học |
| absent | 2 | 3 | Chỉ mẫu số tăng |
| excused | 2 | 3 | Bỏ qua |
| None | 2 | 3 | Bỏ qua |

Chạy bản đã sửa, cùng input và cùng expected:

```powershell
.\.venv\Scripts\python.exe docs/course/studio/attendance/review_lab.py fixed
.\.venv\Scripts\python.exe -m unittest discover -s docs/course/studio/attendance -p test_review_lab.py -v
```

Lệnh đầu phải in66.67 và `verified fixture`. Suite có tests báo cáo và gia
hạn sách của phiên7. Mở test và đọc **input/assertion**; số lượng test qua
không thay cho việc hiểu chúng kiểm gì.

| Input bổ sung | Expected | Lỗi sẽ phát hiện |
|---|---|---|
| `[]` | None | Chia0 |
| `[None, 'excused']` | None | Nhầm chưa có dữ liệu thành0% |
| `['absent', 'absent']` | 0.0 | Nhầm0 với None |
| `['present', 'late']` | 100.0 | Bỏ sót late |
| `['present', 'unknown']` | ValueError | Che dữ liệu sai thành số hợp lệ |

Tự viết một test trước khi mở test reference. Thử đổi điều kiện late cho
sai, chạy đúng test và thấy fail, rồi khôi phục và chạy suite. Đây là kiểm
test có bảo vệ quy tắc; không cần một mutation framework ở buổi này.

**Nếu kẹt:** log `status, attended, eligible` trong bản học cục bộ, so đúng
hàng đầu tiên khác bảng. Đừng thay cả vòng lặp, công thức và fixture cùng lúc.

## Phiên 3 — Review cả chỗ đặt code và giới hạn của lời giải

**Đầu ra:** một quyết định cấu trúc ngắn và một thay đổi yêu cầu đã phân tích.

Với một hàm báo cáo, chưa cần tạo mười file. Khi ghép vào repo điểm danh:

```text
attendance/
  core.py       dữ liệu, quyền thao tác và quy tắc ghi đã học
  reports.py    attendance_rate và chính sách tổng hợp thuần
  storage.py    lấy dữ liệu đúng phạm vi; không tự quyết nghĩa late
  routes.py     đọc query/body, resolve actor, map lỗi và output
```

Đây là lựa chọn khi nhóm báo cáo có trách nhiệm riêng. Nếu chỉ đang thử một
hàm, để cùng core vẫn hợp lý. Điểm cần giữ: router không có bản công thức
riêng; React không tự quyết mẫu số khác server; reports không mở connection
hay import route. Khi người review hỏi “vì sao file này tồn tại?”, trả bằng
trách nhiệm/chỗ thay đổi, không bằng “dự án lớn ai cũng chia như vậy”.

Một phản hồi có ích là: “Hàm nhận mọi trạng thái, nhưng chưa có bằng chứng
endpoint chỉ lấy buổi lớp người gọi được xem. Hãy thêm test tài khoản ngoài
lớp; kết quả không được chứa số đếm hoặc dữ liệu của lớp đó.” Phản hồi này
phân biệt **công thức thuần** đã đúng với **phạm vi query** chưa được chứng minh.
Không nhét kiểm JWT vào công thức để phản ứng với mọi góp ý về bảo mật.

Yêu cầu đổi: “Tổng tỷ lệ của hai buổi có sĩ số khác nhau.” Giả sử buổi A có
1/1 đi học, buổi B có0/9. Trung bình hai phần trăm là50%, nhưng tỷ lệ theo
**tất cả lượt đủ điều kiện** là1/10=10%. Hai câu trả lời tương ứng hai câu hỏi
khác nhau. Phải hỏi người dùng muốn cân theo buổi hay theo lượt.

Nếu chọn cân theo lượt, trả/cộng tử số và mẫu số trước rồi chia **một lần**.
Không lấy trung bình các phần trăm đã làm tròn. Tự ghi trường dữ liệu nào
cần trả thêm và test1/1 +0/9. Câu “đã có dashboard” không đủ trả lời.

**Nếu kẹt:** quay cách suy ra trách nhiệm và hướng import ở
[G3](G3-python-tu-mot-file-den-module.md), rồi trace một request theo
[G4](G4-thiet-ke-tinh-nang-xuyen-he-thong.md). Một hàm có unit test không tự
chứng minh endpoint, UI hay số liệu người dùng thật đã đúng.

## Phiên 4 — Bài có hướng dẫn: đếm đủ để giải thích tỷ lệ

**Đầu ra:** tự viết `attendance_summary(statuses)` trả attended, eligible,
unmarked, excused và rate. Dùng lại policy, không trả mỗi con số thiếu nghĩa.

Fixture phiên1 phải trả:

```json
{"attended": 2, "eligible": 3, "unmarked": 1, "excused": 1, "rate": 66.67}
```

Trước khi code, điền biến nào tăng với từng status. Sau đó tự viết vòng lặp.
Tạo ít nhất bốn test: fixture trên; tất cả chưa ghi; tất cả vắng; status sai.
Tên field là một hợp đồng cần giữ giữa Python và UI.

<details><summary>Gợi ý 1 — Cần phân biệt đại lượng nào?</summary>

attended là một phần của eligible, không cộng chúng với nhau để tính tổng.
unmarked/excused nằm ngoài eligible. Tổng lượt bằng eligible+unmarked+excused.
Kết quả0 eligible vẫn có thể có nhiều lượt chưa ghi.

</details>

<details><summary>Gợi ý 2 — Thứ tự nhánh</summary>

None → tăng unmarked; excused → tăng excused; ba status được tính → tăng
eligible, có mặt/đi muộn tăng attended; status còn lại → raise. Tính rate sau
vòng lặp. Nếu muốn dùng lại hàm đã có, nhận list/tuple và gọi attendance_rate;
đừng duyệt generator một lần rồi mong lần hai còn dữ liệu.

</details>

<details><summary>Lời giải đối chiếu — Mở sau bản chạy đầu tiên</summary>

```python
def attendance_summary(statuses):
    attended = eligible = unmarked = excused = 0
    for status in statuses:
        if status is None:
            unmarked += 1
        elif status == 'excused':
            excused += 1
        elif status in ('present', 'late', 'absent'):
            eligible += 1
            if status in ('present', 'late'):
                attended += 1
        else:
            raise ValueError('Unknown attendance status')
    rate = None if eligible == 0 else round(attended * 100 / eligible, 2)
    return {'attended': attended, 'eligible': eligible,
            'unmarked': unmarked, 'excused': excused, 'rate': rate}
```

Dòng `a = b = 0` gán giá trị0 cho hai biến độc lập ở ví dụ số bất biến này.
Biểu thức `x if condition else y` chọn một giá trị; nó không phải một lượt
vòng lặp mới. Nếu đọc dạng ngắn khó, tự viết if/else nhiều dòng trước.
Lời giải này cố ý tính một lượt. Khi đưa vào module thật, chọn summary làm
nguồn chuẩn rồi cho attendance_rate đọc field rate, hoặc bỏ hàm cũ nếu không
còn caller. Không giữ hai bản chính sách phải sửa song song mà thiếu test.

</details>

UI cần hiện “2/3 lượt; 1 chưa ghi; 1 vắng có phép”. Nếu rate None, hiện chữ
giải thích. Tránh `{rate || 'Chưa có dữ liệu'}` trong JS vì0 là falsy; dùng
kiểm `rate === null`. Đó là lý do semantics từ Python phải đi tới màn hình.

## Phiên 5 — Bài giảm gợi ý: báo cáo một lớp trong khoảng ngày

**Đầu ra:** contract, fixture, một endpoint có quyền, UI có trạng thái và test.
Từ đây đề không cho sẵn cây file hoặc handler. Tự chọn theo cấu trúc đã có.

Giáo viên muốn xem tỷ lệ trong khoảng ngày cho lớp mình phụ trách. Dữ liệu
buổi có ngày học `session_date` của lớp. Khoảng ngày gồm cả hai đầu; tối đa31
ngày; ngày đầu không sau ngày cuối. Bài này dùng ngày lịch `YYYY-MM-DD`, chưa
đổi nó thành timestamp UTC. Chọn timezone lớp khi tạo session_date từ lịch
ở module lịch; không lấy ngày theo browser một cách tùy tiện.

Quy tắc báo cáo:

- Chỉ giáo viên đang có quyền với lớp được đọc. Role teacher một mình chưa đủ.
- Học sinh chuyển lớp không làm thay roster lịch sử. Dùng lượt đã chốt của buổi.
- Buổi ngoài khoảng không được tính; unmarked/excused giữ policy phiên1.
- Chưa có buổi và có buổi nhưng chưa ghi đều có rate None; output cần cho
  biết số buổi để UI giải thích khác nhau.
- Không tải cả LMS vào Python rồi lọc ngoài quyền. Query DB có class/phạm vi
  ngày phù hợp, rồi mới tổng hợp theo policy đã chốt.

Fixture: lớp7 có buổi16/10 present;17/10 late+absent;18/10 excused+None.
Lớp8 có buổi17/10 present+present. Actor chỉ dạy lớp7. Khoảng17–18/10 phải
có2 buổi, attended1, eligible2, unmarked1, excused1, rate50.0. Buổi16/10 và
cả lớp8 không được đóng góp. Tự thêm fixture ngày đầu=ngày cuối.

<details><summary>Gợi ý 1 — Viết hợp đồng trước</summary>

Một lựa chọn là GET `/classes/7/attendance-report?from=2026-10-17&to=2026-10-18`.
Không gửi teacher_id để khai quyền. Chốt output gồm class_id,from,to,sessions,
attended,eligible,unmarked,excused,rate; chốt lỗi khoảng ngày và ngoài quyền.
31 ngày tính cả hai đầu nghĩa `(to_date-from_date).days+1 <= 31`.

</details>

<details><summary>Gợi ý 2 — Chia bài để tìm lỗi đúng tầng</summary>

Test pure summary trước; test bộ lọc ngày riêng; integration test query và
scope với hai lớp; API test query invalid và actor; UI test hoặc kiểm tay
None/0/loading/error. Lọc ngày đúng chưa chứng minh lọc quyền đúng. Khi đổi
query nhanh, response cũ không được thay kết quả query hiện tại; dùng cleanup
hoặc request identity theo cách đã học ở G4.

</details>

<details><summary>Thiết kế tham chiếu — Không phải module đã được triển khai sẵn</summary>

Schema ranh giới parse hai ngày, kiểm thứ tự/độ dài. Service resolve quyền lớp,
nhờ repository đọc đúng buổi thuộc class trong khoảng. JOIN marks từ roster
lịch sử; đếm distinct sheet id cho số buổi và tổng hợp marks theo policy.
Không đếm row JOIN làm số buổi vì một buổi có nhiều mark.

reports.py giữ công thức thuần; service giữ use case/quyền; storage/repository
giữ query; route giữ HTTP. UI có input ngày, nút xem, loading/error và kết quả
đã xác nhận; giữ ngày đã nhập nếu request lỗi. HTTPresponse contract được
parse runtime, không dùng `as AttendanceReport` để coi JSON đã được kiểm.

Index có thể bắt đầu xét trên sheet `(class_id, session_date)` và mark PK
`(sheet_id, student_id)`. Chỉ thêm sau khi nhìn query/schema thực và EXPLAIN;
tên index trong giáo án chưa phải bằng chứng query nhanh với dữ liệu lớn.

</details>

Sau khi chạy được, tự thêm một yêu cầu: “Cho xem từng học sinh trong cùng
khoảng”. Trước khi code, giải thích vì sao không chia rate toàn lớp đều cho
mỗi học sinh và vì sao tên học sinh không phải khóa group. Nếu chỉ đổi chữ
trên màn hình mà không đổi nhóm dữ liệu, mày chưa làm yêu cầu mới.

## Phiên 6 — Đánh giá năng lực bằng sản phẩm, rồi chọn đúng bài bù

**Đầu ra:** một phiếu có bằng chứng cho từng tiêu chí; không tự cho điểm bằng
cảm giác quen code. Chọn0/1/2/3 theo hành động đã làm được.

| Tiêu chí | 0 — Chưa làm | 1 — Có mẫu từng bước | 2 — Làm với gợi ý nhỏ | 3 — Tự làm và giải thích |
|---|---|---|---|---|
| Phân tích đề | Chỉ liệt kê màn hình | Điền policy đã cho | Tự viết happy/error/biên | Hỏi/chốt mơ hồ và dự đoán yêu cầu đổi |
| Dữ liệu | Chép model | Giải thích field có sẵn | Tự suy một hàng/khóa/state | Chứng minh lịch sử, constraint và migration |
| Code | Chỉ đọc hoặc chạy bản cuối | Tự gõ theo | Tự viết lại sau gợi ý | Nhận biến thể mới và hoàn thành |
| Cấu trúc | Thuộc tên folder | Biết file hiện có làm gì | Tự đặt chức năng, import chạy | So hai cách chia và nêu lý do chọn |
| Đúng luật/quyền | Chỉ demo thành công | Theo bảng test mẫu | Tự thêm case sai và biên | Có test chống bỏ luật, scope list/detail nhất quán |
| UI/HTTP/DB | Một phần chạy riêng | Nối theo mẫu | Tự trace/tìm lỗi một tầng | Hai tài khoản, refresh, lỗi mạng, dữ liệu bền |
| Sửa theo review | Thay code theo lời nói | Sửa dòng được chỉ | Tái hiện rồi sửa | Phản biện bằng test, tự kiểm cả tác dụng phụ |

Một feature chưa hoàn thành nếu rule/quyền quan trọng ở mức0 dù CSS đẹp.
Mức1 không xấu; nó cho biết cần làm lại một biến thể trước khi nhận nhiệm vụ
độc lập. Không cộng các ô thành “đã biết85% lập trình”. Khi nói mức3, đính
kèm file/test/tình huống chứng minh thay vì chỉ tick ô.

| Dấu hiệu đang gặp | Nguyên nhân cần kiểm | Việc bù cụ thể |
|---|---|---|
| Biết Python nhưng không tự viết JS event | Chưa nối cú pháp với browser callback | Làm lại G1 buổi5: submit hiện chữ, cố ý sai selector và sửa; [F0](F0-python-sang-js-ts.md) hàm/callback |
| CSS chỉ chỉnh số tới khi đẹp | Chưa phân biệt cha/con, box model, cascade | Làm hai thử nghiệm margin/padding và bật/tắt flex ở [G1](G1-trang-web-tu-thu-muc-trong.md); đọc [F1](F1-html-css-tu-dau.md) |
| Đọc hàm lạ là dừng | Chưa biết tra chữ ký và thử input nhỏ | Điền phiếu một API đang dùng ở [F2](F2-doc-ham-va-tool.md), tự thử output/lỗi trước khi ghép |
| Refresh mất dữ liệu rồi sửa useState | Nhầm RAM frontend với DB | Vẽ nơi lưu/đọc ở [G4](G4-thiet-ke-tinh-nang-xuyen-he-thong.md), dùng Network rồi đọc DB mới |
| Không biết đặt một hàm ở file nào | Chưa gọi tên trách nhiệm/phụ thuộc | Viết hàm thuần một file, tách như [G3](G3-python-tu-mot-file-den-module.md), chứng minh import một chiều |
| Unit test xanh, teacher khác vẫn đọc được | Thiếu scope query/auth, không phải lỗi công thức | Lập fixture hai lớp ở [G5](G5-tu-lat-cat-den-toan-bo-lms.md), kiểm direct API list/detail và [quyền](09-auth-phan-quyen.md) |
| Bị lỗi là cài lại cả môi trường | Chưa thu nhỏ expected/actual và tầng lỗi | Dùng quy trình debug [19](19-debug-va-an-toan.md), ghi request/traceback đúng chỗ trước khi đổi package |
| Hai tab ghi đè mà một tab vẫn qua | Thiếu quy tắc đồng thời và DB bảo vệ | Làm lại bảng A–E, guarded UPDATE/rollback ở [G5](G5-tu-lat-cat-den-toan-bo-lms.md) |
| Nói chịu tải vì dùng async | Chưa có workload và đo | Chốt read/write/hotspot/dataset, chạy theo [P2](25-hieu-nang-chiu-tai.md) và giữ báo cáo CHƯA ĐO đến khi đo thật |

Sau mỗi bài bù, làm một input khác mà giáo án không vừa giải sẵn. Nếu vẫn
cần nhìn lời giải cho từng bước, giữ mức1 và đổi bài nhỏ hơn; không tự ép
qua chương chỉ vì lịch học ghi một ngày.

## Phiên 7 — Bài chuyển miền độc lập: gia hạn một lượt mượn sách

**Đầu ra:** bản phân tích và code do mày tự dựng, rồi một lát cắt API/UI/DB.
Đề này không phải đổi Class thành Book. Nó thêm thời hạn, hàng chờ và số lần
chuyển trạng thái; những thứ mà CRUD đổi tên không giải quyết được.

Một thư viện có lượt mượn sách: id,borrower_id,due_at,renewals,returned. Người
mượn được yêu cầu gia hạn khi đồng thời thỏa:

1. Đúng chủ lượt mượn và sách chưa trả.
2. Thời điểm server **nhỏ hơn** due_at; đúng thời điểm due_at đã quá hạn cho
   thao tác gia hạn. Mọi timestamp lưu/so sánh theo datetime có timezone UTC.
3. Chưa gia hạn đủ2 lần.
4. Không có người đọc khác đang xếp hàng chờ cuốn đó.

Nếu hợp lệ: tăng renewals1 và cộng7 ngày vào **due_at hiện tại**, không cộng
vào now. Bài đầu chỉ làm một lượt mượn và một flag hàng chờ đã được server
resolve. Chưa xây toàn bộ catalog, thanh toán, email hay mượn/trả sách.

Tự làm theo đúng thứ tự trước khi mở bất kỳ gợi ý nào:

- Viết fixture với now cố định; tính tay ngày hạn trước/sau và số lần.
- Viết bảng đủ điều kiện, từng điều kiện fail, biên now=due_at.
- Vẽ đường phụ thuộc file; viết hàm thuần và tests, chưa gọi DB trong hàm đó.
- Chốt input HTTP, quyền, nguồn hàng chờ và response; client không gửi
  borrower_id/renewals/other_reader_waiting để tự nhận điều kiện hợp lệ.
- Lắp repository/transaction, route và một nút gia hạn có loading/error;
  refresh phải thấy hạn đã commit. Dùng hai tài khoản để kiểm ngoài quyền.

Lưu `attempt-1.md` gồm quyết định và code trước khi mở gợi ý. Đừng đánh giá
mình theo việc giải pháp giống reference bao nhiêu; so đúng policy và bằng
chứng. Một cách chia file khác vẫn được nếu trách nhiệm rõ và hành vi đúng.

<details><summary>Gợi ý 1 — Thời gian phải là input để test được</summary>

Hàm nhận now thay vì tự gọi đồng hồ ở trong. Route/service ngoài lấy đồng hồ
server và truyền vào. Test dùng một ngày cố định nên không tự đỏ vào tuần sau.
Python `datetime(..., tzinfo=timezone.utc)` tạo giờ UTC có timezone;
`timedelta(days=7)` là khoảng thời gian để cộng. Import từ standard library,
không cài package tên datetime. Không trộn datetime naive và aware.

</details>

<details><summary>Gợi ý 2 — Một transition có điều kiện, không phải sửa field tự do</summary>

Trả bản Loan mới khi mọi điều kiện đã qua. Không tăng renewals trước rồi mới
kiểm hàng chờ. Returned,renewals,due_at đều là dữ liệu server; hàng chờ phải
được resolve trong ranh giới transaction phù hợp khi ghi. Endpoint PATCH cho
client tự đặt due_at bỏ qua chính quy tắc gia hạn.

</details>

<details><summary>Đáp án nghiệp vụ tham chiếu — Mở sau bản tự viết</summary>

```python
from dataclasses import dataclass, replace
from datetime import datetime, timedelta

@dataclass(frozen=True)
class Loan:
    id: int
    borrower_id: int
    due_at: datetime
    renewals: int = 0
    returned: bool = False

def renew_loan(loan, actor_id, other_reader_waiting, now):
    if loan.due_at.tzinfo is None or now.tzinfo is None:
        raise ValueError('Use timezone-aware datetimes')
    if actor_id != loan.borrower_id:
        raise PermissionError('Only the borrower may request renewal')
    if loan.returned:
        raise ValueError('Loan already returned')
    if now >= loan.due_at:
        raise ValueError('Loan reached its due time')
    if loan.renewals >= 2:
        raise ValueError('Renewal limit reached')
    if other_reader_waiting:
        raise ValueError('Another reader is waiting')
    return replace(loan, due_at=loan.due_at + timedelta(days=7),
                   renewals=loan.renewals + 1)
```

Đây là hàm rule trên dữ liệu đã được server dựng hợp lệ, không phải toàn bộ
input validation của API. Không tự chứng minh rằng flag hàng chờ đáng tin,
snapshot vẫn hiện hành hay DB đã commit. Tests reference kiểm happy path,
due_at biên, wrong borrower, returned,max renewals,waiting,naive clock và giữ
bản gốc. Đọc [file tests](studio/attendance/test_review_lab.py) để đối chiếu.

Một lựa chọn file khi ghép là loan_rules.py thuần; loan_repository.py đọc/ghi
loan+hàng chờ; loan_service.py resolve và giữ transaction; loan_routes.py map
HTTP; frontend api.ts và LoanCard.tsx. Không cần đúng các tên này. Phải giải
thích module nào biết đồng hồ, DB và giao thức.

</details>

<details><summary>Đáp án kiến trúc cho race/retry — Sau khi đã phân tích lỗi</summary>

Hai request cùng đọc renewals0 có thể cùng tính1. Cần khóa/guarded write trong
DB theo thiết kế, cùng ranh giới bảo vệ việc người khác vào hàng chờ. Khóa mỗi
loan mà quy trình tạo reservation không dùng cùng cơ chế thì chưa chặn race
giữa gia hạn và xếp hàng. Chốt serialization point theo cuốn/bản sách và test
engine thật. Một hàm pure đúng không tự giải quyết sự kiện diễn ra đồng thời.

POST gia hạn được gửi lại có thể gia hạn lần2 ngoài ý muốn. Phiên đầu phải
công khai “chưa hỗ trợ retry an toàn”; trước vận hành thêm request key ổn
định do client giữ cho một lần bấm, lưu kết quả và kiểm payload trong cùng
transaction. Cùng key/cùng thao tác trả kết quả đã lưu; key bị dùng cho một
loan khác bị từ chối; một lần bấm mới có key mới. Disable nút chỉ giảm bấm lặp
trên một tab, không thay idempotency của server.

Đây là yêu cầu tiếp theo để mày tự triển khai và chứng minh, chưa có library
DB/race/API/UI chạy sẵn trong bộ reference. Không đưa endpoint chưa có cơ chế
retry vào hoạt động thật rồi gọi nó đủ vì unit tests thuần đã qua.

</details>

Sau đối chiếu, đóng đáp án và tự nhận yêu cầu mới: “Có bạn đang chờ thì chỉ
thủ thư được duyệt gia hạn một lần ngoại lệ, phải có lý do và audit.” Viết
trước điều gì **không đổi**, điều gì đổi ở quyền/state/schema/API/UI/test. Nếu
cách làm là bỏ if hàng chờ cho mọi actor, đó là phá policy, chưa phải ngoại lệ.

## Phiên 8 — Bàn giao bài làm để người khác review được

**Đầu ra:** một gói bằng chứng của chính phiên bản đang review. Không cần
đẩy repository public để làm bài; có thể review trực tiếp trong workspace.

Trong repo học, tạo thư mục `learning-evidence/feature-name/` bằng editor hoặc
New-Item, không đặt dữ liệu học sinh thật hay secret vào đó. Gói tối thiểu:

```text
learning-evidence/feature-name/
  brief.md          yêu cầu, policy chốt, câu còn mở và fixture tay
  decisions.md      cây file tự chọn và vì sao; một phương án đã cân nhắc
  runs.md           lệnh/CWD/interpreter hoặc môi trường, expected/actual
  review.md         phản hồi, tái hiện, quyết định sửa và bằng chứng sau sửa
```

Trong runs.md ghi “đã chạy” cho lệnh thực sự chạy trên phiên bản đó. Ghi rõ
test bị skip, phần chưa kiểm và snapshot/commit nếu có. Nếu chưa dùng Git,
ghi ngày và tên bản lưu riêng để vẫn xác định được source. Ảnh UI đi kèm
tài khoản fixture/viewport/thao tác; ảnh đẹp không thay response DB/API.

Mẫu một dòng bằng chứng tốt:

```text
Case: reader 99 gia hạn loan 10 của reader 2.
Expected: từ chối; due_at và renewals giữ nguyên.
Command/CWD: ...
Actual: ...
Source/test: đường dẫn file và tên test.
Limit: chưa kiểm hai transaction trên MySQL.
```

Đường dẫn dẫn tới code đang tồn tại. Đừng chép placeholder `...` vào bài nộp
rồi coi là đã chạy. Traceback cần phần tên lỗi, vị trí và đường đi liên quan;
không đổ cả log có token/password vào yêu cầu review.

## Phiên 9 — Hỏi người review để học cách nghĩ, rồi kiểm cả lời review

**Đầu ra:** một vòng review có ít nhất một phản hồi được tái hiện/kiểm chứng.

Sách HTML tĩnh này **không đọc repo, chạy tests hay biết mày đã làm đúng**.
Ô ghi chú, quiz và tick chỉ giữ tiến độ tự khai. Muốn có phản hồi về code,
đưa code/evidence cho một người review hoặc trợ lý có quyền đọc đúng repo.
Nếu dùng trợ lý trong workspace này, chỉ rõ repo học và các file; nếu ở chat
khác, dán đoạn tối thiểu đủ tái hiện hoặc đính kèm source liên quan.

Dùng mẫu yêu cầu sau, điền đường dẫn thực:

```text
Tao biết cú pháp Python và đang luyện tự thiết kế, chưa muốn nhận toàn bộ đáp án.
Review feature [tên] trong repo [đường dẫn]. Đọc brief.md, decisions.md,
runs.md và các file [danh sách].

Trước hết hãy cho tao mô tả luồng bằng lời và hỏi một tình huống đổi yêu cầu.
Sau đó tìm lỗi có input/expected/actual hoặc rủi ro có đường đi cụ thể.
Với mỗi lỗi: nói quy tắc bị vi phạm, chỉ đúng file/hàm, cho gợi ý nhỏ nhất
để tao tự sửa, và đề xuất cách chứng minh. Đừng viết lại cả project trước.
Phân biệt điều đã kiểm từ source, điều đã chạy và điều còn chưa biết.
Nếu thiếu môi trường/fixture thì nêu chính xác thứ thiếu; không nói tests đã
qua nếu chưa chạy. Đánh giá cách chia trách nhiệm, không chỉ số lượng file.
```

Phản hồi “code chưa clean, dùng pattern X đi” chưa đủ hành động. Yêu cầu một
ví dụ: một rule nằm ở hai nơi nào, đổi yêu cầu sẽ lệch ra sao, cách kiểm lại.
Ngược lại, người review đưa một counterexample đúng thì chưa cần thống nhất
mọi sở thích đặt tên mới sửa lỗi dữ liệu/quyền trước.

Một vòng xử lý phản hồi:

1. Chép lại ý kiến bằng lời của mày: “Case này sai vì…”. Nếu chưa hiểu, xin
   một fixture nhỏ hơn, chưa áp patch.
2. Tạo case tái hiện trên bản hiện tại. Nếu chưa tái hiện, kiểm giả định,
   phiên bản, scope và input; giữ trạng thái “chưa xác minh”.
3. Viết test hoặc quy trình kiểm tay có expected. Test phải fail vì lỗi đang
   review, không vì import sai hay server chưa chạy.
4. Sửa nhỏ ở đúng trách nhiệm. Chạy case vừa fail, rồi suite/flow liên quan.
5. Đọc diff: policy khác, migration, output hay quyền có vô tình đổi không?
6. Ghi before/after/lệnh/kết quả/giới hạn vào review.md. Nhờ review lại thay
   đổi cụ thể, rồi tự giải thích vì sao sửa được.

Nếu lời khuyên đòi cài tool lạ, dùng [F2](F2-doc-ham-va-tool.md) xác minh tool
làm gì và đọc đúng docs/version. Đọc script trước khi chạy, nhất là lệnh xóa
dữ liệu, migration hoặc lệnh chứa secret. Không có nghĩa mọi phản hồi AI đều
đúng, cũng không nên bác phản hồi chỉ vì code hiện chưa đỏ.

## Phiên 10 — Kiểm khả năng tự xây, rồi tiếp tục đến bản vận hành

**Đầu ra:** một bài kiểm độc lập và backlog có thứ tự cho toàn LMS của mày.

Chọn một tính năng chưa được vừa làm mẫu, giới hạn đủ nhỏ hoàn thành một
lát cắt. Ví dụ: đóng một buổi điểm danh để ngừng sửa; mở lại phải có lý do và
lưu người/thời điểm. Trước khi mở sách, viết policy, fixture, cây file và kế
hoạch test. Tự làm bản đầu; ghi mọi gợi ý đã dùng. Sau đó người review đưa
một thay đổi chưa được báo trước, chẳng hạn đổi người phụ trách lớp sau khi
buổi đã tạo. Mày phân tích lại quyền hiện tại và lịch sử, rồi tự sửa có test.

Bài được coi là có bằng chứng tự làm khi:

- Mày giải thích đường từ nút UI đến dữ liệu đã commit, chỉ file thật và vì
  sao rule nằm ở đó; không chỉ đọc lại tên folder.
- Có happy path, sai dữ liệu, ngoài quyền và biên/chạy lại/đồng thời liên quan.
- Một lỗi được tái hiện, sửa và kiểm lại mà không sửa expected cho vừa code.
- Mày đáp ứng thay đổi mới và chỉ được phần chưa làm/chưa đo.

Nếu vẫn cần gợi ý, quay đúng ô trong rubric phiên6, làm biến thể nhỏ rồi thử
lại. Đây là vòng học; không suy ra “không hợp lập trình” từ một lần chưa làm
được và cũng không gán “đã thành thạo” chỉ vì chạy bản tham chiếu.

Để thành LMS hoàn chỉnh theo phạm vi đã chốt, dùng backlog ở
[G5](G5-tu-lat-cat-den-toan-bo-lms.md) và bản đồ
[P0](23-san-pham-hoan-chinh.md). Mỗi module đều qua chuỗi bằng chứng ở đây;
không để lịch, thi, tài liệu, tài khoản phục hồi chỉ là nút hoặc mô hình mẫu.
Các chương chuyên đề01–28 là chỗ tra khi vướng đúng việc, không phải một
danh sách phải đọc thuộc trước khi được code.

Sau khi các luồng đúng, học [P2](25-hieu-nang-chiu-tai.md) để chốt workload và
đo chịu tải; [P3](26-trien-khai-ci-cd.md) để dựng môi trường khác/release;
[P4](27-bao-mat-va-van-hanh.md) để phiên, quan sát và phục hồi;
[P5](28-do-an-va-nghiem-thu.md) để bàn giao và nghiệm thu. Không có số user
được đảm bảo từ giáo án. Capacity cần kết quả của source, dữ liệu và môi
trường thực. Mục tiêu học xong là mày biết tự làm **và biết dùng bằng chứng
để nhận ra phần mình còn chưa làm được**.
