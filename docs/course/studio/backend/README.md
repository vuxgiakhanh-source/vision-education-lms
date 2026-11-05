# Xưởng G3–G4: từ Python quen thuộc đến tính năng xuyên hệ thống

G3 dùng **thư viện chuẩn Python**, không cần FastAPI/SQLAlchemy. G4 dùng bản
copy của `docs/course/workshop`, không thay backend hay database sản phẩm.
Đọc bài tương ứng, tự gõ/thử rồi mở source để đối chiếu.

## G3 — Chạy từ thư mục này

```powershell
Set-Location D:\vision-education-lms\docs\course\studio\backend
python -X utf8 singlefile.py
python -X utf8 main.py
python -X utf8 -m unittest discover -s . -p test_use_cases.py -v
```

`singlefile.py` in2 dòng: tạo lớp 1Pythonactive, số lớp 1. `main.py` in4 dòng:
tạo lớp, archived, lịch sử 1, lớp cô khác 0. Bộ test có 9 test, cần `OK`.

| File | Trách nhiệm |
|---|---|
| singlefile.py | Bản ban đầu create/list trong một file để so hành vi |
| domain.py | Kiểm title, role, owner trên các giá trị |
| storage.py | Đọc/ghi dict RAM, trả bản copy |
| use_cases.py | Điều phối create/list/archive |
| main.py | Lắp kho/actor và quan sát output |
| test_use_cases.py | Kiểm kết quả, scope và kho không đổi khi lỗi |

Actor còn là dict giả do chương trình tạo. RAM mất khi process kết thúc.
Không có HTTP/auth/transaction nhiều bước. Source minh họa lý do chia file;
không phải kiến trúc bắt buộc cho mọi ứng dụng.

## G4 — Chuẩn bị bản copy mới, không ghi đè

Tạo gốc repo học riêng như dưới; G0 không tự dựng thư mục/Git thay mày. Đổi
đường dẫn nguồn nếu di chuyển sách. Script từ chối đích có sẵn; chọn tên mới
khi cần so đáp án. Đọc G4.1 để thêm .gitignore trước khi commit source.

```powershell
$learningRoot = 'D:\lms-tu-hoc'
New-Item -ItemType Directory -Force -Path $learningRoot
Set-Location $learningRoot
Get-Location
git --version
git init
git status --short
python -X utf8 D:\vision-education-lms\docs\course\studio\backend\prepare_workshop.py .\lab-workshop
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r .\lab-workshop\requirements.txt -r .\lab-workshop\deploy\requirements.txt
```

Môi trường đã có `.venv` thì dùng lại. Script bỏ `node_modules`, `dist`,
cache và DB. Theo [G4](../../G4-thiet-ke-tinh-nang-xuyen-he-thong.md) để init
SQLite học, giữ server/token/secret đúng terminal và nối frontend.

## Đáp án archive — Chỉ mở sau lần tự làm

`class-feature-split.patch` là đáp án riêng cho G4.4: chuyển lớp học vào
package classes, nối đủ router/dependency và shim cho imports cũ. Dùng bản
copy gốc mới `lab-split` và thay tên patch/đích ở các lệnh bên dưới. Không áp
nối nó với archive patch. Test bản tách dự kiến 28 tổng: 26 pass, 2 skip MySQL.

Từ gốc repo học, tạo bản source gốc tên `lab-answer`, rồi kiểm patch trước
khi áp. Nếu đã sửa bản tự làm, không dùng nó làm đích đáp án.

```powershell
python -X utf8 D:\vision-education-lms\docs\course\studio\backend\prepare_workshop.py .\lab-answer
git apply --check --directory=lab-answer D:/vision-education-lms/docs/course/studio/backend/archive-solution.patch
git apply --directory=lab-answer D:/vision-education-lms/docs/course/studio/backend/archive-solution.patch
.\.venv\Scripts\python.exe -X utf8 -m unittest discover -s .\lab-answer -p "test_*.py" -v
```

Expected 35 test:33 pass,2 skip MySQL nếu chưa cấp DB MySQL thử riêng. Bao gồm
26 test gốc đang chạy được và 7 test archive/migration mới. Test chỉ dùng SQLite
tạm trong RAM và ASGI nội bộ; không gọi DB sản phẩm. Test MySQL không tự chạy
khi chưa cấu hình. Không chứng minh capacity hoặc browser hoạt động trọn luồng.

Frontend đáp án: chuyển vào `lab-answer/frontend`, chạy `npm ci` và
`npm run build`. Build phải qua TypeScript strict và Vite. Sau đó chạy
`npm run dev` với server riêng, test bằng browser theo bảng policy G4.6.

Patch gồm model/DTO/repository/service/route/workflow, parser/component,
migration 0002 và test. Hai file `archive_test_solution.py` và
`archive_migration_test_solution.py` là bản đọc riêng của test có trong patch;
không chạy chúng ngay tại G3 vì chúng cần package của bản xưởng đã vá.

Đáp án giữ lịch sử, chặn giao/nộp mới sau archive, cho retry cùng bài cũ và
chấm/công bố điểm cũ. Mở lại lớp là bài độc lập chưa cấp implementation.
DB cũ cần migration; sửa model rồi create_all không tự thêm cột cũ.

## Kiểm chứng của người soạn

G3:9/9 test qua. Patch đã kiểm khớp bản xưởng,33 test qua/2MySQLskip; gồm test
nâng từ migration 0001 có lớp cũ. Frontend patched TypeScript/Vite build qua.
ASGI trong sandbox Windows có thể treo threadpool; bản kiểm soạn đã chạy
terminal ngoài sandbox với SQLite tạm, không đổi endpoint để né lỗi đó.

Chưa chạy race MySQL, browser trọn luồng archive, k6 hay deployment. Các thư mục
`.archive-check`/`_validation` nếu xuất hiện chỉ là bản kiểm tạm bị gitignore,
không thuộc source bài và không được dùng thay repo học của mày.
