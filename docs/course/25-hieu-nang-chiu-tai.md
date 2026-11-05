# P2 — Đo tải, tìm nghẽn và mở rộng có căn cứ

Đầu ra: báo cáo có workload, cấu hình, số đo trước/sau và kiểm dữ liệu sau tải.
Các con số mục tiêu dưới đây là bài tập đề xuất, không phải năng lực đã đo của LMS.

## 1. “Nhiều user” phải được đổi thành điều kiện đo

10.000 tài khoản không có nghĩa 10.000 request cùng lúc. Viết riêng: tài khoản
đăng ký, người hoạt động trong khoảng thời gian, kết nối mở, request/giây và
lượt làm nghiệp vụ/giây. Một lượt có thể gọi nhiều API và tải file.

Ví dụ giả định: 200 học sinh hoạt động, mỗi 10 giây gọi một API → khoảng 20
request/giây trung bình. Khi cùng bấm nộp trong vài giây cuối, burst khác hẳn
trung bình. Đếm cả autosave, polling, tải ảnh và thao tác cô; không ngoại suy
từ một endpoint /health không truy vấn DB.

Ở trạng thái ổn định, quan hệ gần đúng L = λ × W giúp kiểm tra tính hợp lý:
20 request/giây × 0,2 giây ≈ 4 request đang xử lý trung bình. Nó không nói
cần đúng 4 người dùng, không bảo đảm burst/p99 và không dùng khi hệ thống đang
tích backlog vô hạn. Ghi giả định khi dùng công thức.

## 2. Chốt SLI/SLO cho một hành động

SLI là thứ đo: tỉ lệ thành công, thời gian từ request đến response. SLO là
mục tiêu trong cửa sổ và điều kiện đã chốt. Một benchmark ngắn không chứng
minh uptime cả tháng.

| Hạng mục lab | Mục tiêu bài tập | Đừng nhầm |
|---|---|---|
| List assignments | p95 < 500ms, p99 < 1000ms | Trung bình thấp có thể che đuôi chậm |
| Request lỗi ngoài dự kiến | < 1% | 200 với JSON sai vẫn là lỗi nghiệp vụ |
| Business checks | > 99% | Check cần đúng chủ/lớp/nội dung |
| Iterations bị bỏ | 0 | Rate cấu hình khác rate đạt được |
| Dữ liệu sau nộp | Không trùng/mất/đổi timestamp | Throughput cao không bù dữ liệu sai |

Điều chỉnh mục tiêu theo nhu cầu và ngân sách thực tế trước đo. P95=500ms
nghĩa ít nhất 95% mẫu trong phạm vi phép đo không vượt ngưỡng đó; kiểm cả số
mẫu và từng nhóm endpoint, không gộp /health vào để làm đẹp kết quả.

## 3. Chuẩn bị một môi trường tái lập

Dùng [deployment lab](workshop/deploy/README.md), DB MySQL học mới, fixture
giả và [script k6](workshop/perf/lms-load.js). Có sẵn seeder cho 200 học sinh,
1000 bài, không tự xóa dữ liệu cũ. Tăng dữ liệu theo giả định sản phẩm để test
query/index, không lặp 20 hàng bé rồi suy ra dữ liệu nhiều năm.

Ghi CPU/RAM/disk, số worker/replica, pool, DB version/schema, commit, index,
proxy limit và máy phát tải. Máy phát tải chạy chung có thể tranh CPU/IO với
app; đo lab chung máy phải ghi điều này. Token có TTL, hết hạn giữa test làm
401 tăng vì fixture, không phải kết luận DB chậm.

Trước tải: smoke bằng tài khoản đúng/sai để xác nhận script đang gọi đúng app,
chưa lộ điểm và không đếm 404/401 như “request thành công”.

## 4. Chạy script có ngưỡng pass/fail

Từ thư mục `docs/course/workshop/perf`, sau khi xuất accounts.json fixture và
chạy deployment lab ở 8088:

