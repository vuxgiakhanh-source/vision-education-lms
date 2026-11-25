# Phòng thi ảo: xử lý đồng thời

Cập nhật ngày 24/11/2026. Phần của [thiết kế Phòng thi ảo](exam-room.md). Đây là thiết kế đề xuất cho mã chưa viết. Mọi con số được gắn nhãn **đã đo** (có phép đo trên máy phát triển), **ước tính** (suy ra từ phép tính) hoặc **chưa đo** (phải đo ở M3 trên VPS thật).

## 1. Mười nguyên tắc

1. **Đường nóng là một lần mượn kết nối và một câu lệnh.** Đã đo: `/me` mượn 1 lần, 1 câu; `/schedule/weekly` mượn 2 lần, 3 câu. Lưu bài phải đạt 1 lần, 1 câu.
2. **Không bao giờ khóa dòng dùng chung.** Chỉ khóa dòng lượt thi của chính học sinh đó. Không có `FOR UPDATE` trên bảng `exams` trong đường nóng.
3. **Dữ liệu bất biến thì cache, dữ liệu đổi thì có `version`.** Đề đã phát hành không đổi nên cache trong RAM theo `(paper_id, structure_hash)` là an toàn tuyệt đối.
4. **Mọi thao tác ghi phải lặp lại được.** Gửi lại cùng một yêu cầu cho ra cùng một kết quả (UNIQUE, `request_id`, ảnh chụp đầy đủ thay cho patch).
5. **Máy chủ quyết định đúng/sai, không phải giao diện.** Hạn nộp, quyền ghi, trạng thái lượt đều được kiểm trong chính câu lệnh ghi.
6. **Chỉ báo thành công sau khi commit.** "Đã đồng bộ" và "Đã nộp" chỉ hiện sau phản hồi 200.
7. **Tải dồn thì làm cho lệch nhịp.** Phòng chờ, độ trễ ngẫu nhiên khi thử lại, nhịp lưu 10–20 giây có nhiễu.
8. **Quá tải thì từ chối sớm có hướng dẫn**, không để hàng đợi vô hạn: `503` kèm `Retry-After`.
9. **Việc nặng ở tiến trình khác.** Đọc đề, chuyển công thức, dựng ảnh trang không bao giờ chạy trong worker API.
10. **Mọi tranh chấp có một test chạy trên MySQL thật.** SQLite bỏ qua `FOR UPDATE` nên test SQLite không chứng minh được gì về khóa.

## 2. Ngân sách tải

Giả định: 500 học sinh, ca 90 phút, 4 worker API.

| Thời điểm | Tải | Tài nguyên bị đè | Cách giữ nhẹ |
| --- | --- | --- | --- |
| Trước giờ mở | 500 lượt đăng nhập trong khoảng 10 phút | CPU (bcrypt khoảng 200 ms mỗi lần, **đã đo** trên máy dev) | Mở phòng chờ sớm 15 phút, nhắc đăng nhập sớm |
| Bấm Bắt đầu | 100 yêu cầu mỗi giây trong 5 giây | Kết nối DB, thread | 3 câu nhẹ theo khóa chính, jitter 0–5 giây phía giao diện, cache đề |
| Tải ảnh trang đề | 500 em x N trang | **Băng thông cổng mạng** | Nginx phát tệp, tải từng trang khi cuộn, `Cache-Control` dài |
| Đang làm | Trung bình 33 lần lưu mỗi giây (500 em, 15 giây một lần) | Kết nối DB | Một câu UPDATE theo khóa chính |
| Cả lớp rớt Wi-Fi rồi có lại | Đỉnh 500 yêu cầu cùng lúc | Pool, thread | Chờ lùi dần có nhiễu 0–10 giây, một chuyến bay mỗi máy |
| Nộp cuối giờ | 100 giao dịch mỗi giây trong 5 giây | **Tốc độ ghi đĩa (commit)** | Giao dịch ngắn, chỉ khóa dòng của chính em |
| Sau giờ đóng | Quét chốt các lượt bỏ dở | Khóa dòng | Lô nhỏ 100 dòng, `SKIP LOCKED` |

### Số liệu hiện có

