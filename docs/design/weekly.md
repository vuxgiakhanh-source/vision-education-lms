# Đặc tả kỹ thuật Weekly

Cập nhật ngày 19/11/2026. Mốc này giúp học sinh mở `/schedule`, xem lịch đúng khối từ API và chuyển tuần. Học sinh có hồ sơ nhưng chưa xếp lớp vẫn xem được lịch cả khối. Thẻ buổi tiếp theo, thao tác đổi ca và cập nhật thời gian thực nằm ở các mốc sau.

## Luồng gọi và hiện trạng

1. Sidebar điều hướng tới `/schedule`. Next.js mở `ScheduleRoute` → `SchedulePage` → `WeeklyGrid`.
2. `WeeklyGrid` khởi tạo `selectedDate` bằng `formatLocalDate(new Date())`. `useEffect` gọi `loadWeek()` khi mở trang hoặc khi ngày đang chọn thay đổi. `weeklyScheduleService.getWeeklySchedule(selectedDate)` gửi Axios request và trả `res.data`.
3. FastAPI xác thực JWT qua `get_current_user_id` rồi gọi `get_weekly_schedule` → `WeeklyScheduleService.get_weekly_sessions`. Service tìm khối và tính khoảng từ thứ Hai 00:00 đến trước thứ Hai kế tiếp. Repository chỉ lấy buổi `scheduled` của đúng khối trong khoảng đó. Khi có buổi, service đối chiếu đăng ký có hiệu lực và lần đổi để phân loại ID.
4. FE dùng một response để cập nhật cả khoảng ngày và danh sách. Tại thời điểm kiểm tra, `WeeklyGrid` đã gọi service và log `week_start`. State phản hồi, bảng và thao tác hai mũi tên cần làm tiếp.

[Route Schedule](<../../frontend/src/app/(student)/student-schedule/page.tsx>) · [WeeklyGrid](../../frontend/src/features/student/schedule/weekly/components/WeeklyGrid.tsx) · [Router Weekly](../../backend/app/modules/schedule/student/weekly/router.py)

## Hợp đồng API đang có

`GET /schedule/weekly?week_start=2026-11-19` dùng JWT Bearer. Query nhận ngày được chọn, kể cả ngày giữa tuần. Ví dụ sau minh họa phản hồi khi không có buổi:

```json
{
  "week_start": "2026-11-16",
  "sessions": [],
  "my_session_ids": [],
  "transferred_session_ids": []
}
```

| Trường | Kiểu JSON | Cách dùng |
| --- | --- | --- |
| `week_start` | Chuỗi ngày `YYYY-MM-DD` | Ngày thứ Hai. Dựng bảy cột và nhãn ngày từ mốc này. |
| `sessions` | Mảng các mục `{ id, topic, starts_at, ends_at }` | `id` là số, các trường còn lại là chuỗi. Backend sắp theo giờ bắt đầu rồi ID. |
| `my_session_ids` | Mảng số | Buổi được service xác định là ca của học sinh. |
| `transferred_session_ids` | Mảng số | Buổi gốc đã chuyển ca được service đánh dấu trong tuần đang xem. |

Tuần trống là `200` với danh sách rỗng. Router trả `403` nếu tài khoản thiếu hồ sơ học sinh. Ngày sai định dạng bị validation từ chối. Xử lý lỗi mạng và lỗi máy chủ bằng thông báo phù hợp. Với lỗi có thể thử lại, dùng ngày đang chọn cho request tiếp theo. [Schema API](../../backend/app/modules/schedule/student/weekly/schemas.py) · [Dependency xác thực](../../backend/app/core/dependencies.py)

## Thiết kế phần FE tiếp theo

- Giữ `selectedDate` là ngày người dùng đang yêu cầu. Mũi tên dịch ngày đó đi 7 ngày theo lịch, kể cả khi qua tháng hoặc năm.
- Giữ response đã nhận để dựng khoảng từ thứ Hai tới Chủ nhật và danh sách buổi. Dùng cùng một response cho cả nhãn ngày và lưới để tránh hiện buổi của tuần cũ dưới tiêu đề tuần mới.
- Chỉ cho request của lần chọn mới nhất cập nhật state. Kiểm tra bằng cách giả lập hai phản hồi về đảo thứ tự. Có thể bỏ qua kết quả cũ khi effect được dọn dẹp hoặc hủy request sau khi service hỗ trợ tín hiệu hủy.
- Dựng lưới bảy cột ngày và các hàng ca. Mỗi ô có thể có nhiều buổi. Trong khi chưa chốt quy tắc ca cho buổi ngoài khung hoặc dời giờ, làm trước dữ liệu và khung lưới, rồi xác định quy tắc nhóm buổi trước khi nghiệm thu.
- Xử lý tải lần đầu, chuyển tuần, tuần trống, thiếu hồ sơ và lỗi tải. Hai mũi tên giữ nhãn truy cập. Khi mở lịch trực tiếp bằng URL, dùng cùng route và luồng dữ liệu.

## Quyết định còn mở

- **Múi giờ.** Đề xuất dùng múi giờ của trung tâm để tính hôm nay, biên tuần và cột ngày. Cần xác nhận cách ghi và diễn giải `starts_at` và `ends_at` từ MySQL qua API tới FE. Hiện helper FE lấy ngày theo giờ của môi trường chạy, còn model dùng cột DateTime.
- **Xếp ca.** Xác nhận cách nhóm buổi dời giờ, buổi ngoài khung ca và nhiều buổi trong một ô. API hiện có giờ và ID buổi, chưa trả mã ca.
- **Các mốc tiếp theo.** Chốt cách xác định buổi tiếp theo khi vượt sang tuần khác, cách xác nhận ca cùng tuần dạy và cách cập nhật lịch đang mở khi thay đổi.

[Thiết kế dữ liệu](database.md) · [Quy ước giao diện](design-system.md) · [Tiêu chí nghiệm thu và sprint](../planning/weekly-sprint.md)
