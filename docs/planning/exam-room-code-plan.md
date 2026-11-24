# Kế hoạch code Phòng thi ảo

Cập nhật ngày 24/11/2026. Thực thi [thiết kế Phòng thi ảo](../design/exam-room.md), gồm [xử lý đồng thời](../design/exam-room-concurrency.md) và [nhập đề chính xác](../design/exam-room-import.md). Thay thế mục "Kế hoạch thực thi đến 19/12" (các lát L0–L8) trong [bản kế hoạch docx/pdf](Ke-hoach-Phong-thi-ao.pdf); bản docx chưa được cập nhật theo tài liệu này.

## 1. Kết luận trước

1. **Hạ tầng đã sẵn sàng** để viết mã miền (112 test qua gồm cả MySQL, CI đã viết, đã đo các điểm nghẽn có thể đo trên máy dev). Chưa có dòng mã nào của phòng thi.
2. **Khối lượng thật vượt xa quỹ thời gian của một người.** Ước tính công việc lõi khoảng **126 giờ**, cộng đường nhập đề đáng tin khoảng **48 giờ**. Người dùng code khoảng 1 giờ mỗi ngày, tức khoảng 26 giờ từ nay tới 19/12. Vì vậy kế hoạch này giả định **trợ lý viết phần lớn mã, người dùng viết đường nóng cốt lõi và duyệt mọi thứ**, và đưa ra **đường cắt phạm vi** rõ ràng (mục 3).
3. **Đọc đề chính xác và xử lý đồng thời là hai đường chạy song song**, không phải nối tiếp. Đồng thời nằm trên đường găng của ca thi; nhập đề quyết định cô có dùng được hệ thống hay không.
4. **Mốc 19/12 có rủi ro.** Mức đạt chắc chắn là một ca thi thật nhỏ (một lớp) từ đề PDF dạng phiếu hoặc từ XLSX theo mẫu, với bài làm không mất dưới các ca tranh chấp đã liệt kê. Đủ 500 em và đọc DOCX tự do là mục tiêu của mốc sau nếu số đo chưa đạt.

> Thay đổi so với quyết định đã chọn theo ủy quyền trước đó ("chỉ làm M0–M3 cho PDF trước 19/12"): vì người dùng nhấn mạnh việc đọc **PDF, DOCX và XLSX chính xác**, đường nhập đề được đưa lên song song ngay từ tuần đầu (XLSX và phiếu PDF trước, DOCX sau khi có bộ đề vàng). Phần dùng AI, đọc PDF tự động và trộn đề vẫn sau 19/12.

## 2. Hiện trạng