| Phép đo | Kết quả | Môi trường | Ý nghĩa |
| --- | --- | --- | --- |
| Khứ hồi `SELECT 1` tới MySQL | trung vị 0,45 ms, p95 0,76 ms | Docker Desktop, Windows | Chi phí DB của câu theo khóa chính là rất nhỏ |
| Tạo kết nối mới | `localhost` **2.100 ms**; `127.0.0.1` 20–40 ms | Windows | Đã sửa bằng `MYSQL_HOST=127.0.0.1`. Trên Linux VPS có thể khác, phải đo lại |
| Mượn, `SELECT 1`, trả (pre_ping bật) | khoảng 794 lần mỗi giây, một luồng | Windows | |
| `pool_pre_ping` | tốn khoảng 6% thông lượng | 8 luồng | Giữ nguyên, bảo vệ khỏi kết nối chết |
| Kết nối tràn so với pool cố định | thông lượng ngang nhau (2.580 so với 2.541 ops/s); một kết nối mỗi luồng nhanh hơn 22% | 25 luồng, giữ 3 ms | Quyết định ở M3 |
| Middleware bắt lỗi | trước 558 µs, sau 370 µs mỗi request | trong tiến trình | Đã thay bằng ASGI thuần |
| Pool dưới 4 worker | MySQL ghi nhận tối đa 60 kết nối (4 x 15), không lỗi hết kết nối | Windows | Khớp công thức |
| Giới hạn đăng nhập sai song song | 33 phản hồi 401 khớp đúng 33 lần đếm, không mất lần nào | 4 worker, MySQL thật | Đếm nguyên tử đúng; giới hạn là mềm khi bắn song song |
| `/health/ready` ở độ đồng thời 10 | 484 req/s, p95 36 ms | Windows | Endpoint có DB khỏe |
| Ở độ đồng thời 100 | đuôi trễ khoảng 2 giây kể cả `/health` không đụng DB | Windows | **Giới hạn của bộ đo**, không dùng làm số liệu năng lực |

### Chưa đo (phải đo ở M3)

Mọi thứ của đường nóng phòng thi (chưa có mã), băng thông thực của VPS, tốc độ commit khi ghi đĩa VPS, số worker tối ưu, tác dụng của `uvloop` và `httptools` trên Linux, hành vi dưới tải 500 em thật.

### Công thức dùng để thiết kế

Số kết nối đồng thời cần = tốc độ đến x thời gian giữ kết nối (luật Little).

| Đường | Tốc độ | Thời gian giữ (ước tính) | Kết nối cần | Trần 4 x 15 |
| --- | --- | --- | --- | --- |
| Bắt đầu | 100/giây | 6 ms | 0,6 | 60 |
| Lưu bài | 33/giây | 1,5 ms | 0,05 | 60 |
| Nộp | 100/giây | 8 ms | 0,8 | 60 |

Pool không phải điểm nghẽn nếu thời gian giữ ngắn. Nguy cơ thật là **thời gian giữ bị kéo dài**: học sinh mạng chậm (đã xử lý bằng `DbSession`, phiên đóng trước khi gửi byte cuối, đã đo), chờ khóa dòng, đĩa ghi chậm. Vì vậy mỗi đường nóng phải có test đo thời gian giữ.

## 3. Ma trận tranh chấp

Mỗi dòng là một tình huống có thật, cơ chế chống và test chạy trên MySQL.

