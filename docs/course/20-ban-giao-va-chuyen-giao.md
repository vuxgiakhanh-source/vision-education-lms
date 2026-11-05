# Từ chạy trên máy mình đến tự làm một dự án khác

## 1. Chốt bản đầu bằng hành vi

Một bản LMS dùng thử: cô tạo lớp, thêm học sinh, giao bài; học sinh đúng lớp
xem/nộp; cô chấm/công bố; học sinh xem kết quả. Định nghĩa điểm, deadline,
retry, rời lớp và quyền trợ giảng phải được viết trước. Lịch/tài liệu đi tiếp
khi luồng đó ổn. Ghi rõ chức năng chưa có; không làm nút giả để tạo ấn tượng đã xong.

## 2. Môi trường và đường request production

```text
Browser --HTTPS--> reverse proxy
                  ├─ frontend files (Vite build)
                  └─ /api → ASGI server → FastAPI → MySQL
                                               └→ file storage
```

Đây là một kiến trúc triển khai có thể chọn, không phải config đã áp dụng trong
repo. Nếu frontend/backend khác origin, cần CORS và credential policy phù hợp.
Nếu cùng origin dưới /api, phải thống nhất baseURL và route prefix/rewrite.

Vite dev server không phải máy chủ production. `npm run build` tạo dist;
environment Vite thường được nhúng lúc build. Đổi `.env` trên server sau build
không tự đổi bundle đã phát hành. FastAPI cần process manager, restart policy,
health/readiness và log; `--reload` thuộc dev.

## 3. Checklist phát hành có thao tác kiểm

| Việc | Bằng chứng người học nộp |
|---|---|
| Config | .env.example không có secret, mô tả từng biến và lúc đọc |
| Dependency | Lock/requirements phù hợp, cài lại ở môi trường sạch |
| DB | Migration review, schema version, thử upgrade trên bản sao |
| Frontend | Build/lint; deep link refresh route chạy được |
| API | Health, lỗi đúng status, không lộ traceback, request size hợp lý |
| Quyền | Hai lớp, nhiều vai trò; truy cập trực tiếp API vẫn bị chặn |
| File | Lưu bền, đúng quyền download, backup liên kết metadata |
| Quan sát | Từ một lỗi UI tìm được request và server log |
| Backup | Phục hồi sang DB mới rồi đối chiếu dữ liệu |
| Quay lại | Cách quay code và kế hoạch dữ liệu khi schema đã đổi |

Không chứa secret trong ảnh hoặc câu lệnh ghi vào README. Ghi tên biến và nguồn
cấp thay vì giá trị thật. Bản phát hành phải biết phiên bản source/schema đang dùng.

## 4. Bài thực hành staging

Chọn môi trường riêng, dữ liệu giả, ghi lại cách chạy FE/BE/DB. Thực hiện một
release nhỏ; gây lỗi cấu hình API có chủ đích; tìm lỗi bằng Network/log; sửa;
khôi phục DB học từ backup. Đo thời gian và ghi bước còn thủ công. Không thao
tác phá trên production hoặc dữ liệu học sinh thật.

Với Docker, cần học Dockerfile, build context, image/container, layer/cache,
network service names, env, volume và healthcheck trước khi viết Compose cho
cả app. Hostname `localhost` bên trong container là chính container đó;
backend container thường gọi tên service DB, không dùng localhost của máy host.

## 5. Bài dự án chuyển giao: thư viện nhỏ

Bạn nhận đề: thủ thư quản lý sách và bản sao; độc giả mượn/trả; theo dõi quá hạn.
Không có schema/API mẫu. Tự hỏi trước: một tên sách có nhiều bản sao không,
một người mượn tối đa bao nhiêu, hai người mượn bản cuối cùng đồng thời thế nào,
trả lặp và mất sách xử lý sao, ai được xem lịch sử của ai?

Nộp đặc tả, ERD, API contract, code, tests, README và bản demo. Bắt buộc tự viết
một luồng tạo phiếu mượn có transaction và kiểm quyền. Tự thiết kế UI có đủ
loading/error/empty/success, thử keyboard và viewport hẹp.

## 6. Buổi bảo vệ không nhìn lời giải

- Mở một request, chỉ từng file và giá trị đi qua.
- Giải thích vì sao một rule ở service, một rule ở DB và một rule ở UI.
- Thay yêu cầu: cho gia hạn một lần; tự chỉ ra schema/API/UI/test bị ảnh hưởng.
- Nhận lỗi do người kiểm tạo, nêu giả thuyết trước khi sửa.
- Chạy lại từ môi trường sạch theo README, không nhờ trạng thái cũ trong máy.

Tra docs được. Sao chép nguyên implementation không được tính là tự làm.
Không bắt nhớ mọi API; cần biết tìm đúng tài liệu, đọc signature và kiểm hành vi.

## 7. Phiếu đánh giá năng lực cuối khóa

Mỗi mảng 0–3: 0 chưa làm; 1 cần chỉ từng dòng; 2 tự làm với tài liệu; 3 tự làm
và xử lý biến thể/lỗi. Chấm: phân tích, ngôn ngữ, UI, API, DB, quyền, test,
debug, phát hành và giải thích. Mục tiêu là tất cả mảng cốt lõi ít nhất mức2;
không bù lỗi đọc chéo dữ liệu bằng điểm giao diện đẹp.

Khi yếu một mảng, quay lại đúng bài nhỏ và làm biến thể. Giữ nhật ký lỗi và
quyết định. Một lần làm được có thể nhờ nhớ ví dụ; làm lại ở miền thư viện với
yêu cầu thay đổi mới cung cấp bằng chứng chuyển giao kỹ năng.

## 8. Sau nền tảng: học theo nhu cầu quan sát được

Tìm kiếm lớn → xem query/index và yêu cầu search. Tác vụ lâu → job queue,
retry/idempotency/quan sát. Cache → invalidation và phân quyền dữ liệu. Realtime
→ WebSocket/auth/reconnect/nhiều process. Offline → đồng bộ/conflict/storage.
Mỗi công nghệ mới phải có vấn đề, giới hạn, thử nghiệm và tiêu chí thành công.
Bạn đã học cách tự học khi biến một điều chưa biết thành phép thử kiểm được.
