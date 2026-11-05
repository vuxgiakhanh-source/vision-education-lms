# Ví dụ tham chiếu và cách kiểm tra

Làm bài trong chương trước, sau đó đối chiếu. Các file ở đây không import vào
frontend/backend sản phẩm. Test domain dùng repository giả; test ví dụ transaction
dùng SQLite trong bộ nhớ. Không kết nối database sản phẩm hoặc cài thêm gói tự động.

## Python: bài nộp và chấm số

- `domain.py`: object, Protocol, repository giả, service và validation điểm/số.
- `test_domain.py`: các tình huống đúng/sai theo hợp đồng chương 10–11.

Từ gốc repo với môi trường hiện có:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s docs/course/examples -p "test_domain.py" -v
```

Nếu dùng Python 3.12+ khác, thay đường dẫn Python phù hợp. Test không cần FastAPI,
SQLAlchemy hoặc MySQL. Chúng không chứng minh transaction, auth JWT hay HTTP.

## TypeScript: dữ liệu nhiệm vụ

- `tasks.ts`: type, hàm thuần và parse unknown có kiểm tra runtime.
- `tasks.test.ts`: ví dụ assertion không cần framework test mới.

Kiểm tra kiểu bằng compiler frontend hiện có, từ gốc repo:

```powershell
.\frontend\node_modules\.bin\tsc.cmd --noEmit --strict --skipLibCheck --target ES2023 --module ESNext --moduleResolution bundler --allowImportingTsExtensions docs/course/examples/tasks.ts docs/course/examples/tasks.test.ts
```

Chạy bằng Node 24 đang có tại máy, hỗ trợ loại bỏ các kiểu TypeScript dùng ở đây:

```powershell
node docs/course/examples/tasks.test.ts
```

Node chạy file TS không tự kiểm tra kiểu; vì vậy cần cả bước tsc. Không dùng enum
TypeScript hoặc cú pháp cần biến đổi thêm trong bài này. `package.json` chỉ xác
định ESM cho thư mục ví dụ, không thêm thư viện hay script vào ứng dụng.

## Ví dụ giải thích từng dòng trong sách

```powershell
node docs/course/examples/teaching-examples.test.cjs
.\.venv\Scripts\python.exe -m unittest discover -s docs/course/examples -p test_teaching.py -v
```

JavaScript kiểm vòng lặp, callback, giữ tham chiếu và async/await với client giả.
Bốn test Python kiểm trung bình giữ điểm 0, service với reader giả, commit hai
bản ghi và rollback khi lỗi sau flush đầu tiên. Hai test cuối cần SQLAlchemy
đã có trong venv và dùng SQLite trong bộ nhớ. Không chạy HTTP/MySQL thật.
Ví dụ React được parse như TSX; chưa được render bằng React trong bộ test này.

## Cách dùng để học bằng tay

1. Viết implementation của mình trong thư mục thực hành riêng do mình chọn.
2. Đọc hợp đồng và viết vài test trước khi xem implementation tham chiếu.
3. Chạy, dự đoán và giải thích mỗi kết quả; không chỉ chép đến khi xanh.
4. Thay yêu cầu: cho nộp muộn có phép hoặc thêm một lượt làm; cập nhật cả đặc tả và test.
5. Khi chuyển vào sản phẩm, chốt yêu cầu và thêm kiểm tra HTTP/DB/quyền thực tế.