| # | Tình huống | Bất biến | Cơ chế | Người dùng thấy | Test |
| --- | --- | --- | --- | --- | --- |
| 1 | Bấm Bắt đầu hai lần, hoặc hai tab | Một lượt cho mỗi em, hạn cố định từ lần đầu | `UNIQUE(exam_id, student_id)` + `INSERT … ON DUPLICATE KEY` | Cùng một lượt, cùng hạn | `test_concurrent_start_creates_one_attempt` |
| 2 | 500 em bắt đầu cùng lúc | Mỗi em đúng một lượt, không em nào bị bỏ | Khác dòng nên không tranh dữ liệu; chống quá tải bằng jitter và cache | Vào được trong vài giây | k6 `start_herd` |
| 3 | Hai tab lưu cùng `base_version` | Đúng một bản thắng | `UPDATE … WHERE answers_version = :base` | Tab thua nhận `409` kèm trạng thái máy chủ | `test_sync_two_writers_same_version_exactly_one_wins` |
| 4 | Mất phản hồi, máy gửi lại | Gửi lặp vô hại | Ảnh chụp đầy đủ; nếu `409` mà đáp án máy chủ bằng bản của máy thì coi là thành công | Không thấy gì | `test_sync_replay_after_lost_response_is_adopted` |
| 5 | Gói lưu cũ đến muộn | Không ghi đè bản mới | `answers_version` thấp hơn bị từ chối | Không thấy | `test_stale_sync_never_overwrites_newer` |
| 6 | Lưu sau khi đã nộp | Bài đã nộp không đổi | `status = 'in_progress'` trong điều kiện | `410` kèm biên nhận | `test_sync_after_submit_returns_receipt_and_changes_nothing` |
| 7 | Lưu sau hạn | Không nhận bản lưu muộn làm bài chính thức | `deadline_at >= :now - grace` trong điều kiện | `410`, bản muộn đi vào hộp "gửi muộn" | `test_sync_rejected_after_deadline` |
| 8 | Cô khóa tài khoản giữa ca | Mất quyền ghi ngay | `EXISTS (users.is_active = 1)` trong câu UPDATE | `403 account_locked` | `test_sync_rejected_when_account_locked_between_requests` |
| 9 | Đổi thiết bị | Một thiết bị được ghi | `write_epoch` tăng khi `takeover` | Máy cũ nhận `409 epoch_mismatch` | `test_old_device_cannot_write_after_takeover` |
| 10 | Nộp hai lần cùng lúc | Một biên nhận | `SELECT … FOR UPDATE` trên lượt, lần sau thấy đã nộp | Cùng một biên nhận | `test_submit_twice_concurrently_one_receipt` |
| 11 | Nộp trùng `request_id` nhưng nội dung khác | Không âm thầm đổi bài | So `request_id` và `content_digest` | `409` | `test_submit_same_request_id_different_content_conflicts` |
| 12 | Nộp đúng lúc việc quét chốt | Không chốt hai lần | Cùng khóa dòng; quét chỉ đụng lượt quá `deadline_at + grace` | Một biên nhận | `test_submit_vs_sweeper_race` |
| 13 | Nộp sau ân hạn | Bài chính thức là bản đồng bộ gần nhất | Lưu bản muộn vào `exam_late_submissions` | Quy tắc và cách xin đối soát | `test_submit_after_grace_stores_late_copy` |
| 14 | Cô gia hạn lúc em đang nộp | Dùng hạn đúng tại thời điểm khóa | `extend` cập nhật `deadline_at` theo từng lượt dưới khóa dòng | Nhận hạn mới | `test_extend_during_submit_uses_locked_deadline` |
| 15 | Hai tab cô sửa kỳ thi | Không ghi đè | `exams.version` trong `WHERE`, `If-Match` | `409`, tải lại | `test_exam_edit_two_tabs_second_gets_409` |
| 16 | Cô phát hành đúng lúc sửa | Đề được phát hành đúng là đề đã duyệt | Phát hành trong một giao dịch khóa `exams` và `exam_papers`; đề khóa thì sửa bị `423` | `409` hoặc `423` | `test_publish_vs_edit_race` |
| 17 | Phát hành khi thiếu đáp án | Không mở phòng thiếu đáp án | Tính `missing` trong giao dịch phát hành | `422` kèm vị trí thiếu | `test_publish_lists_missing_answers` |
| 18 | Thêm học sinh đồng thời | Không trùng người | Khóa chính `(exam_id, student_id)` | Một dòng | `test_participants_unique_under_concurrent_add` |
| 19 | Tải cùng tệp hai lần | Một bản lưu | `UNIQUE(owner_id, sha256)` | Dùng lại tệp cũ | `test_upload_same_file_twice_dedupes` |
| 20 | Hai worker nhập đề nhận cùng job | Một worker một job | `SELECT … FOR UPDATE SKIP LOCKED LIMIT 1` | Không thấy | `test_import_job_claimed_by_one_worker` |
| 21 | Worker nhập đề chết giữa chừng | Job không mắc kẹt | `locked_until` hết hạn thì job về `queued` | Job tự chạy lại | `test_import_job_reclaimed_after_worker_death` |
| 22 | Chấm lại đồng thời hoặc lặp | Một kết quả mỗi phiên bản khóa đáp án | Khóa lượt; `UNIQUE(attempt_id, answer_key_version)` | Điểm không đổi | `test_regrade_is_idempotent` |
| 23 | Nhiều tab coi thi | Tải không nhân lên theo số tab | Cache kết quả tổng hợp 3 giây trong tiến trình, `ETag` | Không thấy | `test_progress_is_cached_between_polls` |

