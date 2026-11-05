# Deployment lab cục bộ: React → Nginx → FastAPI → MySQL

Dùng Docker Engine/Compose đang chạy. Toàn bộ tài nguyên có project name
`vision-course-lab`, web bind 127.0.0.1:8088, DB không publish cổng. Không dùng
Compose MySQL của sản phẩm. Đây là lab HTTP trên máy học, chưa phải public hosting.

## 1. Chuẩn bị và build

Từ gốc repo, tạo ba biến cho terminal hiện tại (không commit giá trị):

```powershell
$env:LAB_SECRET = (.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(48))")
$env:LAB_DB_PASSWORD = (.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(32))")
$env:LAB_DB_ROOT_PASSWORD = (.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(32))")
$env:LAB_RELEASE = 'lesson-01'
docker compose -f docs/course/workshop/deploy/compose.yaml config --quiet
docker compose -f docs/course/workshop/deploy/compose.yaml build
docker compose -f docs/course/workshop/deploy/compose.yaml up -d
docker compose -f docs/course/workshop/deploy/compose.yaml ps
```

Giữ cùng giá trị DB password cho volume đã khởi tạo, qua secret store/file riêng
ngoài Git khi cần chạy lại. Không tạo password mới ở mỗi lần up với volume cũ:
MySQL init variables không tự đổi password user trong DB đã tồn tại. Đổi secret
JWT làm token cũ hết hiệu lực. Không in `docker compose config` đầy đủ vì có thể
lộ env đã nội suy; `--quiet` chỉ kiểm cấu hình.

Lockfile frontend được dùng bởi npm ci. Runtime Python và images trong lab chưa
lock toàn bộ transitive dependencies/digest; trước release thật tạo lock được
review, quét và pin digest. Dockerfile non-root cho API; web dùng image Nginx
mặc định. Không coi cấu hình này là container hardening hoàn chỉnh.

## 2. Migration và fixture

Service migrate chạy Alembic 0001 trước API. DB phải là DB học mới/rỗng; baseline
không dùng để “stamp” sản phẩm hay database SQLite của bài trước.

```powershell
docker compose -f docs/course/workshop/deploy/compose.yaml logs migrate
docker compose -f docs/course/workshop/deploy/compose.yaml exec api python -m alembic -c deploy/alembic.ini current
docker compose -f docs/course/workshop/deploy/compose.yaml exec api python -m deploy.seed_lab --students 200 --assignments 1000
Invoke-RestMethod http://127.0.0.1:8088/api/ready
```

Seeder từ chối khi users không rỗng. Không reset DB để chạy lại benchmark;
chọn DB/project/volume học mới bằng một cấu hình đã review nếu cần dataset mới.
Không dùng `down -v` với dữ liệu cần giữ. API /health chỉ báo process trả được
request, /ready SELECT 1 kiểm kết nối DB; nó chưa kiểm đủ mọi schema/permission.

Tạo token cô/học sinh bằng CLI fixture có LAB_SECRET từ container:

```powershell
docker compose -f docs/course/workshop/deploy/compose.yaml exec api python -m lms_lab token --user 1
docker compose -f docs/course/workshop/deploy/compose.yaml exec api python -m lms_lab token --user 2
```

Mở http://127.0.0.1:8088 và làm P0. Không đưa credential vào ảnh/báo cáo.
CLI fixture không phải đăng nhập production.

## 3. Xuất tài khoản và chạy tải

Từ gốc repo, dùng PowerShell 7 để xuất UTF-8 không BOM; file bị ignore và không
được nhúng vào sách:

```powershell
$labAccounts = docker compose -f docs/course/workshop/deploy/compose.yaml exec -T api python -m deploy.export_accounts
if ($LASTEXITCODE -ne 0) { throw 'Không xuất được fixture' }
$labAccounts | Set-Content -Encoding utf8NoBOM docs/course/workshop/perf/accounts.json
Set-Location docs/course/workshop/perf
k6 run -e MODE=read -e RATE=5 -e DURATION=30s lms-load.js
```

