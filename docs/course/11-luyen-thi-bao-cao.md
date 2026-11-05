# 11 — Luyện thi toán, thời gian và báo cáo

## Bài 11.1 — Tách đề thi, phiên bản và lượt làm

Question là câu hỏi có cấu trúc; Exam là tập câu; ExamVersion/Snapshot là nội
dung cố định cho một lần phát hành; Attempt là lượt làm của một học sinh;
AttemptAnswer lưu câu trả lời theo câu trong lượt đó. Không dùng chung một bản
ghi câu trả lời cho nhiều lượt làm hoặc âm thầm thay nội dung lượt cũ khi cô sửa đề.

Nếu đảo câu/đáp án, lưu mapping ổn định cho attempt. Đáp án đúng gắn id đáp án,
không gắn nhãn A/B/C/D đang hiển thị. Học sinh refresh phải thấy cùng một lượt và
thứ tự phù hợp. Server giữ đáp án và điểm chưa được công bố, không gửi trong JSON
rồi chỉ ẩn bằng CSS.

## Bài 11.2 — Mỗi dạng câu có schema riêng

| Dạng | Đầu vào cần mô tả | Điểm cần chốt |
|---|---|---|
| Một đáp án | option_id thuộc câu hiện tại | Bỏ trống, chọn id không tồn tại |
| Đúng/sai nhiều ý | subquestion_id và boolean cho từng ý | Thiếu ý, chấm từng ý hay theo tổ hợp |
| Trả lời số | Chuỗi đáp án theo định dạng đã chọn | Dấu thập phân, khoảng trắng, phân số, sai số, làm tròn |
| Tự luận | Văn bản/file theo giới hạn | Chấm tay, thang điểm và phản hồi |

Đặc tả theo yêu cầu thực tế của cô. Không suy luận cách chấm của một kỳ thi chỉ
từ giao diện mẫu. Làm một dạng chạy trọn trước khi thêm tất cả dạng khác.

## Bài 11.3 — Ví dụ chấm số có hợp đồng hẹp

Ví dụ sau nhận số thập phân dùng dấu chấm, có chữ số trước dấu chấm, cho phép
dấu +/-, trim khoảng trắng, không nhận phân số/exponent/NaN/infinity. Điểm đúng
là 1, sai là 0 chỉ để học; không đại diện quy tắc kỳ thi cụ thể.

```python
import re
from decimal import Decimal

def parse_decimal_answer(text: str) -> Decimal:
    normalized = text.strip()
    if len(normalized) > 100 or re.fullmatch(r'[+-]?[0-9]+(?:\.[0-9]+)?', normalized) is None:
        raise ValueError('Định dạng số không hợp lệ')
    return Decimal(normalized)

def grade_numeric(expected: str, answer: str) -> int:
    return int(parse_decimal_answer(expected) == parse_decimal_answer(answer))

assert grade_numeric('0.5', ' 0.50 ') == 1
assert grade_numeric('0.5', '0.6') == 0
```

Không dùng eval để chạy biểu thức học sinh nhập. Muốn chấp nhận `1/2` hay `0,5`
phải thiết kế parser/chuẩn hóa có giới hạn và test thêm. Muốn dùng dung sai cần
chốt absolute/relative tolerance, khoảng hợp lệ và thứ tự làm tròn; không tự coi
mọi số gần nhau là đúng.

## Bài 11.4 — Tổng điểm và đa hình

Mỗi grader trả kết quả theo cùng hợp đồng: điểm đạt, điểm tối đa, trạng thái
được chấm; không có grader trả string và grader khác trả float tùy ý.
Dùng Decimal khi quy tắc thập phân cần chính xác; chỉ định làm tròn ở bước nào.
Nếu thay đổi quy tắc chấm, lưu version và có quy trình chấm lại/giữ lịch sử.

Một cấu trúc đề xuất:

```text
GradingService
  chọn grader theo question.type đã được server kiểm tra
  kiểm tra answer thuộc đúng question/attempt
  grader trả GradeResult
  cộng theo trọng số/quy tắc đã chốt
  lưu kết quả nhất quán trong transaction
```

Chọn grader có thể bắt đầu bằng mapping nhỏ. Factory nhiều tầng chỉ cần khi
độ phức tạp thực sự đòi hỏi. Frontend hiển thị định dạng điểm; server tính điểm.

## Bài 11.5 — Đồng hồ và lưu tiến độ

Server xác định started_at, deadline và quyền tạo lượt. Frontend đếm ngược từ
deadline để hiển thị; sửa giờ máy/JavaScript không được kéo dài quyền nộp.
Chốt ai kết thúc attempt khi hết giờ: server job hoặc cơ chế finalize khi truy
cập/xử lý tiếp; phải có đường xử lý cả khi trình duyệt đã đóng.

Autosave cần phân biệt draft và nộp cuối. Giới hạn tần suất, gắn attempt id và
version/request sequencing để response cũ không ghi đè câu trả lời mới. Retry
phải an toàn, không tạo lượt mới. Khi mất mạng, UI nói rõ phần nào server đã xác
nhận; trạng thái local không thay thế dữ liệu server.

