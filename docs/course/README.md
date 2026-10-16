# Giáo án tự viết Vision Education LMS

Ngày soạn: 17/10/2026. Mục tiêu: bạn tự phân tích, viết, giải thích, kiểm tra và
sửa một chức năng đi từ React đến MySQL. Dùng đúng stack hiện tại của repo.

Đây là giáo trình thực hành. Các tính năng tương lai và quy tắc của bài tập là
đề xuất học tập, chưa tự động trở thành yêu cầu đã duyệt của sản phẩm.

## Bắt đầu thế nào?

1. Làm bài khảo sát ở [chương 00](00-phuong-phap.md).
2. Mỗi lần chọn một bài; học cú pháp → dự đoán → tự viết → thử lỗi → giải thích.
3. Chương nào đã biết, làm bài cuối chương để chứng minh trước khi bỏ qua.
4. Ghi lại một việc tiếp theo trong [WORKLOG](../WORKLOG.md).
5. Đọc [CODE_GUIDE](../CODE_GUIDE.md) khi quên vị trí file trong dự án.

## Mục lục và sản phẩm mỗi chương

| Chương | Học gì? | Bài thực hành phải tự làm |
|---|---|---|
| [00](00-phuong-phap.md) | Phương pháp, debug, đọc code, Git cơ bản | Kể lại login và lưu điểm dừng |
| [01](01-javascript.md) | Biến, kiểu, hàm, object/array, tham chiếu | Lọc, đếm, cập nhật nhiệm vụ |
| [02](02-typescript-http.md) | TypeScript, bất đồng bộ, HTTP | Kiểm tra response và xử lý trạng thái tải |
| [03](03-html-css.md) | HTML ngữ nghĩa, CSS, Grid, Tailwind | Form và danh sách responsive có focus |
| [04](04-react.md) | Props/state, hooks, router, form | Trang nhiệm vụ có lọc và gọi API |
| [05](05-python-oop.md) | Python, class, exception, composition, SOLID vừa đủ | Service nộp bài với repository giả |
| [06](06-sql.md) | Thiết kế bảng, JOIN, transaction, index | Mô hình lớp, thành viên và bài nộp |
| [07](07-fastapi.md) | Pydantic, router, Depends, hợp đồng API | Một endpoint có validation và lỗi rõ ràng |
| [08](08-sqlalchemy.md) | Session, model, repository, migration | Lưu một nghiệp vụ trọn transaction |
| [09](09-auth-phan-quyen.md) | JWT, tài khoản hiện tại, quyền theo lớp | Chặn truy cập chéo lớp ở backend |
| [10](10-lat-cat-hoan-chinh.md) | Tư duy thiết kế một chức năng xuyên hệ thống | Cô giao → học sinh nộp → cô chấm |
| [11](11-luyen-thi-bao-cao.md) | Lượt làm, thời gian, chấm điểm, thống kê | Một dạng câu hỏi và sổ câu sai |
| [12](12-kiem-thu-van-hanh.md) | Test, Git, CI, cấu hình, phát hành và phục hồi | Bản dùng thử có bằng chứng kiểm tra |
| [13](13-bai-tap-dap-an.md) | Bài tổng hợp, gợi ý, đáp án và bảo vệ đồ án | Tự xây một module mới khi yêu cầu thay đổi |

Có thêm [ví dụ tham chiếu chạy được](examples/README.md). Làm bài trước khi
đọc lời giải. Các ví dụ này không được nối vào ứng dụng và không thay database thật.

## Những mốc phải qua

| Mốc | Điều kiện |
|---|---|
| A — hiểu ngôn ngữ | Tự viết lọc/cập nhật mảng, giải thích tham chiếu và async |
| B — hiểu giao diện | Tự dựng form/list, mô tả state và xử lý loading/error/empty |
| C — hiểu backend | Vẽ được request → schema → service → repository → DB |
| D — hoàn thành nghiệp vụ | Dùng hai tài khoản thực hiện toàn luồng, tải lại vẫn đúng |
| E — đúng khi có lỗi | Test quyền, hạn nộp, gửi lặp, rollback và dữ liệu không hợp lệ |
| F — bàn giao được | Người khác theo README chạy được; giải thích và sửa yêu cầu mới |

Chưa có mốc nào được đánh dấu bạn đã đạt. Giao diện đã hoàn thiện không thay thế
việc tự chứng minh các mốc này.

## Chấm một bài thực hành

- 20 điểm: phân tích đầu vào/đầu ra, quy tắc và tình huống biên trước khi code.
- 30 điểm: code đúng, tên rõ, trách nhiệm hợp lý, phù hợp cấu trúc repo.
- 25 điểm: kiểm tra có cả tình huống đúng, lỗi và quyền truy cập khi liên quan.
- 15 điểm: giải thích được từng bước, dữ liệu và quyết định thiết kế.
- 10 điểm: tự sửa được khi thay đổi một yêu cầu nhỏ, có ghi điểm dừng.

Mốc qua bài đề xuất: 80/100, đồng thời không còn lỗi tính điểm, mất bài nộp hoặc
truy cập dữ liệu ngoài quyền trong phạm vi bài. Thang điểm này là công cụ tự học,
không phải cam kết chất lượng sản phẩm khi triển khai thực tế.

## Môi trường đã đối chiếu tại máy

Python 3.12.10, Node 24.19.0, TypeScript CLI 6.0.3; FastAPI 0.143.0,
Pydantic 2.14.0, SQLAlchemy 2.1.4, Alembic 1.20.0. Frontend dùng React 19,
React Router 7, Tailwind 4, Axios, React Hook Form, Zod. Phiên bản này là ảnh
chụp môi trường khi soạn, không phải yêu cầu nâng cấp.

Code repo dùng SQLAlchemy `Column` và `db.query`. Giáo án giải thích cách hiện tại
và minh họa `select` cho phần mới; không yêu cầu đổi toàn bộ auth để theo ví dụ.
Tài liệu SQLAlchemy 2.0 được dùng cho các khái niệm chung; kiểm tra khác biệt
phiên bản khi áp dụng API cụ thể. Kiểu ví dụ TypeScript được viết để học với
strict checking; cấu hình ứng dụng hiện tại chưa bật toàn bộ strict mode.

## Thói quen để nhớ lâu

Trước khi dùng AI: ghi dự đoán và thử viết một lần. Khi cần hỗ trợ, yêu cầu gợi ý
hoặc review phần đã viết. Sau khi tham khảo lời giải, đóng lời giải và viết lại
một biến thể có dữ liệu khác. Sau một buổi, vài ngày và một tuần, chọn lại một
bài cũ để giải thích ngắn; đây là gợi ý ôn tập, không phải lịch tự động.