| Thành phần | Trạng thái |
| --- | --- |
| Hạ tầng backend | Xong: `DbSession`, pool tường minh, giới hạn đăng nhập, `/health`, middleware ASGI, logger, cấu hình có kiểm tra, token có phạm vi, quy ước thời gian |
| Kiểm chứng | 112 test qua trên MySQL 8.0.46 thật (gồm hai ca tranh chấp), `alembic check` sạch, CI chưa chạy trên GitHub |
| Khung mã phòng thi | 86 file rỗng đã tạo theo [cây thư mục](../design/exam-room.md#13-cấu-trúc-thư-mục) |
| Mã miền phòng thi | Chưa có: model, migration, API, giao diện |
| Spike | DOCX đọc đúng 12/12 + 8/12 ý; PDF tìm đúng 44/44 mốc câu. Script nằm ngoài repo (thư mục tạm của phiên làm việc), cần chuyển thành mã chính thức ở ticket P5 |
| Chưa quyết với cô | Ân hạn nộp, đổi thiết bị, thang điểm, tệp XLSX mẫu, tệp `.doc` thật, cho phép đưa tệp đề vào repo |

## 3. Phạm vi theo bậc

| Bậc | Nội dung | Điều kiện để gọi là xong |
| --- | --- | --- |
| **1 · Bắt buộc cho ca thi thật nhỏ** | P0, P1, P2 (không cần `secure_link`: API phát ảnh trang có kiểm token), phiếu PDF, XLSX theo mẫu (P5.1–P5.3) | Cô tạo kỳ thi, một lớp làm và nộp, không mất bài ở 23 ca tranh chấp, đối soát đúng |
| **2 · Cần để đủ 500 em** | P3, P4, `secure_link` của Nginx, DOCX có bộ đề vàng (P5.4–P5.6) | Số đo k6 đạt ngưỡng; DOCX "sai không cờ = 0" trên bộ đề vàng |
| **3 · Sau 19/12** | Công thức MTEF, PDF gợi ý cấu trúc, `.doc`, AI, trộn đề, thống kê sâu | |

**Dấu hiệu cắt.** Cuối mỗi cổng kiểm (mục 4), nếu trễ quá 1 ngày so với lịch thì cắt theo thứ tự: (a) FE giám sát chi tiết (giữ API), (b) `secure_link` (giữ API phát ảnh), (c) DOCX (giữ XLSX và phiếu PDF), (d) kết quả cho học sinh (giữ kết quả cho cô). **Không bao giờ cắt**: test tranh chấp, đối soát, biên nhận, thiết kế gửi lặp.

## 4. Lịch và cổng kiểm

| Tuần | Làm | Cổng kiểm cuối tuần |
| --- | --- | --- |
| **25/11 – 1/12** | P0 chuẩn bị, P1 dữ liệu và tạo kỳ thi, P5.1 tải tệp an toàn | **G1 (1/12):** cô tạo kỳ thi nháp từ PDF, lưu khi thiếu một đáp án, mở lại đúng; phát hành bị từ chối và chỉ đúng chỗ thiếu; điền đủ thì phát hành được và bấm lần hai trả cùng trạng thái |
| **2/12 – 8/12** | P2.1–P2.5 lõi làm bài, P2.7–P2.8 FE danh sách và phòng chờ, P5.2–P5.3 phiếu PDF và XLSX | **G2 (8/12):** 23 test tranh chấp xanh trên MySQL; học sinh thử: tắt Wi-Fi, sửa hai câu, F5, mở lại thấy đúng đồng hồ và đáp án; nộp hai lần cùng biên nhận; token đăng nhập hết hạn giữa giờ vẫn làm tiếp được |
| **9/12 – 15/12** | P2.6 ảnh trang, P2.9 FE trình làm bài, P3 coi thi và kết quả, P5.4–P5.6 DOCX và bộ đề vàng | **G3 (15/12):** thí điểm nội bộ cả luồng; DOCX của cô qua `evaluate` với sai không cờ = 0 |
| **16/12 – 19/12** | P4 đo tải, diễn tập phục hồi, thí điểm một lớp | **G4 (19/12):** báo cáo k6 và đối soát; một ca thi thật với một lớp |

Nếu cổng nào không đạt, ghi rõ vào `PROJECT_CONTEXT.md` phần đã đạt, phần chưa và phạm vi đã thử, rồi tiếp tục thí điểm nhỏ thay vì công bố khả năng chưa kiểm chứng.

## 5. Quy trình cho mỗi ticket

**Định nghĩa hoàn thành (DoD) chung:**

1. Mã theo quy ước repo (BE: router, service lớp nhận repository qua constructor, repository; FE: `pages/components/services/types/schemas` gần nơi dùng).
2. Có test: SQLite cho logic, **MySQL cho mọi thứ liên quan khóa, đồng thời, `rowcount`, ràng buộc**.
3. `alembic check` sạch trên DB test nếu đổi schema; migration chạy từ DB trống.
4. `pytest` (cả cờ MySQL), `tsc`, `eslint`, `next build` đều qua.
5. Câu SQL hot path có test chứng minh **một lần mượn, một câu** (đếm sự kiện `checkout` và câu lệnh).
6. Cập nhật `PROJECT_CONTEXT.md`: điều đã làm, điều đã kiểm, điều chưa.

**Cột "Ai":** **B** = người dùng tự viết (đường nóng, để học và để bảo vệ trong phỏng vấn), **T** = trợ lý viết, người dùng duyệt và chạy kiểm chứng, **C** = cần cô.

## 6. Ticket

### P0 · Chuẩn bị (khoảng 8 giờ)

| ID | Việc | File | Test và cách kiểm | Giờ | Ai |
| --- | --- | --- | --- | --- | --- |
| P0.1 | Hết chờ pool thành `503` + `Retry-After: 2` (không phải `500`) | `app/core/error_middleware.py` | `test_pool_timeout_returns_503_with_retry_after`: ép pool một kết nối rồi chiếm giữ | 1 | T |
| P0.2 | Khẳng định `rowcount` là số dòng khớp | `tests/test_exam_rowcount.py` | MySQL: UPDATE đặt cùng giá trị vẫn trả 1 dòng | 0,5 | T |
| P0.3 | Công cụ test đồng thời | `tests/helpers/concurrency.py` | Chạy N luồng bằng `Barrier`, mỗi luồng một kết nối; tự kiểm bằng test mẫu 2 luồng | 2 | T |
| P0.4 | Nút đăng xuất rõ ràng, xóa token (máy dùng chung) | `components/layout/*` | Kiểm tay: đăng xuất rồi mở lại trang không vào được | 1 | B |
| P0.5 | Đổi `ACCESS_TOKEN_EXPIRE_MINUTES=180` trong `backend/.env` | `.env` | | 0,1 | B |
| P0.6 | Lập `expected.json` cho hai tệp spike (vectơ DOCX, mặt cầu PDF) | `tests/golden_private/` | Chạy lại spike, so đúng | 2 | B + C |
| P0.7 | Hỏi cô: ân hạn, đổi máy, thang điểm, mẫu XLSX, `.doc`, tệp có đưa vào repo | tài liệu | Ghi câu trả lời vào `PROJECT_CONTEXT.md` | 0,5 | B + C |

### P1 · Dữ liệu và tạo kỳ thi (khoảng 32 giờ)

| ID | Việc | File chính | Test | Giờ | Ai |
| --- | --- | --- | --- | --- | --- |
| P1.1 | Model và migration cho 9 bảng ([mục 4](../design/exam-room.md#4-mô-hình-dữ-liệu)) | `models/exam.py`, `alembic/versions/*` | Ràng buộc: `UNIQUE(exam_id, student_id)`, `UNIQUE(owner_id, sha256)`, `UNIQUE(receipt_code)`, khóa ngoại; `alembic check`; migration từ DB trống | 4 | T |
| P1.2 | Domain thuần: IR (pydantic), khóa đáp án và tính `missing`, `compute_deadline`, `is_within_grace`, mã biên nhận và `content_digest` | `modules/exams/domain/*` | Khoảng 30 test đơn vị: vào muộn 08:45 phòng 08:00–10:00 bài 90 phút thì hạn 10:00; `missing` đúng vị trí; mã không trùng | 4 | T |
| P1.3 | Tải tệp: nhận luồng, kiểm byte đầu, giới hạn, `sha256`, trùng tệp | `modules/exams/files/*`, `exam_import/detect.py`, `safety.py` | Đổi đuôi `.exe` thành `.pdf` bị `415`; quá 50 MB bị `413`; tải trùng dùng lại; tải trùng đồng thời (ca 19) | 4 | T |
| P1.4 | Đề và đáp án: CRUD nháp, `If-Match`, lưu thiếu đáp án được, khóa đề | `modules/exams/papers/*` | Hai tab sửa: tab thứ hai `409`; sửa đề đã khóa `423` | 4 | T |
| P1.5 | Kỳ thi: tạo, sửa, người dự thi (lớp theo khối và học sinh theo tên, hợp nhất theo ID), **phát hành là một giao dịch** | `modules/exams/create_exam/*` | Phát hành thiếu đáp án `422` kèm vị trí (ca 17); phát hành đúng lúc sửa (ca 16); thêm người trùng đồng thời (ca 18); phát hành lặp trả cùng trạng thái | 6 | T |
| P1.6 | FE giáo viên: trang Tạo kỳ thi (port từ bản HTML), tải tệp, chế độ phiếu PDF, nhập đáp án, nút phát hành dẫn tới ô còn thiếu | `features/teacher/exams/create_exam/*`, `papers/*` | Kiểm tay trên Chrome; lint, tsc | 10 | T |
| P1.7 | Route và điều hướng "Phòng thi ảo" trong sidebar giáo viên | `app/(teacher)/teacher-exams/*` | Mở từ sidebar | 1 | T |

### P2 · Lõi làm bài (khoảng 48 giờ)

Đây là phần đề xuất người dùng tự viết các ticket P2.2–P2.4 (bắt đầu, lưu, nộp): có giao dịch, khóa dòng và gửi lặp, và là phần có giá trị nhất khi phỏng vấn.

| ID | Việc | File chính | Test | Giờ | Ai |
| --- | --- | --- | --- | --- | --- |
| P2.1 | Token lượt thi và `require_attempt_access` (kiểm phạm vi và `attempt_id` khớp đường dẫn) | `attempts/token.py`, `core/dependencies.py` | Token đăng nhập dùng trên `/student/attempts/*` bị từ chối và ngược lại; hết hạn; sai `attempt_id` | 2 | T |
| P2.2 | **Bắt đầu hoặc tiếp tục** ([SQL mục 4.1](../design/exam-room-concurrency.md#41-bắt-đầu-hoặc-tiếp-tục)) | `attempts/service.py`, `repository.py` | Ca 1 (20 luồng cùng một em), ca 2 (nhiều em), `403` không có tên, `425` chưa mở, `410` đã đóng, hạn bằng `compute_deadline`, `takeover_required` | 4 | **B** |
| P2.3 | **Lưu bài**: một câu UPDATE, chẩn đoán lỗi ([mục 4.2](../design/exam-room-concurrency.md#42-lưu-bài-một-lần-mượn-một-câu)) | như trên | Ca 3–9; **đếm đúng 1 lần mượn, 1 câu lệnh ở đường thành công** | 4 | **B** |
| P2.4 | **Nộp và chấm**: khóa dòng, chốt, biên nhận, lịch sử chấm ([mục 4.3](../design/exam-room-concurrency.md#43-nộp-bài-và-chấm)) | như trên + `domain/grading.py` | Ca 10–14; chấm trắc nghiệm, đúng/sai theo ý, trả lời ngắn (chuẩn hóa dấu phẩy, dấu trừ Unicode, `1/2`); nộp trong ân hạn và sau ân hạn | 7 | **B** + T cho `grading` |
| P2.5 | Quét chốt lượt quá hạn: hàm chốt dùng chung, CLI, `systemd timer` | `jobs/sweep_attempts.py`, `deploy/systemd/` | Ca 12; lô 100 dòng; không đụng lượt còn trong ân hạn; chạy hai bản cùng lúc không trùng | 2 | T |
| P2.6 | Ảnh trang: dựng WebP lúc phát hành, thêm watermark tên, API phát ảnh có kiểm token (bản đầu); `secure_link` ở bậc 2 | `files/service.py`, `exam_import/pdf_reader.py`, `deploy/nginx/` | Học sinh ngoài danh sách không đọc được; ảnh chỉ gồm các trang được chọn; lời giải không lọt | 5 | T |
| P2.7 | API học sinh: danh sách kỳ thi, phòng chờ (`server_now`, giờ mở, quy định) | `attempts/router.py` | `server_now` có offset `+07:00` | 2 | T |
| P2.8 | FE học sinh: danh sách, phòng chờ, đồng hồ từ `server_now`, jitter khi bấm Bắt đầu | `features/student/exams/room/*`, `hooks/useServerClock.ts` | Giả lập máy lệch 10 phút vẫn đếm đúng | 5 | T |
| P2.9 | FE trình làm bài: reducer, `draftStore`, hàng đợi một chuyến bay, chờ lùi có nhiễu, phiếu trả lời, xem ảnh trang, hộp nộp, biên nhận, `navigator.locks` | `features/student/exams/attempt/*`, `receipt/*` | Kiểm tay theo kịch bản G2; điện thoại thật | 14 | T |
| P2.10 | Test FE cho reducer và hàng đợi lưu (thêm `vitest`) | `store/attemptReducer.test.ts` | Gửi lặp, `409` có đáp án bằng bản mình thì coi là thành công, mất mạng | 3 | T |

**Thứ tự phụ thuộc:** P1.1, P1.2 → P2.1 → P2.2 → P2.3 → P2.4 → P2.5. P2.6 và P2.7 song song sau P1.5.

### P3 · Coi thi và kết quả (khoảng 18 giờ)

| ID | Việc | Test | Giờ | Ai |
| --- | --- | --- | --- | --- |
| P3.1 | Ghi sự kiện (kèm lần lưu) và endpoint dùng cho `sendBeacon` (token trong thân yêu cầu) | Mất sự kiện không làm mất bài; sự kiện có giờ máy và giờ máy chủ | 3 | T |
| P3.2 | `GET progress`: tổng hợp một truy vấn, `ETag`, cache 3 giây trong tiến trình | Ca 23; 500 lượt trả dưới 100 ms (đo trên MySQL) | 3 | T |
| P3.3 | Kết quả, chấm lại (idempotent), gia hạn theo lượt, quyết định bài gửi muộn | Ca 14, 22; gia hạn ghi lý do | 5 | T |
| P3.4 | FE giám sát và kết quả: bảng em, "liên lạc lần cuối", dòng sự kiện, bộ lọc "Cần chú ý", hộp gửi muộn | Kiểm tay; phân biệt được bài đã nộp, em cần hỗ trợ, sự kiện cần xem | 7 | T |

### P4 · Tải và thí điểm (khoảng 20 giờ)

| ID | Việc | Cách kiểm | Giờ | Ai |
| --- | --- | --- | --- | --- |
| P4.1 | Kịch bản k6 (6 kịch bản ở [mục 8.2](../design/exam-room-concurrency.md#82-tải-bằng-k6-m3-từ-máy-khác-trên-vps-thật)) và `scripts/exam_reconcile.py` | Chạy thử với 20 tài khoản trên máy dev, công cụ đối soát phát hiện được lỗi cố tình chèn | 6 | T |
| P4.2 | Dựng VPS theo `deploy/`, Nginx `secure_link`, sao lưu ngoài VPS, **diễn tập khôi phục** | Khôi phục vào môi trường riêng rồi tính lại điểm một lượt từ bản nộp | 6 | B + T |
| P4.3 | Chạy các kịch bản trên VPS thật từ máy khác, sửa lỗi, A/B `h11` với `httptools`/`uvloop`, quyết định số worker và pool | Đạt ngưỡng, hoặc ghi rõ phạm vi đã thử | 6 | B + T |
| P4.4 | Thí điểm một lớp có cô coi thi; viết sổ tay sự cố | Ghi số chỗ phải nhờ hướng dẫn | 2 | B + C |

### P5 · Nhập đề (đường song song, khoảng 48 giờ cho phần đáng tin)

| ID | Việc | File chính | Test | Giờ | Ai |
| --- | --- | --- | --- | --- | --- |
| P5.1 | An toàn tải lên (cùng P1.3): bom nén, XXE, macro, tiến trình con có giới hạn | `exam_import/safety.py` | Bom nén bị từ chối; `.xlsm` bị từ chối; XML có thực thể ngoài không đọc được tệp cục bộ | 3 | T |
| P5.2 | Phiếu PDF: dựng ảnh trang, trang nào phát, trang lời giải bị loại | `exam_import/pdf_reader.py` | Ảnh khớp trang; trang bị loại không có trong gói | 3 | T |
| P5.3 | **XLSX theo mẫu**: tệp mẫu tải về, bộ đọc theo tên cột, gom hết lỗi một lần | `exam_import/xlsx_reader.py` | Mỗi loại lỗi một test; `Sheet "Đề", dòng 16: thiếu phương án C`; dòng hợp lệ vẫn được giữ | 8 | T + C duyệt mẫu |
| P5.4 | Worker nhập đề và API job: `SKIP LOCKED`, gia hạn `locked_until`, tiến trình con, giới hạn, tạm dừng khi có kỳ thi mở | `workers/exam_import_worker.py`, `imports/*` | Ca 20, 21; job quá thời gian thành `failed` rõ ràng | 6 | T |
| P5.5 | **DOCX**: chuyển spike thành mã chính thức (mốc câu, loại theo từng câu, phương án, đúng/sai, đáp án gợi ý, loại lời giải, cờ) | `exam_import/docx_reader.py`, `validators.py` | Tệp vectơ: 12/12 và 8/8, 52 đoạn lời giải bị loại, 2 câu không xác định bị gắn cờ; test "không lộ đáp án" | 10 | T |
| P5.6 | **Bộ đề vàng và `evaluate`**: lập `expected.json`, báo cáo chỉ số, cổng CI | `exam_import/evaluate.py` | Sai không cờ = 0; thử bằng cách cố ý sửa bộ đọc cho sai và thấy cổng đỏ | 5 | T + C |
| P5.7 | FE nhập đề: vùng thả tệp, tiến độ, **màn duyệt** (nội dung cạnh ảnh gốc, cờ, xác nhận đáp án gợi ý, khóa "Dùng đề này" khi còn lỗi chặn) | `features/teacher/exams/import/*` | Kiểm tay với tệp vectơ | 14 | T |
| P5.8 | Công thức: WMF/EMF sang PNG trên máy chủ, cache theo `sha256`, cờ `W_FORMULA_UNCONVERTED` chặn phát hành | `exam_import/formulas.py` | Không ảnh đen hoặc trống (đã từng gặp ở bản thử); đo thời gian chuyển trên VPS | 8 | T |

Từ P5.1 đến P5.3 thuộc bậc 1, từ P5.4 đến P5.8 thuộc bậc 2. Sau 19/12: PDF gợi ý cấu trúc (khoảng 6 giờ), `.doc` (4), AI (8), trộn đề (10).

## 7. Câu hỏi phỏng vấn gắn với ticket

Mỗi nhóm có một câu để người dùng tự trả lời sau khi làm xong (mô phỏng người hỏi khó tính: được hỏi vặn nếu trả lời mơ hồ).

| Nhóm | Câu hỏi |
| --- | --- |
| P2.2 | Hai tab cùng bấm Bắt đầu. `INSERT … ON DUPLICATE KEY UPDATE id = id` khác gì với "SELECT rồi INSERT nếu chưa có"? Giá trị `deadline_at` của lượt thứ hai là gì và vì sao? |
| P2.3 | `rowcount` của một UPDATE trả 0 thì có những nguyên nhân nào? Vì sao cần truy vấn chẩn đoán riêng, và vì sao không đưa nó vào đường thành công? |
| P2.4 | Chứng minh bằng ví dụ có hai giao dịch xen kẽ rằng "SELECT … FOR UPDATE" tránh được hai biên nhận. Điều gì xảy ra nếu bạn quên `FOR UPDATE` ở REPEATABLE READ? |
| P2.5 | `SKIP LOCKED` khác gì `NOWAIT`? Vì sao bộ quét dùng `SKIP LOCKED` còn đường nộp dùng khóa chờ? |
| P5.3 | Vì sao đọc XLSX theo tên cột thay cho vị trí? Một ô công thức Excel chưa có giá trị đã tính sẽ làm bộ đọc ra sao, và bạn xử lý thế nào? |
| P5.5 | Câu 11 của đề vectơ tô vàng cả phương án thay vì tô nhãn. Quy tắc nào của bộ đọc làm nó đúng, và quy tắc đó có thể sai trong tình huống nào? |
| P5.6 | "Sai không cờ = 0" khác "độ chính xác 100%" ở điểm nào? Vì sao cổng 100% trên bộ đề vàng chưa đủ để tin bộ đọc? |
| P4.3 | Đuôi trễ 2 giây xuất hiện kể cả ở `/health` không đụng DB. Bạn phân biệt giới hạn của máy phát tải với giới hạn của máy chủ bằng cách nào? |

## 8. Rủi ro

| Rủi ro | Khả năng và ảnh hưởng | Giảm thiểu |
| --- | --- | --- |
| Quỹ thời gian nhỏ hơn khối lượng | **Cao.** Đã nêu ở mục 1 | Bậc phạm vi, dấu hiệu cắt, trợ lý viết phần lớn mã |
| Cô chưa quyết quy chế | Trung bình. Chặn mã `EXAM_GRACE_SECONDS`, `takeover`, `scoring` | P0.7 hỏi ngay tuần đầu; mã nhận giá trị từ cấu hình để đổi không cần sửa code |
| Chuyển WMF/EMF sang PNG trên Linux kém chất lượng | Trung bình. Công thức sai hoặc đen | P5.8 đo trên máy chủ thật cùng bộ đề vàng; công thức không chuyển được chặn phát hành |
| LibreOffice tốn RAM trên VPS 4 GB | Trung bình | Chạy một việc mỗi lúc, tiến trình con có giới hạn, tạm dừng khi có kỳ thi mở |
| Tốc độ commit trên đĩa VPS thấp | Chưa biết. Ảnh hưởng lúc nộp dồn | Đo ở P4.3; giữ `innodb_flush_log_at_trx_commit=1` trừ khi cô chấp nhận rủi ro mất tối đa một giây |
| Băng thông cổng mạng VPS thấp | Chưa biết | Hỏi nhà cung cấp tuần đầu; `secure_link` và tải từng trang; phương án kho riêng |
| iOS tạm dừng JavaScript khi tắt màn hình | Chắc chắn xảy ra | Đồng hồ tính từ `deadline_at`, không đếm giảm; thử trên iPhone thật |
| CI chạy đỏ lần đầu | Cao nhưng rẻ | Push một nhánh nhỏ trước, sửa trước khi có nhiều mã |
| Đề tự do của cô có kiểu chưa gặp | Cao theo thời gian | Cờ và màn duyệt; mỗi tệp mới sai không cờ được thêm vào bộ đề vàng |
| Giấy phép PyMuPDF | Thấp nếu tránh dùng | Dùng `pypdfium2` và `pdfminer.six` |

## 9. Việc người dùng cần làm ngay (không chờ mã)

1. Bật CI: push một nhánh nhỏ, xem workflow chạy.
2. Gửi cô các câu ở P0.7, kèm hai tệp mẫu `.xlsx` và `.doc` thật nếu có.
3. Đổi `ACCESS_TOKEN_EXPIRE_MINUTES=180` trong `backend/.env`.
4. Xác nhận ba điều: (a) kế hoạch hai đường song song và các bậc phạm vi ở mục 3; (b) phân công **B** cho P2.2–P2.4; (c) có cho phép đưa tệp đề của cô vào repo hay chỉ giữ `expected.json`.
