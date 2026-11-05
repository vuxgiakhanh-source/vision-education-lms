# P5 — Đồ án được đánh giá bằng sản phẩm và bằng chứng

Đầu ra: một phiên bản có phạm vi chốt, demo dùng được và hồ sơ để người khác
đánh giá. Không có thang điểm nội bộ nào bảo đảm điểm của mọi hội đồng hay
phản hồi của mọi người dùng; chốt rubric thật khi nhận đề.

## 1. Hồ sơ tối thiểu để reviewer không cần đoán

| Hồ sơ | Phải trả lời được |
|---|---|
| Product brief | Ai dùng, giải quyết việc gì, bản này có/chưa có gì? |
| Acceptance matrix | Yêu cầu nào được kiểm bằng tình huống nào? |
| ERD + data dictionary | Quan hệ, invariant, thời gian, điểm, retention ra sao? |
| API + permission contract | Ai làm gì với resource nào, lỗi/status nào? |
| ADR | Vì sao chọn kiến trúc/transaction/cache/deployment này? |
| Validation | Đã chạy thật gì, môi trường nào, còn thiếu gì? |
| Performance report | Workload/cấu hình/latency/lỗi/correctness sau tải? |
| Runbook + release record | Bản nào đang chạy, phát hiện lỗi và phục hồi thế nào? |
| README | Người khác cài sạch, chạy test và demo được không? |

Không nộp screenshot đẹp để thay test quyền hoặc report chứa số chưa đo.
Đường link bằng chứng phải gắn đúng commit/version, không dùng kết quả bản cũ
để nghiệm thu một bản đã đổi logic.

## 2. Rubric đề xuất cho đồ án này

| Mảng | Điểm | Bằng chứng cụ thể |
|---|---|---|
| Bài toán và phạm vi | 10 | Rule rõ, quyết định giải thích được, xử lý biến thể |
| Nghiệp vụ và dữ liệu | 25 | Nhiều tài khoản đi hết luồng, invariants đúng |
| UX và accessibility | 15 | Tác vụ thực, keyboard, focus, responsive, lỗi giữ input |
| Kiến trúc và clean code | 15 | Dependency rõ, refactor có tests, diff dễ review |
| Testing và bảo mật | 15 | Negative/scope/transaction/integration, policy phiên |
| Hiệu năng và vận hành | 15 | Đo tải đại diện, deploy/restore có kết quả |
| Bàn giao và bảo vệ | 5 | README sạch, demo + tự sửa thay đổi nhỏ |

Mốc đề xuất: >=80/100 và không có lỗi nghiêm trọng còn mở về đọc chéo, mất bài,
sai điểm hoặc lộ secret trong phạm vi nghiệm thu. Ghi chưa làm được thay vì
dùng điểm ở màn hình khác để bù một invariant quan trọng bị sai.

## 3. Kiểm sản phẩm với người dùng thử

Mời vài người đúng vai trò làm tác vụ cụ thể, không hướng dẫn từng cú bấm:
“giao bài cho lớp này”, “tìm bài và nộp”, “chấm nhưng chưa cho học sinh xem”.
Ghi hoàn thành/không, thời gian, lỗi và chỗ cần trợ giúp. Dùng dữ liệu giả.

Quan sát người dùng có biết trạng thái đã lưu/chưa lưu, sửa lỗi được không,
hiểu deadline/điểm công bố không. Sau sửa thử lại cùng tác vụ. Phản hồi ít người
giúp tìm vấn đề UX, chưa chứng minh mọi nhóm người dùng đều hài lòng.

## 4. Accessibility phải được thao tác

Test toàn luồng chỉ bằng bàn phím: tab đúng thứ tự, focus thấy rõ, label/error
liên kết input, dialog đóng/mở không mất focus. Kiểm zoom, màn hẹp, text dài,
contrast, reduced motion và thông báo loading/error bằng assistive technology
phù hợp. Đừng dùng màu làm dấu hiệu duy nhất.

Tool tự động giúp phát hiện một phần, chưa thay kiểm thủ công/screen reader.
Ghi thiết bị/browser/công cụ và lỗi còn lại. Mục tiêu chuẩn truy cập cần được
chốt cụ thể theo đề/môi trường, không tự ghi “đạt WCAG” khi chưa đánh giá đủ.

## 5. Chạy buổi demo theo một câu chuyện

1. Nói phạm vi bản này và rule quan trọng, không liệt kê tên thư viện.
2. Cô giao bài thật; học sinh khác profile thấy và nộp; refresh dữ liệu còn.
3. Cô chấm 0 nhưng chưa công bố; mở Network học sinh chứng minh chưa lộ.
4. Công bố rồi xem điểm; gọi API bằng tài khoản ngoài lớp để kiểm từ chối.
5. Gửi lại cùng nội dung, giữ id/giờ; gửi khác nội dung bị conflict.
6. Mở report tải/restore đúng version, nói giới hạn chưa kiểm.

Giữ fixture/seed để demo tái lập; không bấm nút reset trên dữ liệu thật.
Chuẩn bị lỗi mạng để giải thích trạng thái không chắc đã lưu, không giả thành
success. Khi có lỗi, trình bày bằng chứng và giả thuyết thay vì giấu đi.

## 6. Buổi bảo vệ có thay đổi yêu cầu

Reviewer chọn một trong các đề:

- Trợ giảng chỉ chấm một nhóm trong lớp.
- Cho nộp muộn có phép nhưng không đổi timestamp bản đã xác nhận.
- Thêm điểm Decimal và lịch sử chấm lại.
- Công bố theo đợt, thu hồi giữa lúc học sinh đang tải.
- Nhiều người cùng nộp đúng hạn; tối ưu lock mà giữ correctness.

Trước sửa phải chỉ tác động đến schema, quyền, transaction, DTO, UI, test và
migration. Viết một test phản chứng rồi sửa lát cắt nhỏ. Tra docs được; không
nhận nguyên implementation AI sinh rồi coi là đã chứng minh tự thiết kế.

## 7. Mốc nghiệm thu cuối khóa

**G0 — chức năng:** core loop và module đã chốt qua matrix, không có nút giả.
**G1 — chất lượng:** reviewer đọc được luồng, tests bắt lỗi, cài sạch được.
**G2 — tải:** workload/cấu hình rõ, đủ số đo, không mất/trùng/lộ dữ liệu.
**G3 — vận hành:** staging, release/rollback/restore đã diễn tập và đo.
**G4 — chuyển giao:** tự làm rule mới và người khác chạy README thành công.

Chưa qua mốc nào thì ghi nguyên nhân và việc tiếp theo. Đọc hết sách, tick
checklist hay chạy unit test không tự thay bằng chứng của mốc khác.

## 8. Một việc đầu tiên sau khi đọc

Đừng mở đồng loạt mọi module. Làm P0 bằng hai tài khoản, ghi đúng một lỗi gặp
và tự điều tra. Sau đó refactor P1, MySQL/cạnh tranh/đo tải P2, staging P3 và
runbook/security P4. Mỗi bước hoàn thành có code, kết quả và điều chưa xác nhận.