```powershell
k6 run -e MODE=read -e RATE=5 -e DURATION=30s lms-load.js
k6 run -e MODE=read -e RATE=20 -e DURATION=2m lms-load.js
k6 run -e MODE=submit -e RATE=10 -e DURATION=1m lms-load.js
```

Mỗi iteration trong script hiện có đúng một request. Executor constant-arrival-
rate đặt số iteration khởi chạy theo thời gian; thiếu VU có thể bỏ iteration.
Script có threshold cho dropped_iterations để không im lặng coi đã phục vụ đủ.
Script không sleep trong executor này vì executor đã điều tiết nhịp.

Checks xác minh JSON; thresholds quyết định pass/fail toàn lượt. Check thất
bại đơn lẻ không tự làm một bài k6 thất bại nếu thiếu threshold tương ứng.
Script chỉ cho localhost và không in token/body. Chuyển sang staging riêng cần
review URL, dữ liệu, limit và thời gian test; không chạy tải vào hệ thống người khác.

Lần đầu MODE=submit tạo bản nộp; lần sau cùng học sinh là retry. Muốn đo insert
mới, tạo fixture/bài mới trong DB học và cập nhật script/contract. Không ghi
“tốc độ ghi mới” từ một test chủ yếu trả bản đã có.

## 5. Các kiểu tải trả lời những câu hỏi khác nhau

| Kiểu | Cách thực hành | Học được gì |
|---|---|---|
| Smoke | Rate thấp 30 giây | Token, endpoint, checks, fixture đúng |
| Baseline | Giữ 5 rồi 20 iterations/s | Đường cơ sở để so thay đổi |
| Step/stress | Tăng từng bậc, giữ đủ quan sát | Điểm latency/lỗi bắt đầu tăng |
| Spike | Dồn nộp theo burst cuối giờ | Queue, lock và phục hồi sau burst |
| Soak | Giữ tải dự kiến lâu hơn | RAM/connection/file handle có tăng mãi? |

Script mẫu cung cấp baseline read/submit. Tự thêm scenario cho spike/soak,
mix đọc/ghi và lượt user có think time; nộp mã scenario cùng kết quả. Không
ghi những kịch bản chưa chạy thành tính năng đã được nghiệm thu.

## 6. Tìm nghẽn bằng quan sát theo thứ tự

Một p99 xấu chỉ là dấu hiệu. Đối chiếu thời điểm ở máy tải → proxy → API → DB.

| Quan sát | Giả thuyết | Phép thử giữ các biến khác |
|---|---|---|
| 429 tăng, API rảnh | Proxy rate limit chặn | So limit và offered rate; ghi đúng loại lỗi |
| SQL nhiều theo số hàng | N+1 | Đếm query/trang trước/sau eager loading |
| CPU DB cao, rows examined lớn | Query/index không phù hợp | EXPLAIN với fixture lớn, thêm đúng index |
| Pool timeout, connection chạm trần | Worker × pool quá lớn hoặc transaction dài | Đo connection/lock, rút transaction |
| Cùng bài nộp chờ nhau | Assignment lock tuần tự hóa | So nhiều bài với cùng một bài |
| API CPU cao, DB rảnh | CPU work/serialize/hash | Profile use case, tách tác vụ nặng nếu cần |
| Máy tải CPU cao, dropped tăng | Generator nghẽn | Tách generator, đo lại cùng app |

Không đổi worker, index, cache và RAM cùng lúc rồi quy công cho một thứ. Mỗi
lần sửa cần một giả thuyết, diff nhỏ và đo lại cùng điều kiện.

## 7. Worker, pool và async liên quan nhau thế nào?

Lab container dùng 2 Uvicorn workers; mỗi process có pool_size=5 và
max_overflow=5. Trần lý thuyết phía API là 2 × (5+5)=20 connection. Thêm
replica thì nhân tiếp; cộng job/migration/admin và chừa headroom cho DB.
Pool mở theo nhu cầu, không có nghĩa khởi động đã tạo đủ 20 connection.