Token hết hạn hai giờ; script mặc định chỉ đọc trang đầu 20 bài. Đổi workload/
dataset và ghi điều kiện để đo truy vấn trang sâu/nhiều lớp. Không công bố số
user chỉ từ test này. Lệnh ở phần sau giả định đã quay về thư mục gốc repo.

## 4. Backup và restore sang database mới

Trong lab, tạm ngừng thao tác ghi ở UI trước bản dump để đối chiếu dễ. MySQL
InnoDB dùng --single-transaction; DDL thay schema không được chạy đồng thời.
Lệnh redirect SQL bên trong container để tránh khác biệt encoding PowerShell.

```powershell
New-Item -ItemType Directory -Force docs/course/workshop/deploy/backups | Out-Null
docker compose -f docs/course/workshop/deploy/compose.yaml exec -T db sh -c 'MYSQL_PWD="$MYSQL_PASSWORD" mysqldump -u "$MYSQL_USER" --single-transaction --no-tablespaces "$MYSQL_DATABASE" > /tmp/lab-backup.sql'
docker compose -f docs/course/workshop/deploy/compose.yaml cp db:/tmp/lab-backup.sql docs/course/workshop/deploy/backups/lab-backup.sql
docker compose -f docs/course/workshop/deploy/compose.yaml exec -T db sh -c 'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql -uroot -e "CREATE DATABASE lms_restore CHARACTER SET utf8mb4"'
docker compose -f docs/course/workshop/deploy/compose.yaml exec -T db sh -c 'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql -uroot lms_restore < /tmp/lab-backup.sql'
```

CREATE DATABASE cố ý không có IF NOT EXISTS: nếu đã có lms_restore, dừng và chọn
tên DB phục hồi mới; không nhập đè DB đã có. Kiểm exit code từng lệnh trước bước
sau. Kiểm COUNT theo bảng, một bài nộp/điểm tính tay, schema revision và quyền.
Để smoke app phục hồi, tạo account chỉ cho DB restore và cấu hình instance riêng;
không chỉ thấy file dump tồn tại rồi ghi “restore thành công”.

Backup chứa dữ liệu cần được kiểm soát quyền, mã hóa/lưu ngoài máy app và áp
dụng retention khi vận hành thật. Lab chưa có file storage; khi thêm upload,
phải phục hồi cả object và metadata nhất quán, không chỉ MySQL.

## 5. Quan sát và quay lại

```powershell
docker compose -f docs/course/workshop/deploy/compose.yaml logs --since 5m api web
docker compose -f docs/course/workshop/deploy/compose.yaml stats --no-stream
```

API log request_id/method/route pattern/status/elapsed, không request body/token.
Nginx log không có query string. Đối chiếu header X-Request-ID với API log;
template chưa có metrics exporter, dashboard hay distributed tracing.

Giữ image tag/digest bản trước và schema revision. Nếu schema tương thích,
đổi LAB_RELEASE sang tag cũ rồi up với `--no-build`; không rebuild code mới
vào tag cũ. Migration/rollback có dữ liệu cần kế hoạch expand/contract trong P3.
Không tự chạy downgrade 0001 vì nó xóa bảng.

## 6. Từ local đến staging/public

Trên máy staging riêng, giữ DB/API private, đặt TLS ingress có certificate và
renewal trước web. Cấu hình domain/HTTPS/forwarded headers theo proxy tin cậy,
không tin header client tùy ý. Kiểm deep-link refresh, mixed content, body limit,
timeout, secure cookie nếu dùng và backup/alert trước mời người dùng.

Template chỉ bind localhost có chủ đích. Việc public hosting, mua domain/cloud,
thay firewall và dùng dữ liệu thật là bước triển khai riêng; sách hướng dẫn
chuẩn bị, không tự mở dịch vụ ra Internet.
