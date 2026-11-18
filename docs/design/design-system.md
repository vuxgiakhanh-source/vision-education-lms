# Design system Vision Education LMS

Cập nhật ngày 19/11/2026. Bản ưng 2 ở cổng 5179 là tham chiếu giao diện của Weekly. Các quy ước dưới đây là bản thiết kế ban đầu để kiểm tra trên Weekly rồi áp dụng cho những màn hình có cùng nhu cầu. [Bản tham chiếu đã chọn](../../PROJECT_CONTEXT.md#điểm-dừng-1)

## Giá trị nền và vai trò

| Giá trị | Vai trò đề xuất | Ví dụ sử dụng |
| --- | --- | --- |
| Plus Jakarta Sans, sau đó dùng sans-serif hệ thống | Chữ giao diện | Tiêu đề, nội dung thẻ, nhãn và nút |
| `#F8FAFD`, `#FFFFFF` | Nền trang, nền khung nội dung | Dashboard và khung lịch |
| `#1E293B`, `#EAEFF5` | Chữ chính, viền nhẹ | Tiêu đề, chiều sâu của thẻ |
| `#5553E6`, `#EEF0FD` | Màu nhấn, nền nhấn nhẹ | Mục đang chọn, viền focus và nhãn ca cá nhân |
| `4 / 8 / 12 / 16 / 24 / 32 px` | Thang khoảng cách đề xuất | Nhóm nút, khoảng cách giữa thẻ, lề khung |

Tách ba mức khi đưa vào CSS. Mức đầu lưu giá trị gốc, ví dụ màu tím `#5553E6`. Mức thứ hai ghi vai trò, ví dụ màu nhấn. Mức thứ ba mô tả cách một component sử dụng vai trò đó, ví dụ viền focus của nút chuyển tuần. Khi chuyển thành CSS hoặc Tailwind, các component tham chiếu tên theo vai trò.

## Thành phần và trạng thái

| Thành phần | Trạng thái và hành vi |
| --- | --- |
| Khung trang | Dùng layout chung Dashboard. Khi đủ rộng, lịch ở trái và thẻ ở phải. Khi hẹp, đặt thẻ xuống dưới và cuộn ngang trong vùng bảng nếu cần. |
| Khung Weekly | Cùng một khung chứa tiêu đề **Lịch học**, mũi tên, nhãn khoảng ngày và lưới. Dùng cùng bố cục cho tuần trống và lỗi tải để vẫn thấy điều hướng tuần. |
| Nút icon | Chỉ hiện chevron. Tên truy cập **Tuần trước** và **Tuần sau**. Có kiểu thường, hover, focus nhìn thấy được và disabled khi hành động thực sự không khả dụng. Kích thước khởi điểm đề xuất là 40 × 40 px, đối chiếu lại với bản 5179. |
| Ô lịch | Có tiêu đề cột theo ngày và tiêu đề hàng theo ca. Ô có thể rỗng hoặc có nhiều buổi. Khi có nhiều buổi, giữ thứ tự giờ bắt đầu và cho xem đủ từng buổi. Nội dung và quy tắc xếp ca chi tiết còn chờ chốt. |
| Nhãn ca | Kèm chữ ở các trạng thái **Ca của bạn** và **Đã chuyển ca**, dùng màu hoặc biểu tượng để nhận ra nhanh hơn. |
| Trạng thái tải | Khi tải, giữ kích thước khung trong khả năng có thể. Khi tuần trống, hiện thông báo và vẫn cho đổi tuần. Khi lỗi tải có thể khôi phục, hiện thông báo và hành động **Thử lại**. |
| Thẻ buổi tiếp theo | Hiện khối, ngày giờ và nội dung dạy. Cách tìm buổi nếu tuần đang xem không có buổi tương lai còn chờ chốt. |
| Nút đổi lịch | Mở lựa chọn đổi tạm hoặc đổi cố định ở mốc đổi lịch. Cần quy định focus khi mở và đóng phần chọn. |

Khi nghiệm thu, đối chiếu với bản tham chiếu trên laptop và kiểm tra ở màn hẹp. Dùng Tab để tới hai nút, dùng Enter hoặc Space để chuyển tuần. Kiểm tra chữ, focus và nhãn ca trong trạng thái thường, tải, trống và lỗi. Các giá trị đề xuất cần được đối chiếu độ tương phản và kích thước thực tế trước khi khóa thành quy ước dùng chung.

[Đặc tả Weekly](weekly.md) · [Sprint Weekly](../planning/weekly-sprint.md)
