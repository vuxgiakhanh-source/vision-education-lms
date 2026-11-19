# Kế hoạch sprint xem lịch tuần

Cập nhật ngày 19/11/2026. Đây là backlog đề xuất theo thứ tự phụ thuộc. Ngày bắt đầu, thời lượng và người thực hiện từng việc sẽ chốt khi xếp sprint.

## Mục tiêu demo

Đăng nhập bằng tài khoản học sinh, mở **Lịch học**, thấy lịch đúng khối từ MySQL dev, chuyển qua lại giữa các tuần và nhận được thông báo phù hợp khi tuần trống hoặc khi lỗi tải.

## Backlog

| Việc | Điều kiện hoàn thành | Phụ thuộc |
| --- | --- | --- |
| Kiểm tra schema trên MySQL dev | Migration tới head, có hồ sơ, lớp, buổi, đăng ký, bảng đổi ca và các cột mà API Weekly đọc. | Đối chiếu tên khóa và dữ liệu seed trước khi chạy. |
| Kiểm tra Weekly qua HTTP | Token hợp lệ, hai tuần có dữ liệu khác nhau, tuần trống, buổi khác khối và ca biên đầu tuần đều cho kết quả dự kiến. | Schema và dữ liệu MySQL dev. |
| Hiển thị một tuần | Dùng response để hiện nhãn ngày từ `week_start`. Dựng các cột rồi điền buổi theo ngày và ca đã thống nhất. | Có thể làm phần khung song song với MySQL. Hoàn thiện cách xếp ô sau khi chốt quy tắc ca. |
| Chuyển tuần | Hai mũi tên dịch đúng 7 ngày và tải đúng tuần. Kết quả cũ về trễ không ghi đè tuần đang xem. | Có response hiển thị được trên trang. |
| Tải, trống và lỗi | Tuần trống vẫn đổi được tuần. Khi lần tải hiện tại thất bại, giao diện hiển thị thông báo và giữ lịch tải thành công gần nhất nếu có. | Có luồng tải dữ liệu trong giao diện. |
| Demo tích hợp | Chạy từ đăng nhập đến đổi tuần trên app dùng MySQL dev và lưu kết quả kiểm tra. | Các việc phía trên. |

Điểm bắt đầu ở FE là lưu response đang log trong `WeeklyGrid` và dùng `week_start` để hiện nhãn giữa hai mũi tên. Phần MySQL có thể kiểm tra song song. Ghi nhận nếu một việc bị chặn bởi quyết định múi giờ hoặc phân ca.

## Kịch bản nghiệm thu

Chuẩn bị một học sinh đã xếp lớp, một học sinh cùng khối chưa xếp lớp, hai tuần liên tiếp có buổi khác nhau, một tuần trống và một buổi của khối khác. Thêm một lần đổi tạm đã lưu để kiểm tra API qua cả tuần gốc lẫn tuần đích. Dùng dữ liệu kiểm thử, chẳng hạn các tuần bắt đầu `2026-11-16`, `2026-11-23` và `2026-11-30`.

| Kiểm tra | Kết quả mong đợi |
| --- | --- |
| Gửi `week_start=2026-11-19` | API trả thứ Hai `2026-11-16`. FE hiện **16–22/11/2026**. |
| Học sinh chưa xếp lớp | Vẫn xem được lịch của khối mình. Buổi khác khối không xuất hiện. |
| Buổi bắt đầu đúng đầu thứ Hai | Chỉ có trong tuần bắt đầu vào thứ Hai đó. |
| Có hai buổi cùng ngày và ca | Cả hai đều hiển thị sau khi áp dụng quy tắc nhóm ca. |
| Chuyển sang tuần sau rồi quay lại nhanh | Nhãn và danh sách khớp lần chọn cuối kể cả khi phản hồi về đảo thứ tự. |
| Tuần trống | API trả `200` với danh sách rỗng. FE hiện trạng thái trống và điều hướng vẫn dùng được. |
| Thiếu hồ sơ hoặc lỗi tải | Thiếu hồ sơ hiện thông báo riêng. Nếu mất mạng, trang hiện lỗi cho lần tải hiện tại và giữ tuần đã chọn trong state. Lỗi về trễ từ lần tải cũ không ghi đè thông báo của lần tải mới. |
| Có lần đổi tạm qua hai tuần | API gắn ID buổi gốc và ID buổi đích ở tuần tương ứng. Hoàn thiện nhãn ca cá nhân là mốc sau của FE. |

Cuối sprint ghi ca đã chạy, môi trường chạy, kết quả và việc còn vướng. Mốc Weekly hoàn thành khi demo được cả luồng bằng MySQL dev. Việc gọi được API và thấy log chỉ hoàn thành bước nối request.

## Sau mốc Weekly

- Thêm nút **Thử lại** để tải đúng tuần đang chọn, ví dụ sau khi học sinh bật lại mạng. Khi thử lại thành công, bỏ thông báo lỗi.
- Cân nhắc tải lại tự động khi mạng trở lại. Nếu làm, kiểm tra lỗi từ lần thử cũ về trễ và tránh gửi trùng request với thao tác đổi tuần hoặc bấm **Thử lại**.

[Roadmap](../../PROJECT_ROADMAP.md) · [Đặc tả Weekly](../design/weekly.md) · [Thiết kế dữ liệu](../design/database.md)
