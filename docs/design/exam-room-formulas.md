# Phòng thi ảo: đọc công thức MathType

Cập nhật ngày 24/11/2026. Phần của [thiết kế nhập đề](exam-room-import.md). Mã nguồn: `backend/app/modules/exams/imports/readers/` (`mathtype.py`, `mtef.py`, `mtef_latex.py`).

## Vấn đề

Đề Word của cô gõ công thức bằng **MathType**. Trong tệp `.docx`, mỗi công thức là một đối tượng OLE (`word/embeddings/oleObjectN.bin`) kèm một ảnh WMF/EMF. Ảnh trình duyệt không hiển thị được, và chữ trích từ tệp không có công thức. Nếu chỉ dùng ảnh thì không tráo được phương án, không so sánh được hai phương án giống nhau và không hiển thị sắc nét.

## Ba nguồn, theo thứ tự tin cậy

| Nguồn | Nội dung | Độ tin cậy |
| --- | --- | --- |
| `mathtype_tex` | LaTeX do **chính MathType ghi sẵn** trong đối tượng (sau chuỗi `TeX Input Language`) | Chính xác, không phải đoán |
| `mtef_decoded` | Giải mã nhị phân MTEF v5 thành LaTeX | Tin cậy theo từng cấu trúc, xem bảng dưới |
| Ảnh | Ảnh WMF/EMF của chính MathType | Luôn có, là dự phòng |

Bộ đọc luôn giữ ảnh, kể cả khi đã có LaTeX, để cô đối chiếu.

## Nguyên tắc: không đoán

- Cấu trúc lạ, ký tự lạ, màu, chỉnh tay (nudge), thước tab, MTEF đời cũ (v3): **từ chối giải mã** và giữ ảnh.
- Dữ liệu có thừa hay thiếu một byte, bản ghi chưa cân bằng, lồng quá sâu: báo lỗi, không đọc tiếp.
- Công thức giải mã bằng cấu trúc **chưa có công thức thật để đối chiếu** bị đánh dấu `latex_unverified`, và câu chứa nó bị gắn cờ `formula_unverified` để cô so với ảnh trước khi phát đề.

## Cách kiểm chứng

Có 98 công thức trong đề thật vừa mang LaTeX do MathType ghi sẵn, vừa có dữ liệu nhị phân. Chúng là **đáp án chuẩn** để đo bộ giải mã mà không cần người chấm. Ngày 24/11/2026, bộ giải mã khớp **98/98** (sau khi chuẩn hóa các cách viết hiển thị giống hệt nhau như `x^{2}` và `x^2`, `\mathrm` và `\text`, khoảng trắng).

Cấu trúc đã khớp thật (danh sách `VERIFIED_FEATURES`): ký tự thường, chữ trong `\text`, ký hiệu, dấu cách, vectơ (`\overrightarrow`), viền mũi tên trên một ký tự, thanh ngang trên một ký tự, phân số, căn bậc hai, chỉ số trên, giới hạn.

Chưa có công thức thật để đối chiếu, nên bị gắn cờ: chữ Hy Lạp, tên hàm (`sin`, `cos`), chỉ số dưới, ngoặc (tròn, đứng, khoảng), mũ trên nhiều chữ. Đây không có nghĩa chúng sai, chỉ là chưa được chứng minh bằng dữ liệu thật.

Test khóa hành vi này: `backend/tests/test_exam_mtef.py` dùng byte công thức thật làm dữ liệu cố định, cắt cụt ở mọi vị trí, làm hỏng ngẫu nhiên 4000 lần (chỉ được phát sinh hai loại lỗi dự kiến), và có test riêng bảo đảm mọi cấu trúc trong danh sách tin cậy đều xuất hiện trong ít nhất một công thức thật đã khớp.

## Kết quả đo trên đề thật của cô

| Tệp | Công thức | LaTeX do MathType ghi | Giải mã, cấu trúc đã khớp | Giải mã, cần xem | Chỉ ảnh |
| --- | --- | --- | --- | --- | --- |
| Mã 102 | 106 | 25 | 66 | 11 | 4 |
| Mã 104 | 106 | 25 | 66 | 11 | 4 |
| Tiệm cận (s03) | 97 | 48 | 21 | 28 | 0 |
| Hàm số (s04) | 10 | 0 | 7 | 3 | 0 |
| HSG (s05) | 5 | 0 | 0 | 5 | 0 |

Toàn bộ đối tượng: 345. Giải mã được 332; từ chối 4 (thước tab); báo lỗi 8 (Equation Editor 3.0 đời cũ, MTEF v3); 1 tệp OLE hỏng.

## Giới hạn

- Mới kiểm chứng trên đề của một cô và một vài tệp. Đề dùng nhiều cấu trúc khác (tích phân, ma trận, hệ phương trình, tổng) sẽ bị từ chối và dùng ảnh cho đến khi có công thức thật để thêm vào.
- Tên và vị trí cấu trúc theo đặc tả MTEF v5 và bảng mã của MathType; một số mã (ví dụ ký tự ngoặc riêng của MathType) được suy từ dữ liệu thật và nằm trong nhóm chưa kiểm chứng.
- Công thức giải mã ra LaTeX vẫn cần được hiển thị bằng KaTeX trên giao diện và so với ảnh ở màn duyệt. Phần giao diện đó chưa viết.
- Mã tham chiếu bên ngoài (Apache-2.0) chỉ được đọc để lấy đặc tả, không được chạy hay đưa vào dự án.