Kiểm thử mốc deadline trước/đúng/sau, hai tab, reload, đóng trình duyệt, mất mạng,
gửi lặp và client clock sai. Đừng chỉ test đồng hồ giảm từ 10 về 0.

## Bài 11.6 — Render toán và nội dung do người dùng tạo

Biểu thức LaTeX/KaTeX là định dạng hiển thị, không tự là bộ giải/chấm toán.
Thiết kế cách lưu nội dung text và math, giới hạn kích thước, xử lý lỗi render.
Không đưa HTML không tin cậy vào dangerouslySetInnerHTML mà không có cơ chế
sanitize phù hợp. File hình và tài liệu có quyền xem riêng, không chỉ che link.

## Bài 11.7 — Báo cáo có mẫu số và nguồn rõ

Ví dụ 6 câu đúng trên 10 câu được giao nhưng chỉ làm 8 câu:

- Theo toàn bài: 6/10 = 60%.
- Theo câu đã làm: 6/8 = 75%.

Cả hai có thể có ý nghĩa khác nhau; báo cáo phải ghi cách tính. Chọn lượt đầu,
lượt cuối hay lượt cao nhất cũng cho kết quả khác. Không cộng mọi lượt rồi nói
đó là năng lực duy nhất của học sinh.

Với chuyên đề: cần gắn tag câu hỏi từ nguồn tin cậy, nêu số câu/lượt làm và khoảng
thời gian. Hai câu sai chưa đủ để gắn nhãn chắc chắn một em yếu cả chương.
Sổ câu sai có thể bắt đầu bằng truy vấn câu sai theo user/chuyên đề; đề xuất ôn
theo quy tắc rõ, chưa cần mô hình AI để làm bản đầu có ích.

## Bài tự viết

- **EX1:** một câu MCQ với option id; đảo thứ tự nhưng chấm vẫn đúng.
- **EX2:** numeric grader theo hợp đồng hẹp, test 0, âm, whitespace, comma,
  phân số, NaN, exponent, chuỗi rất dài và dữ liệu thiếu.
- **EX3:** sửa câu hỏi đã phát hành; chứng minh lượt cũ vẫn gắn đúng phiên bản.
- **EX4:** autosave hai request về ngược thứ tự; thiết kế để không mất câu mới.
- **EX5:** tính tay báo cáo từ 3 lượt làm, so với query; chốt mẫu số.
- **EX6:** học sinh chưa được xem lời giải; kiểm tra response thật không chứa đáp án.

Qua chương khi kết quả có thể tái lập và giải thích, không phụ thuộc việc client
gửi điểm/giờ/đáp án đúng. Đưa quy tắc cụ thể cho cô duyệt trước khi dùng thật.

## Xưởng — Thiết kế một dạng câu hỏi từ đầu

Bắt đầu single choice, chưa làm mọi dạng toán cùng lúc. Dữ liệu tách question
version,options,correct option restricted,attempt,attemptanswer. Khi bắt đầu lượt,
chốt question version và thứ tự hiển thị; đổi ngân hàng không làm đổi đề đang thi.
Nếu đáp án nhiều lựa chọn, equality theo tập hay chấm phần phải được định nghĩa.

```text
Start → kiểm user/quyền/giới hạn lượt → server tạo started_at/deadline
Save → kiểm attempt owner/status/time + version câu trả lời
Submit → chốt một lần theo policy → tính điểm từ đáp án server
Publish → học sinh nhận field được phép sau công bố
```

Client countdown chỉ hiển thị. Chốt thời điểm server kiểm hạn và hành vi khi
request đang xử lý/đứt mạng. Autosave dùng revision/sequence hoặc cơ chế đã chốt
để request cũ không ghi đè mới; hai lần submit cần idempotency/quy tắc trạng thái.

## Xưởng — Nội dung toán và thống kê có nghĩa

LaTeX là một cách biểu diễn công thức; cần renderer như KaTeX/MathJax nếu sản
phẩm chọn dùng, hiện chưa nằm trong frontendmanifest. Richtext/math input cần
schema,nội dung được phép,preview và kiểm XSS; không đưa HTML tùy ý vào DOM.
Đáp án số cần hợp đồng dấu thập phân,phân số,đơn vị,tolerance và làm tròn.
Không dùng eval để chấm biểu thức người dùng. Symbolic grading là phạm vi riêng.

Ví dụ đúng 6/đã làm 8/tổng 10: accuracy phần làm75%, hoàn thành80%, đúngtoànbài60%.
Không gắn nhãn chung “tỉ lệ đúng” mà không định nghĩa. Chọn best/latest/first
attempt,thời gian/câu,timezone và sample size; học sinh không có bài khác điểm 0.

**Điền:** chấm một lượt fixture có câu sai/chưa làm. **Trắng:** tạo flow thi
single choice với serverclock và responsekhông lộ đáp án. **Sửa lỗi:** sửa câu hỏi
ngân hàng làm kết quả cũ thay đổi; thiết kế snapshot/version và test tái lập.