Ca 16 và 17 chung quy là hai tính chất: **phát hành là một giao dịch**, và **đề đã khóa thì bất biến**.

## 4. Bốn đường nóng

### 4.1 Bắt đầu hoặc tiếp tục

```sql
-- (1) Quyền và cửa sổ thi: hai tra cứu theo khóa chính trong một câu
SELECT e.id, e.status, e.opens_at, e.closes_at, e.duration_minutes, e.paper_id, e.version
FROM exams e
JOIN exam_participants p ON p.exam_id = e.id AND p.student_id = :uid
WHERE e.id = :exam_id;

-- (2) Tạo lượt. Bấm lặp vẫn chỉ có một dòng. deadline tính một lần ở máy chủ
INSERT INTO exam_attempts
  (exam_id, student_id, started_at, deadline_at, status, answers, answers_version, write_epoch, device_id)
VALUES
  (:exam_id, :uid, :now, LEAST(:closes_at, :now + INTERVAL :minutes MINUTE), 'in_progress', '{}', 0, 1, :device)
ON DUPLICATE KEY UPDATE id = id;

-- (3) Đọc lượt (cũ hoặc vừa tạo)
SELECT id, deadline_at, status, answers, answers_version, write_epoch, device_id, receipt_code
FROM exam_attempts WHERE exam_id = :exam_id AND student_id = :uid;
```

Đề (IR) lấy từ cache theo `(paper_id, structure_hash)`, không truy vấn DB. Nếu `device_id` khác với thiết bị đang ghi và `last_seen_at` còn mới, trả `takeover_required: true` thay vì tự chuyển quyền.

### 4.2 Lưu bài: một lần mượn, một câu

```sql
UPDATE exam_attempts a
SET    a.answers = :answers_json,
       a.answers_version = a.answers_version + 1,
       a.last_sync_at = :now,
       a.last_seen_at = :now
WHERE  a.id = :attempt_id
  AND  a.student_id = :uid
  AND  a.status = 'in_progress'
  AND  a.write_epoch = :epoch
  AND  a.answers_version = :base_version
  AND  a.deadline_at >= :now_minus_grace
  AND  EXISTS (SELECT 1 FROM users u WHERE u.id = a.student_id AND u.is_active = 1);
```

- `rowcount = 1`: thành công, trả `answers_version = base_version + 1`. Không cần đọc lại.
- `rowcount = 0`: chạy **một truy vấn chẩn đoán** (hiếm) để chọn lỗi đúng: `410` đã nộp hoặc đóng (kèm biên nhận), `409 epoch_mismatch`, `409 version_conflict` (kèm đáp án và version máy chủ), `403 account_locked`.
- `rowcount` trong MySQL là số dòng **khớp điều kiện** chỉ khi kết nối bật `CLIENT_FOUND_ROWS`. SQLAlchemy với PyMySQL bật sẵn; test phải khẳng định điều này vì nếu tắt thì ghi trùng nội dung sẽ báo 0 dòng.
- Hạn dùng `deadline_at`, **không** đọc bảng `exams`, nên gia hạn kỳ thi không cần xóa cache nào.

Quy tắc phía máy: nếu nhận `409 version_conflict` mà `answers` của máy chủ bằng đúng bản mình vừa gửi, coi như đã thành công (phản hồi trước bị mất). Nếu khác, hiện hộp đối chiếu và giữ nháp.

### 4.3 Nộp bài và chấm