Không tăng workers vô hạn. Mỗi worker tốn RAM và có pool riêng. Sync SQLAlchemy
được dùng ở endpoint def trong lab; không biến hàm thành async rồi gọi driver
sync trực tiếp và nghĩ I/O đã không chặn event loop. Chọn sync/async toàn đường
dependency và đo, không dùng tên async làm bằng chứng chịu tải.

Pool timeout, network timeout và deadline nghiệp vụ khác nhau. Timeout không
tự chứng minh transaction đã rollback; client cần trạng thái/retry contract.
Retry có giới hạn/backoff/jitter cho lỗi tạm thời đã phân loại; không retry
mọi POST hay retry 401/validation liên tục. Khi quá tải, giới hạn hàng đợi,
request size, thời gian và trả lỗi phù hợp để tránh tích backlog mãi.

## 8. Cache và queue chỉ thêm với contract rõ

Cache báo cáo: ghi key gồm actor/scope/filter/version cần thiết; TTL; invalidation
khi điểm/quyền đổi; cách tránh trả cache của người khác. Nêu mức dữ liệu cũ được
phép. Cache không phải nguồn quyết định quyền; resource vẫn kiểm quyền hiện tại.

Queue cho email/export: transaction ghi outbox; worker claim có lease; gửi;
đánh dấu; retry có giới hạn; nơi giữ job lỗi và cách xử lý. Giả lập worker chết
sau gửi nhưng trước đánh dấu; consumer/provider cần idempotency theo contract.
Request thành công không đồng nghĩa email đã đến, UI phải thể hiện trạng thái.

Horizontal scaling cần state ngoài RAM process: DB/session/limiter/socket event
phối hợp giữa instance. Sticky session không chữa invariant/độ bền dữ liệu.
Không cần áp dụng tất cả ngay; nêu bottleneck đã đo trước khi chọn công cụ.

## 9. Kiểm correctness sau tải và báo cáo

Điền [REPORT.md](workshop/perf/REPORT.md). Ghi offered/achieved rate, p95/p99,
lỗi/checks, dropped, CPU/RAM, DB connections/locks và điều kiện thí nghiệm.

```sql
SELECT assignment_id, student_id, COUNT(*) AS copies
FROM submissions
GROUP BY assignment_id, student_id
HAVING COUNT(*) > 1;
```

Query không trả row là một invariant. Đối chiếu thêm nội dung, chủ bài, điểm,
timestamp và số request nghiệp vụ mong đợi. UNIQUE không chứng minh ứng dụng
trả response retry đúng. [Test MySQL cạnh tranh](workshop/test_mysql_concurrency.py)
kiểm hai Session độc lập; phải chạy bằng DB học riêng để có bằng chứng locking.

## 10. Bài tự làm và tiêu chí qua

**Điền:** thêm threshold cho một endpoint riêng và chứng minh script exit lỗi
khi cố ý đặt mục tiêu bất khả thi. Không sửa ngưỡng chỉ để lượt đo xanh.

**Trắng:** làm workload 80% đọc/20% nộp với tài khoản/fixture đủ lớn; giải thích
iteration khác request. Test burst cuối hạn và kiểm giờ server/bản nộp.

**Sửa lỗi:** tìm bottleneck khóa assignment trong bản tham chiếu. Đề xuất tối
ưu giữ retry/UNIQUE/scope/deadline, thêm test MySQL cạnh tranh rồi so số đo.

Qua khi chứng minh được “cấu hình X đáp ứng workload Y với ngưỡng Z trong
thời gian T”, chỉ rõ giới hạn. Chưa chạy đủ phép đo thì giữ trạng thái CHƯA ĐO.

Nguồn chính thức: [k6 executor](https://grafana.com/docs/k6/latest/using-k6/scenarios/executors/constant-arrival-rate/),
[k6 thresholds](https://grafana.com/docs/k6/latest/using-k6/thresholds/),
[SQLAlchemy pooling](https://docs.sqlalchemy.org/en/21/core/pooling.html),
[FastAPI workers](https://fastapi.tiangolo.com/deployment/server-workers/).
