# P3 — Build, migration, phát hành và quay lại

Đầu ra: một bản staging có thể dựng lại từ source, biết phiên bản đang chạy,
phát hiện release lỗi và quay lại theo kế hoạch dữ liệu.

## 1. Hiểu bốn loại sản phẩm của một release

Source commit mô tả code; lock mô tả dependency; image/bundle là artifact đã
build; schema revision mô tả DB. Lưu cả bốn trong release record. Gắn tag source
không chứng minh image cùng tag chưa bị build lại với dependency khác.

Frontend VITE_* thường đọc lúc build và hiện được ở client. Lab build
VITE_LAB_API_URL=/api. Nginx /api/ proxy tới FastAPI, phần /api/ được thay bằng
đường dẫn root do proxy_pass có URI `/`. Thử /api/classes thật để xác nhận;
đừng chỉnh cả frontend và backend prefix theo cảm giác.

## 2. Đọc deployment lab trước khi chạy

Mở [hướng dẫn từng lệnh](workshop/deploy/README.md),
[Compose](workshop/deploy/compose.yaml), [API Dockerfile](workshop/deploy/Dockerfile.api),
[web Dockerfile](workshop/deploy/Dockerfile.web), [Nginx](workshop/deploy/nginx.conf).

```text
Browser → 127.0.0.1:8088 → Nginx
                         ├─ React dist
                         └─ /api → api:8000 → db:3306
Migration job ───────────────────────────────┘
```

DB/API không publish cổng host. Volume giữ dữ liệu DB qua restart container.
Container localhost là container đó, nên API dùng service name db. API dùng
non-root user; secrets được cấp bằng env trong lab, chưa là secret manager.

Compose đợi DB healthy, migrate exit thành công rồi API, web đợi API ready.
Thứ tự khởi động không tự phục hồi mọi dependency khi đang chạy. Healthcheck
unhealthy không tự restart một process còn sống; cần giám sát và hành động vận
hành. Restart policy xử lý process/container thoát theo policy, không thay alert.

## 3. Migration là một thay đổi dữ liệu có rủi ro

Đọc [0001_baseline.py](workshop/deploy/migrations/versions/0001_baseline.py):
tạo bảng theo FK, index và constraints rõ. Nó dành cho DB học mới, chưa là cách
nâng cấp DB sản phẩm hiện có. Alembic upgrade chạy riêng một job, không để mỗi
worker startup cùng chạy migration/seed.

Ví dụ thêm status không-null vào bảng lớn:

1. **Expand:** thêm cột tương thích code cũ, cho phép null/default đã xét.
2. Deploy code đọc được cả giá trị cũ/mới, mọi đường ghi có policy rõ.
3. Backfill theo batch nhỏ, đo lock/replication/IO, có checkpoint tiếp tục.
4. Kiểm không còn hàng thiếu, code cũ đã rời hệ thống.
5. **Contract:** thêm ràng buộc/bỏ cột cũ ở release riêng có review.

Không mặc định ALTER nào cũng không khóa hoặc DDL MySQL rollback như nghiệp
vụ. Thử đúng DB version, kích thước đại diện và xem kế hoạch downtime. Backup
trước thay đổi chưa đủ nếu chưa biết restore mất bao lâu.

## 4. CI tối thiểu chạy ở một máy sạch

[course-ci.yaml](workshop/deploy/course-ci.yaml) là template cho repo học có
workshop làm root. Copy vào .github/workflows trong repo học sau khi đọc paths;
không phải workflow đang tự chạy ở repository sản phẩm này.

Pipeline cài Python dependency → unittest → npm ci → TypeScript strict + Vite
build. Tests SQLite/ASGI chứng minh một lớp; thêm job MySQL/browser khi đã có
fixture/runner phù hợp. CI không được mang secret production vào pull request
không tin cậy. Token CI có quyền tối thiểu, artifact/log không chứa token lab.

Trước release: pin action theo commit SHA đã review và image theo digest,
lock dependency, quét dependency/image phù hợp. Các tag mẫu trong lab giúp đọc
nhanh, chưa phải chuỗi cung ứng khóa đầy đủ. Không ghi “reproducible hoàn toàn”
khi Python transitive dependencies và base images vẫn thay đổi.

## 5. Một quy trình phát hành có thao tác xác nhận

| Bước | Hành động | Điều kiện đi tiếp |
|---|---|---|
| Chuẩn bị | Freeze phạm vi, ghi commit/image/schema | CI và matrix scope qua |
| Dữ liệu | Backup, thử migration trên bản sao | Restore + migration smoke qua |
| Staging | Deploy đúng artifact | Health/ready, deep link, 2 tài khoản qua |
| Quyết định | Review lỗi còn lại và phương án quay | Có người chịu trách nhiệm, cửa sổ phù hợp |
| Release | Áp migration/code theo thứ tự đã chốt | Biết app/schema đang dùng |
| Sau release | Smoke nghiệp vụ + theo dõi lỗi/latency | Không chỉ /health xanh |

Không tự động deploy mọi push khi chưa đủ kiểm tra. CD có thể có bước người
vận hành duyệt release cụ thể; đây là quy trình của dự án, không phải nút xin
phép mỗi lần người học chạy một lệnh lab cục bộ.

## 6. Rollback code khác phục hồi dữ liệu

Case A: chỉ sửa UI, DB không đổi → dùng image trước, smoke lại.
Case B: thêm cột tương thích → code trước có thể chạy, giữ cột mới.
Case C: migration xóa dữ liệu → code trước không tạo lại dữ liệu; cần restore
hoặc forward fix với kế hoạch đối chiếu thao tác phát sinh sau backup.

Chọn rollback theo case thực tế, không coi alembic downgrade là nút cứu chung.
Downgrade baseline lab sẽ drop bảng. Khi restore bản cũ, quyết định xử lý các
bài nộp mới hơn backup; RPO/RTO ở P4 biến điều này thành yêu cầu đo được.

## 7. Bài diễn tập staging

1. Dựng lab từ môi trường sạch, ghi thời gian, lệnh và exit code.
2. Cố ý đặt baseURL sai trong một build riêng; phát hiện bằng Network/log.
3. Giữ image tốt trước đó, quay lại mà không rebuild tag cũ.
4. Phục hồi dump vào DB mới theo README; kiểm một luồng đọc bằng instance thử.
5. Dừng DB lab, xác nhận /ready không xanh; bật lại và đo thời gian hồi phục.

Không thực hiện thí nghiệm phá trên dữ liệu thật. Ghi được lỗi chứng minh
runbook có ích; không cần che lỗi để bài báo cáo đẹp.

## 8. Tiêu chí qua và bài biến thể

**Điền:** release record đủ source/lock/image/schema và một smoke test nghiệp vụ.
**Trắng:** thêm migration GradeRevision và kế hoạch tương thích khi code cũ
chưa ghi audit. **Sửa lỗi:** migrate thất bại mà API vẫn chạy schema cũ; làm
pipeline dừng đúng và kiểm nó không nhận traffic như thể deploy đã xong.

Qua khi người khác dùng README dựng staging riêng, biết bản nào chạy và diễn
tập phục hồi được. Public hosting/TLS và hạ tầng ở môi trường thật phải được
kiểm ở đó; Dockerfile tồn tại chưa chứng minh đã triển khai thành công.

Nguồn: [Docker dependency readiness](https://docs.docker.com/compose/how-tos/startup-order/),
[FastAPI containers](https://fastapi.tiangolo.com/deployment/docker/),
[Nginx proxy_pass](https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_pass),
[GitHub Actions security](https://docs.github.com/en/actions/reference/security/secure-use).