```sql
BEGIN;
SELECT id, status, answers, answers_version, write_epoch, deadline_at,
       receipt_code, submit_request_id, content_digest
FROM   exam_attempts
WHERE  id = :attempt_id AND student_id = :uid
FOR UPDATE;                                   -- chỉ khóa dòng của chính em

-- status = submitted hoặc auto_submitted: trả lại biên nhận (so request_id và content_digest, khác thì 409)
-- now <= deadline_at + grace, epoch và base_version khớp:
--   chấm bằng khóa đáp án trong cache (paper_id, key_version), rồi
UPDATE exam_attempts
SET    status = 'submitted', answers = :final, answers_version = answers_version + 1,
       submitted_at = :now, submit_request_id = :rid, receipt_code = :code,
       content_digest = :digest, score = :score, max_score = :max
WHERE  id = :attempt_id;
INSERT INTO exam_grade_history (attempt_id, answer_key_version, score, graded_at, reason)
VALUES (:attempt_id, :key_version, :score, :now, 'submit');
COMMIT;
-- now > deadline_at + grace: bài chính thức là bản đã đồng bộ gần nhất; ghi bản muộn vào exam_late_submissions
```

Biên nhận gồm mã (10 ký tự base32 sinh bằng `secrets`), giờ nộp, và `content_digest` (băm nội dung đáp án) để em chứng minh mình đã nộp gì. Khóa đáp án đọc từ DB **một lần mỗi tiến trình** rồi cache, nên chấm không tốn truy vấn.

### 4.4 Quét chốt các lượt quá hạn

```sql
SELECT id FROM exam_attempts
WHERE  status = 'in_progress' AND deadline_at < :now - INTERVAL :grace SECOND
ORDER  BY id LIMIT 100
FOR UPDATE SKIP LOCKED;
```

Mỗi lô 100 dòng xử lý và commit riêng bằng **cùng hàm chốt** với đường nộp (một nguồn quy tắc). Chạy bằng `systemd timer` mỗi phút và cũng được gọi khi có người đọc một lượt đã quá hạn. `SKIP LOCKED` làm quét không chờ các lượt đang được nộp.

## 5. Phía trình duyệt

| Quy tắc | Lý do |
| --- | --- |
| **Một chuyến bay**: mỗi lượt chỉ có một yêu cầu lưu đang chạy, thay đổi mới gộp lại chờ lượt sau | Tránh hai bản của cùng một máy tranh nhau và tránh dồn khi mạng chậm |
| Gửi sau 3 giây kể từ thay đổi cuối, cộng nhiễu 0–2 giây; tối đa một lần mỗi 15 giây | Làm lệch nhịp 500 máy |
| Lỗi: chờ lùi dần 1, 2, 4, 8, 16 giây (trần 30), mỗi lần cộng nhiễu ngẫu nhiên đầy đủ | Không đập vào máy chủ đang quá tải |
| Mất mạng cả lớp rồi có lại: trễ thêm ngẫu nhiên 0–10 giây trước lần thử đầu | Tránh bão kết nối lại |
| `timeout` 15 giây cho mọi yêu cầu (đã đặt ở `lib/axios.ts`) | Một yêu cầu treo sẽ chặn mọi lần lưu sau |
| `navigator.locks.request('attempt-' + id, { ifAvailable: true })` | Hai tab của cùng một máy: chỉ tab giữ khóa được ghi, tab kia chỉ đọc |
| `sendBeacon` khi `pagehide` **không đặt được header `Authorization`** nên token lượt thi đi trong thân yêu cầu của riêng endpoint sự kiện | Giới hạn của trình duyệt |
| Tín hiệu còn sống: một yêu cầu nhỏ mỗi 60 giây (cộng nhiễu), cập nhật `last_seen_at` | 500/60 khoảng 8 yêu cầu mỗi giây |
| Độ lệch đồng hồ `offset = server_now - Date.now()` đo lại mỗi lần lưu thành công | Không tin đồng hồ máy học sinh |

## 6. Hàng đợi và việc nền

- **Không có Redis hay broker.** Hàng đợi nhập đề là bảng `exam_import_jobs` trong MySQL. Worker nhận việc bằng `SELECT … FOR UPDATE SKIP LOCKED LIMIT 1`, đặt `locked_until = now + 90 giây`, rồi **gia hạn** `locked_until` mỗi 30 giây khi còn chạy. Worker chết thì `locked_until` hết hạn và job quay về `queued`.
- Worker nhập đề **chạy một việc mỗi lúc** (cấu hình được), ở `nice` thấp, và **tạm dừng khi có kỳ thi đang mở** để dành CPU cho học sinh.
- Bộ đọc chạy trong **tiến trình con** có thời gian tối đa (`EXAM_IMPORT_TIMEOUT_SECONDS`) và giới hạn bộ nhớ; quá giới hạn thì job `failed` với thông báo rõ.
- Hàm chốt lượt quá hạn dùng chung giữa đường nộp và việc quét, nên một quy tắc duy nhất quyết định "bài chính thức".

## 7. Tự bảo vệ khi quá tải

| Biện pháp | Chi tiết | Trạng thái |
| --- | --- | --- |
| Pool kết nối tường minh | 10 + 5 mỗi tiến trình, chờ tối đa 10 giây, tái chế 1.800 giây | Đã làm |
| Phiên DB đóng trước khi gửi phản hồi (`DbSession`) | Học sinh mạng chậm không giữ kết nối | Đã làm, đã đo thứ tự |
| Hết chờ pool thành `503` kèm `Retry-After: 2` thay vì `500` | `sqlalchemy.exc.TimeoutError` ánh xạ trong middleware lỗi | Chưa làm, trong kế hoạch |
| `--limit-concurrency` của uvicorn | Trần số kết nối mỗi worker, vượt thì `503` | Chưa làm, chọn giá trị ở M3 |
| Giới hạn đăng nhập sai theo tài khoản | 10 lần rồi 60 giây một lần, không theo IP vì cả trung tâm dùng chung một IP | Đã làm. Giới hạn **mềm** khi bắn song song (đã đo: 33 lần qua thay vì 10) |
| Giới hạn tần suất lưu theo lượt | Tối đa khoảng 1 lần mỗi giây | Chưa làm |
| Bộ giới hạn đăng nhập đồng thời | 4 bcrypt đồng thời mỗi tiến trình | Đã có |

Thiếu `503` có nghĩa là hết chờ pool hiện ra như `500` "Đã xảy ra lỗi máy chủ". Đây là mục đầu tiên của kế hoạch vì nó quyết định giao diện xử lý quá tải thế nào.

## 8. Kiểm chứng

### 8.1 Test tranh chấp trên MySQL

Các test ở cột cuối bảng mục 3, chạy bằng `SCHEDULE_MYSQL_TESTS=1` trên DB `*_test`. Mẫu chung: dùng `threading.Barrier` để các luồng cùng xuất phát, mỗi luồng có kết nối riêng, rồi khẳng định trạng thái cuối cùng của DB (không chỉ mã phản hồi). Lỗi tranh chấp thường chỉ xuất hiện khi lặp lại, nên mỗi test chạy vài chục vòng.

### 8.2 Tải bằng k6 (M3, từ máy khác, trên VPS thật)

| Kịch bản | Mô tả | Ngưỡng đạt |
| --- | --- | --- |
| `login_ramp` | 500 đăng nhập trong 10 phút, một đợt dồn 1 phút | Không lỗi, p95 dưới 3 giây |
| `start_herd` | 500 bắt đầu trong 5 giây | Mỗi em đúng một lượt; p95 dưới 2 giây |
| `steady_sync` | 500 em lưu mỗi 15 giây lệch nhịp, 20 phút | p95 lưu dưới 500 ms; tỷ lệ lỗi dưới 0,1% (không tính `409` dự kiến) |
| `network_flap` | 20% em mất mạng 60 giây rồi nối lại cùng lúc | Không em nào mất đáp án đã được báo lưu |
| `submit_herd` | 500 nộp trong 5 giây, 10% gửi trùng | p95 dưới 2 giây; đúng 500 biên nhận |
| `restart_api` | Dừng `lms-api` 60 giây giữa ca, rồi chạy lại | Mọi máy phục hồi; không mất đáp án đã báo lưu |

Mỗi lần chạy kết thúc bằng **công cụ đối soát** (`scripts/exam_reconcile.py`): so đáp án cuối cùng mà mỗi máy ảo tin là đã lưu với bản ghi trong MySQL. Đạt khi không có máy nào có đáp án "đã lưu" mà DB không có, và số biên nhận bằng số lượt đã nộp.

### 8.3 Cần đo thêm

`CLIENT_FOUND_ROWS`, thời gian giữ kết nối của từng đường nóng, độ trễ commit trên đĩa VPS, `innodb_flush_log_at_trx_commit` (mặc định 1 là bền vững; chỉ hạ khi đã chấp nhận mất tối đa một giây dữ liệu), A/B `--http h11` với `--http httptools --loop uvloop`.

## 9. Bẫy đã gặp trong dự án này

| Bẫy | Bằng chứng | Phòng |
| --- | --- | --- |
| Phiên DB mặc định đóng **sau** khi gửi byte cuối | Đo thứ tự: endpoint, serialize, gửi, đóng | Dùng `DbSession` (`scope="function"`) |
| Việc chạy nền dùng lại phiên đã đóng thì **rò rỉ kết nối** | Đo: task nền vẫn chạy được trên phiên đã đóng mà không lỗi | Việc nền tự mở phiên bằng `get_session_factory()` |
| `BackgroundTasks` bị bỏ khi endpoint ném `HTTPException` | Quan sát khi làm giới hạn đăng nhập | Trả `JSONResponse(background=…)` |
| Ghi MySQL trong đường trả lời làm hở thời gian phản hồi | 605 so với 366 ms rồi sau sửa 211 so với 213 ms | Ghi sau phản hồi, hoặc làm hai nhánh cùng chi phí |
| `localhost` trên Windows chậm 2 giây mỗi kết nối | 2.100 ms so với 20–40 ms | `127.0.0.1` |
| MySQL gán cột `SET` từ trái sang phải | Câu SQL in ra | `ordered_values` |
| SQLite bỏ qua `FOR UPDATE`, khóa ngoại mặc định tắt | Đọc tài liệu, đã gặp ở test tranh chấp | Test khóa chạy trên MySQL |
| Phép đo tải trên máy dev bị nhiễu bởi chính máy phát tải | `/health` không DB cũng có đuôi 2 giây | Đo ở M3 từ máy khác, so sánh với endpoint không DB làm mốc |

## 10. Đã đo: bão nộp bài (24/11/2026)

Đo trên máy phát triển (Docker MySQL, loopback, một tiến trình nhiều luồng), **không phải VPS**. Mỗi bài có 22 câu, nộp bằng `AttemptService.submit` thật (khóa dòng, đọc khóa đáp án, chấm, cập nhật, ghi lịch sử, commit). Kết quả chỉ cho biết hình dạng, chưa phải năng lực của VPS.

| Kịch bản | Tổng | Thông lượng | Trung vị | p95 | p99 |
| --- | --- | --- | --- | --- | --- |
| 125 em, pool 15, 15 luồng (phần của một worker) | 0,41 s | 305 bài/s | 47 ms | 55 ms | 58 ms |
| 500 em, pool 60, 60 luồng (bốn worker gộp) | 1,62 s | 308 bài/s | 164 ms | 233 ms | 260 ms |
| 500 em ập vào pool 15 (60 luồng chờ pool) | 3,12 s | 160 bài/s | 90 ms | 2443 ms | 2545 ms |

- Một lần nộp giữ kết nối khoảng 47 ms khi 15 luồng chạy song song, không phải 20 ms. Nhưng cả 500 bài vẫn xong trong 1,6–3,1 s và không bài nào bị `503`, vì `DB_POOL_TIMEOUT` là 10 s.
- Chờ pool lâu nhất đo được khoảng 2,5 s, khi mọi em nộp **đúng một thời điểm**. Cho nên giao diện phải **trễ ngẫu nhiên 0–2 s trước khi tự nộp lúc hết giờ** (nhỏ hơn nhiều so với ân hạn 30 s). Quy tắc này chưa có trong mục 5.
- Chấm 22 câu trong bộ nhớ tốn khoảng chục micro-giây đến vài chục micro-giây, nhỏ so với thời gian truy cập DB.
- Ảnh trang đề: dùng `Cache-Control: private` (không phải `public`) vì URL có chữ ký và đề chưa được phép lọt vào bộ nhớ đệm dùng chung.
