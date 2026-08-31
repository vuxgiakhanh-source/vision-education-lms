# 📚 BI KIP TOAN TAP: VISION LMS - BACKEND & FRONTEND

> Tai lieu nay tong hop toan bo thu vien, cong cu, cu phap duoc dung trong du an.

---

## PHaN BACKEND

---

## 1. Pydantic - Validate du lieu

**La gi?** Thu vien Python de dinh nghia 'khuon' du lieu.

```python
from pydantic import BaseModel
from typing import Optional

class LoginRequest(BaseModel):
    phone_number: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    must_change_password: bool

class UserProfile(BaseModel):
    full_name: str
    age: Optional[int] = None
    is_active: bool = True
```

**Khi nao dung?** Luon dung de dinh nghia Request (nhan vao) va Response (tra ra).

---

## 2. FastAPI - Web Framework

### Router - Khai bao endpoint

```python
from fastapi import APIRouter
router = APIRouter()

@router.get('/users')
def get_users(): ...

@router.post('/login')
def login(request: LoginRequest): ...

@router.put('/change-password')
def change_password(request: ChangePasswordRequest): ...

@router.delete('/users/{user_id}')
def delete_user(user_id: int): ...
```

### Depends - Dependency Injection (QUAN TRONG)

```python
from fastapi import Depends

# Dinh nghia dependency
def get_current_user_id(credentials = Depends(security)) -> int:
    return user_id

# Dung trong router - truyen TEN HAM, KHONG co ()
@router.put('/change-password')
def change_password(
    request: ChangePasswordRequest,
    user_id: int = Depends(get_current_user_id),
    service: ChangePasswordService = Depends(get_auth_service)
): ...
```

> QUY TAC VANG: Depends(ten_ham) - KHONG viet Depends(ten_ham())

### HTTPException - Tra loi HTTP

```python
from fastapi import HTTPException, status

raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token khong hop le')
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Du lieu sai')
raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Khong tim thay')
```

### HTTPBearer - Xac thuc Bearer Token

```python
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> int:
    token = credentials.credentials  # JWT sach (da cat 'Bearer ')
    ...
```

> FastAPI tu dong: tim header 'Authorization: Bearer TOKEN', cat 'Bearer ', neu khong co -> tra 403

---

## 3. SQLAlchemy - ORM Database

### Khai bao Model

```python
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Integer, Column, String, Boolean, Enum, DateTime

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    full_name = Column(String(255), nullable=False)
    phone_number = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    must_change_password = Column(Boolean, default=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
```

### Ket noi Database & Session

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("mysql+pymysql://user:password@localhost:3306/dbname")
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db   # cap db cho API dung
    finally:
        db.close() # tu dong dong du co loi hay khong
```

> Tai sao yield thay return?
> return -> ham ket thuc ngay, khong bao gio chay db.close() -> tran ket noi.
> yield -> tam dung, dua db ra dung, sau khi xong moi chay db.close().

### CRUD co ban

```python
# READ - Tim 1 record
user = db.query(User).filter(User.id == user_id).first()

# READ - Tim nhieu records
users = db.query(User).filter(User.is_active == True).all()

# UPDATE - Sua record
user.hashed_password = new_hashed_password
db.commit()   # phai commit de luu xuong database

# CREATE - Tao moi
new_user = User(full_name="Nguyen Van A")
db.add(new_user)
db.commit()
db.refresh(new_user)  # lay lai data sau insert

# DELETE
db.delete(user)
db.commit()
```

---

## 4. bcrypt - Ma hoa mat khau

**La gi?** Thuat toan bam mat khau mot chieu, khong the giai ma nguoc.

```python
from bcrypt import gensalt, hashpw, checkpw

# Bam mat khau (luu vao database)
def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")
    hashed_bytes = hashpw(password_bytes, gensalt())
    return hashed_bytes.decode("utf-8")

# Xac thuc mat khau khi dang nhap
def verify_password(password: str, hashed_password: str) -> bool:
    return checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
```

> Tai sao encode/decode? bcrypt lam viec voi bytes, khong lam viec voi str.
> .encode('utf-8') -> str -> bytes
> .decode('utf-8') -> bytes -> str

---

## 5. python-jose - JWT Token

**La gi?** Thu vien tao va giai ma JWT (JSON Web Token) - loai 'the can cuoc dien tu'.

### Cau truc JWT

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9   <- Header (thuat toan)
.eyJpZCI6MSwicm9sZSI6InN0dWRlbnQifQ    <- Payload (du lieu)
.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV   <- Signature (chu ky)
```

### Cu phap

```python
from jose import jwt, JWTError
from datetime import datetime, timezone, timedelta

ALGORITHM = "HS256"

# Tao token
def create_access_token(payload: dict, expires_delta: timedelta) -> str:
    copy_payload = payload.copy()
    copy_payload["exp"] = datetime.now(timezone.utc) + expires_delta
    return jwt.encode(copy_payload, SECRET_KEY, ALGORITHM)

# Giai ma token
def decode_access_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    # Tu dong raise JWTError neu: het han / bi sua / sai format

# Bat loi token
try:
    payload = decode_access_token(token)
except JWTError:
    raise HTTPException(status_code=401, detail="Token khong hop le")
```

### JWTError bat nhung loi nao?

| Tinh huong | Ket qua |
|---|---|
| Token het han (exp da qua) | JWTError |
| Token bi sua noi dung | JWTError |
| Token ky boi SECRET_KEY khac | JWTError |
| Token sai format | JWTError |

---

## 6. python-dotenv - Bien moi truong

**La gi?** Doc file .env va nap vao bien moi truong Python.

```python
from dotenv import load_dotenv
import os

load_dotenv()   # doc file .env, nap vao os.environ

value = os.getenv("SECRET_KEY")
value = int(os.getenv("EXPIRE_MINUTES"))
value = os.getenv("ORIGINS").split(",")
```

### Trong du an nay

```python
# backend/app/core/config.py
class Settings:
    def __init__(self):
        self.mysql_user = os.getenv("MYSQL_USER")
        self.mysql_password = os.getenv("MYSQL_PASSWORD")
        self.mysql_database = os.getenv("MYSQL_DATABASE")
        self.database_url = f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}@localhost:3306/{self.mysql_database}"
        self.secret_key = os.getenv("SECRET_KEY")
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
        self.allowed_origins = os.getenv("ALLOWED_ORIGINS").split(",")

settings = Settings()  # singleton - import va dung o moi noi
```

> LUON them .env vao .gitignore - khong bao gio commit file nay len Git.

---

## 7. loguru - He thong Log

**La gi?** Thu vien log dep hon print(), in mau ra terminal va ghi vao file.

```python
from loguru import logger

logger.info("Dang nhap thanh cong: ID 1")
logger.warning("SDT khong hop le")
logger.error("Loi ket noi database")
logger.debug("Dang xu ly request...")

# Dung f-string nhu binh thuong
logger.info(f'User ID {user.id} da dang nhap')
```

### Cau hinh cac handler

```python
logger.remove()   # xoa handler mac dinh

# Handler 1: In ra terminal co mau
logger.add(sys.stdout, colorize=True, level="INFO")

# Handler 2: Ghi vao file app.log, xoay khi >10MB
logger.add("logs/app.log", level="INFO",
    rotation="10 MB", retention="10 days", compression="zip")

# Handler 3: Ghi rieng loi vao error.log, co stack trace
logger.add("logs/error.log", level="ERROR",
    rotation="10 MB", retention="30 days", backtrace=True, diagnose=True)
```

---

## 8. Python Enum - Kieu liet ke

**La gi?** Dinh nghia tap hop cac hang so co ten. Tranh dung string 'admin', 'teacher' tuy tien.

```python
from enum import Enum

class UserRole(Enum):
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"

role = UserRole.ADMIN
role.value   # -> "admin"
role.name    # -> "ADMIN"

# Trong SQLAlchemy model:
role = Column(Enum(UserRole), nullable=False)

# Trong JWT payload:
{"id": user.id, "role": user.role.value}
```

---

## 9. Custom Exceptions - Loi tuy chinh

**La gi?** Tao class loi rieng cho tung tinh huong nghiep vu.

```python
# exceptions.py
class UserNotFoundException(Exception): pass
class WrongPasswordException(Exception): pass
class EmptyPasswordException(Exception): pass
```

```python
# service.py - nem loi
if not user:
    raise UserNotFoundException()
if not verify_password(password, user.hashed_password):
    raise WrongPasswordException()
```

```python
# router.py - bat loi va tra HTTP
try:
    return service.login(request)
except UserNotFoundException:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='...')
except WrongPasswordException:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='...')
```

> Tai sao khong raise HTTPException thang trong service?
> Service khong nen biet ve HTTP. Service chi lo nghiep vu.
> Router moi la noi quyet dinh loi nghiep vu -> HTTP status code nao.

---
---

## PHAN FRONTEND: KIEN TRUC, TOAN BO CONG CU & FRAMEWORK

---

## 9. Buc tranh toan canh: Day chuyen hoat dong cua Frontend

Hãy tưởng tượng toàn bộ Frontend của bạn là một **dây chuyền hoạt động khép kín**:

```text
[ Người dùng gõ URL trên trình duyệt ]
                  │
                  ▼
         1. REACT ROUTER DOM (Lễ tân chỉ đường)
                  │
                  ▼
         2. ROUTE GUARD (Bảo vệ soát vé)
            ──► Chưa có vé (Token)? ──► ĐÁ VỀ /login
            ──► Đang bắt đổi mật khẩu? ──► ÉP VÀO /change-password
            ──► Đủ điều kiện? ──► Cho phép đi tiếp
                  │
                  ▼
         3. PAGE & COMPONENT (Phòng khách & Bàn ghế của REACT)
            ──► Trang trí bằng TAILWIND CSS (Màu sắc, bo góc, căn giữa)
            ──► Ép khuôn chặt chẽ bằng TYPESCRIPT
                  │
                  ▼
         4. REACT HOOK FORM (Người ghi order của khách)
            ──► Lắng nghe từng phím người dùng gõ vào ô Input
                  │
                  ▼
         5. ZOD & RESOLVER (KCS - Kiểm định chất lượng dữ liệu)
            ──► Đúng 10 số điện thoại chưa?
            ──► Mật khẩu có để trống không?
            ──► KHÔNG ĐẠT ──► Báo lỗi đỏ lên màn hình ngay lập tức!
            ──► ĐẠT YÊU CẦU ──► Cho phép kích hoạt nút Bấm
                  │
                  ▼
         6. AXIOS (Người vận chuyển sang Backend FastAPI)
            ──► Interceptor tự móc Token từ LocalStorage gắn vào Header
            ──► Bắn request POST/PUT sang Backend
                  │
                  ▼
         7. KẾT QUẢ TỪ BACKEND VỀ
            ──► Lỗi ──► Báo lỗi server lên màn hình
            ──► Thành công ──► Lưu Token/Cờ vào LocalStorage
                              ──► REACT ROUTER đá sang /dashboard!
```

---

## 10. Cau truc Feature-Based: Thu muc nao chua cong cu nao?

Trong cấu trúc của bạn (`src/features/auth/login/`), mỗi thư mục con là "nhà" của một công cụ cụ thể:

| Thư mục con | Công cụ đảm nhiệm | Nhiệm vụ thực tế trong dự án |
|---|---|---|
| `types/` | **TypeScript** | Định nghĩa các khuôn dữ liệu (`LoginFormData`, `LoginResponse`) |
| `schemas/` | **Zod** | Viết luật kiểm tra dữ liệu (`loginSchema`: 10 số, không để trống) |
| `services/` | **Axios** | Viết hàm gọi API sang Backend (`loginService.login()`) |
| `components/` | **React + Tailwind + React Hook Form** | Form giao diện, ô input, nút bấm, bắt sự kiện gõ |
| `pages/` | **React + Tailwind** | Lắp ráp các component lại thành một trang hoàn chỉnh |
| `guards/` | **React Router DOM** | Người bảo vệ đứng gác cửa trang web (`ProtectedRoute`, `GuestRoute`) |

### 👉 Quy trinh 6 buoc chuan khi ban tu code 1 tinh nang moi:
1. **Bước 1**: Vào `types/` ➔ Khai báo kiểu dữ liệu cần nhận/trả về (TypeScript).
2. **Bước 2**: Vào `schemas/` ➔ Viết luật validate Zod.
3. **Bước 3**: Vào `services/` ➔ Viết hàm gọi API qua Axios.
4. **Bước 4**: Vào `components/` ➔ Viết giao diện Form, cắm Zod vào React Hook Form.
5. **Bước 5**: Vào `pages/` ➔ Lắp ráp thành màn hình hoàn chỉnh.
6. **Bước 6**: Vào `App.tsx` ➔ Đăng ký Route và bọc Route Guard bảo vệ.

---

## 11. Bang tong hop "Kho vu khi" Frontend (Doi chieu voi Python)

Dự án Frontend của bạn được xây dựng bằng **9 công cụ cốt lõi** trong `package.json`:

| Tên công cụ / Thư viện | Phiên bản | Nhiệm vụ chính trong dự án | Tương đương cái gì bên Python / Backend? |
|---|---|---|---|
| **React** | 19.x | Thư viện xây dựng giao diện bằng Component & State | Jinja2 Templates (nhưng React xịn hơn: tự đổi giao diện khi dữ liệu đổi) |
| **TypeScript** | 5.x / 6.x | Thêm kiểu dữ liệu vào JavaScript để bắt lỗi từ lúc gõ code | Type Hints trong Python (`def login(user_id: int) -> dict:`) |
| **Vite** | 8.x | Máy chủ chạy thử nghiệm (Dev Server) & đóng gói code siêu tốc | Uvicorn (khi chạy `uvicorn main:app --reload`) |
| **Tailwind CSS** | 4.x | Thiết kế giao diện bằng các class viết tắt trực tiếp trong HTML/JSX | CSS thuần (nhưng không cần tự đặt tên class lung tung) |
| **React Router DOM** | 7.x | Chuyển trang mượt mà (SPA) không bị giật/tải lại trang & Route Guard | APIRouter của FastAPI (nhưng chạy ngay trên trình duyệt) |
| **Zod** | 4.x | Định nghĩa "khuôn" dữ liệu và validate form ở giao diện | **Pydantic** (`BaseModel`) |
| **React Hook Form** | 7.x | Quản lý form nhập liệu, lưu dữ liệu ô gõ phím mà không lag | Form handling |
| **@hookform/resolvers** | 5.x | "Cầu nối" để cắm schema của Zod vào React Hook Form | Không cần bên Python vì FastAPI tự kết hợp Pydantic |
| **Axios** | 1.x | Bắn HTTP Request (POST, GET, PUT) sang Backend | Thư viện `requests` hoặc `httpx` của Python |

---

## 12. React 19 & JSX - Nen tang giao dien

### 1. Tai sao lai can React? (Neu dung JavaScript thuan thi kho the nao?)

#### 🔴 CÂU CHUYỆN 1: Nỗi ám ảnh khi làm bằng JavaScript thuần (Không có React)
Hãy tưởng tượng bạn đang làm chức năng **Giỏ hàng** cho một trang web bán hàng:
Trên màn hình lúc này có **4 chỗ** cùng hiển thị thông tin giỏ hàng:
1. Góc trên cùng bên phải: Icon xe đẩy hiển thị số lượng: `🛒 0`
2. Ở giữa trang: Cái nút bấm: `[Thêm vào giỏ]`
3. Ở cột bên phải: Danh sách các món đồ đã chọn.
4. Ở dưới chân trang: Dòng chữ tổng tiền: `Tổng: 0đ`

Bây giờ, người dùng bấm nút **[Thêm vào giỏ]**.
Nếu dùng **JavaScript thuần**, bạn (lập trình viên) phải tự tay viết code đi "săn lùng" từng thẻ HTML trên màn hình để sửa từng chữ một:
```javascript
// 1. Đi tìm icon xe đẩy để đổi số 0 thành số 1:
document.getElementById('cart-badge').innerText = "1";

// 2. Đi tìm cái nút vừa bấm để đổi chữ:
document.getElementById('add-btn').innerText = "Đã thêm vào giỏ";

// 3. Đi tìm cột danh sách bên phải để nhét thêm 1 dòng HTML vào:
document.getElementById('cart-list').innerHTML += "<li>Áo thun 500k</li>";

// 4. Đi tìm dòng tổng tiền ở chân trang để cộng tiền:
document.getElementById('total-price').innerText = "500.000đ";
```

😱 **NỖI ĐAU XUẤT HIỆN KHI:**
Người dùng bấm nút **[Xóa sản phẩm]**:
* Bạn lại phải tự tay viết code: trừ số ở xe đẩy về `0`, đổi chữ nút bấm quay lại thành `[Thêm vào giỏ]`, tìm đúng dòng `<li>` trong danh sách để xóa đi, rồi tính lại tổng tiền về `0đ`.
* **Hậu quả**: Chỉ cần bạn lỡ tay quên cập nhật 1 chỗ (ví dụ quên trừ tiền ở chân trang, hoặc icon xe đẩy vẫn hiện số 1 trong khi giỏ đã rỗng) ➔ **Giao diện bị loạn cào cào, dữ liệu một đằng hiển thị một nẻo!** Trang web càng to thì code JS thuần càng biến thành một bãi rác không ai dám sửa.

---

#### 🟢 CÂU CHUYỆN 2: React xuất hiện và giải cứu thế nào?
React đưa ra một triết lý làm thay đổi cả ngành công nghiệp web:
> **"Lập trình viên CHỈ CẦN QUẢN LÝ DỮ LIỆU. Còn việc sửa HTML trên màn hình, HÃY ĐỂ REACT TỰ LÀM!"**

Trong React, bạn chỉ cần tạo đúng 1 danh sách trong bộ nhớ (State):
```javascript
// Dữ liệu ban đầu: giỏ hàng rỗng
const [cart, setCart] = useState([]) 
```

Và trên giao diện JSX, bạn chỉ việc cắm biến `cart` vào các vị trí:
* Icon xe đẩy: `🛒 {cart.length}`
* Dưới chân trang: `Tổng tiền: {tính_tổng(cart)}`
* Danh sách: Duyệt qua `cart` vẽ ra từng món.

Bây giờ, khi người dùng bấm nút [Thêm vào giỏ], bạn chỉ cần làm **ĐÚNG 1 VIỆC DUY NHẤT**:
```javascript
setCart([...cart, "Áo thun 500k"]) // Thêm áo thun vào danh sách cart
```
**HẾT! BẠN KHÔNG CẦN LÀM GÌ NỮA CẢ!**
* Bạn không cần tìm thẻ xe đẩy.
* Bạn không cần tìm thẻ chân trang.
* Bạn không cần tìm thẻ danh sách.

Ngay khi `cart` có thêm đồ, **React sẽ tự động nhìn thấy và tự động cập nhật cả 4 vị trí trên màn hình cùng một lúc trong 0.001 giây!** Không bao giờ có chuyện xe đẩy hiện số 1 mà chân trang lại hiện 0đ.

---

#### 🎯 ÁP DỤNG THẲNG VÀO DỰ ÁN VISION LMS CỦA BẠN:
Nhìn vào form đăng nhập [LoginForm.tsx](file:///d:/vision-education-lms/frontend/src/features/auth/login/components/LoginForm.tsx):
Khi người dùng bấm nút **Đăng nhập**, nếu dùng JS thuần bạn sẽ phải:
* Đi tìm nút bấm đổi chữ thành "Đang đăng nhập...".
* Đi khóa nút bấm lại (`disabled = true`) để khách không bấm liên tục.
* Đi tìm chỗ hiện lỗi để xóa lỗi cũ.
* Khi API trả về lỗi ➔ Lại đi tìm cái hộp đỏ nhét chữ "Sai mật khẩu" vào.

Còn trong React của bạn hiện tại, mọi thứ chỉ phụ thuộc vào đúng 1 biến `isSubmitting`:
```tsx
<button disabled={isSubmitting}>
    {isSubmitting ? "Đang đăng nhập..." : "Đăng nhập"}
</button>
```
Khi gọi API ➔ `isSubmitting = true` ➔ Nút bấm **tự động khóa lại** và **tự động đổi chữ** mà bạn không cần đụng 1 ngón tay vào DOM!


---

### 2. Component - "Khối Lego giao diện"
Component trong React thực chất chỉ là **một hàm trả về HTML (JSX)**.
* **Quy tắc**: Tên Component bắt buộc phải **viết hoa chữ cái đầu** (PascalCase) để React phân biệt với thẻ HTML thông thường (thẻ `<button>` thường viết thường, còn `<LoginForm />` viết hoa).

---

### 3. `useState` - Bo nho cua Component (Vi du thuc te tu nut con mat mat khau)

Hãy xem đoạn code thực tế từ file [LoginForm.tsx](file:///d:/vision-education-lms/frontend/src/features/auth/login/components/LoginForm.tsx#L11):

```tsx
// 1. Khai bao State:
// - showPassword: bien luu gia tri hien tai (ban dau la false = dang an mat khau)
// - setShowPassword: ham chuyen dung de cap nhat gia tri moi cho showPassword
const [showPassword, setShowPassword] = useState(false)

// 2. Ap dung vao o Input:
// Neu showPassword la true -> type="text" (nhin thay mat khau)
// Neu showPassword la false -> type="password" (hien thi dau cham tron)
<input
    type={showPassword ? "text" : "password"}
    placeholder="Nhập mật khẩu"
    {...register("password")}
/>

// 3. Nut bam con mat:
// Khi nguoi dung click, dao nguoc gia tri (!showPassword: false -> true, true -> false)
<button type="button" onClick={() => setShowPassword(!showPassword)}>
    {showPassword ? <IconMatMo /> : <IconMatDong />}
</button>
```

👉 **Co che hoat dong tung micro-giay**:
1. Người dùng bấm vào nút con mắt ➔ Hàm `setShowPassword(true)` được gọi.
2. React phát hiện biến `showPassword` vừa đổi từ `false` sang `true`.
3. React **tự động vẽ lại (re-render) Component**: Thẻ `<input>` biến thành `type="text"`, icon chuyển thành mắt mở. Bạn không cần viết một dòng `document.getElementById` nào!

---

### 4. Props va `children` - Truyen du lieu giua cac Component

* **Props**: Giống như việc bạn truyền tham số vào hàm Python:
  ```tsx
  // Dinh nghia component con nhan vao Prop ten la 'label'
  function CustomLabel({ text }: { text: string }) {
      return <label className="text-sm font-semibold text-gray-700">{text}</label>
  }

  // Component cha goi va truyen du lieu:
  <CustomLabel text="Số điện thoại" />
  <CustomLabel text="Mật khẩu mới" />
  ```

* **`children`**: Khi bạn muốn nhét cả một khối giao diện vào bụng một component khác:
  ```tsx
  // Component KhungCard boc ben ngoai:
  function Card({ children }: { children: React.ReactNode }) {
      return (
          <div className="bg-white rounded-[32px] p-8 shadow-lg">
              {children}  {/* Noi dung con se duoc hien thi o day */}
          </div>
      )
  // Su dung:
  <Card>
      <h2>Dang nhap</h2>
      <p>Nhap thong tin de tiep tuc</p>
  </Card>
  ```

---

### 5. CAM NANG CU PHAP THUC CHIEN (SYNTAX CHEAT SHEET - TUNG DONG, TUNG KY TU)


#### Cú pháp 1: Khai báo một Component React
```tsx
export function TenComponent() {
    return (
        <div>
            <h1>Tiêu đề</h1>
        </div>
    )
}
```
* `export`: Để các file khác trong dự án có thể `import` vào dùng.
* `function TenComponent()`: Tên component **bắt buộc viết hoa chữ cái đầu** (PascalCase).
* `return (...)`: Phải có cặp ngoặc tròn `()`, bên trong là giao diện JSX.
* **Quy tắc**: Bên trong `return` chỉ được có **duy nhất 1 thẻ bọc ngoài cùng** (thường là `<div>` hoặc thẻ rỗng `<> ... </>`).

---

#### Cú pháp 2: Khai báo State (`useState`)
```tsx
import { useState } from 'react'

const [tên_biến, setTên_biến] = useState(giá_trị_ban_đầu)
```
* **Cấu trúc**: Luôn là một mảng gồm 2 phần tử trong ngoặc vuông `[ ]`:
  * `tên_biến`: Chứa giá trị hiện tại để đem đi hiển thị.
  * `setTên_biến`: Tên hàm dùng để đổi giá trị (luôn bắt đầu bằng chữ `set`).
* **Ví dụ thực tế**:
  ```tsx
  const [showPassword, setShowPassword] = useState(false) // ban đầu ẩn mật khẩu
  const [count, setCount] = useState(0)                  // ban đầu là số 0
  const [name, setName] = useState("")                   // ban đầu là chuỗi rỗng
  ```

---

#### Cú pháp 3: Bắt sự kiện bấm nút (`onClick`)
```tsx
<button type="button" onClick={() => setTên_biến(giá_trị_mới)}>
    Bấm vào đây
</button>
```
* `onClick`: Chữ `C` phải viết hoa.
* `() => ...`: Bắt buộc phải có hàm mũi tên `() =>` ở trước. Nếu bạn viết `onClick={setCount(1)}` thì hàm sẽ tự chạy ngay khi vừa mở trang web!
* **Ví dụ đảo ngược boolean true/false (như nút bật/tắt mắt mật khẩu)**:
  ```tsx
  <button type="button" onClick={() => setShowPassword(!showPassword)}>
  ```

---

#### Cú pháp 4: Khai báo Type cho Component nhận `children` (Dùng cho Route Guard)
```tsx
// Bước 1: Khai báo khuôn Props bằng type
type Props = {
    children: React.ReactNode
}

// Bước 2: Gắn khuôn vào Component
export function ProtectedRoute({ children }: Props) {
    return <>{children}</>
}
```
* `type Props = { ... }`: Định nghĩa khuôn cho tham số đầu vào.
* `children: React.ReactNode`: `children` là component con được bọc bên trong; `React.ReactNode` là kiểu dữ liệu cho phép con là bất kỳ thẻ JSX nào.
* `{ children }: Props`: Nhận `children` và ép theo khuôn `Props`.
* `<>{children}</>`: Cặp thẻ rỗng `<> </>` (React Fragment) bọc lấy `children` trả về.

---

#### Cú pháp 5: Làm việc với `localStorage` (Sổ tay trình duyệt)
```tsx
// 1. Lưu vào (chỉ lưu được chuỗi String):
localStorage.setItem('access_token', res.access_token)
localStorage.setItem('must_change_password', String(res.must_change_password)) // ép boolean thành string

// 2. Lấy ra:
const token = localStorage.getItem('access_token')

// 3. Lấy boolean ra để so sánh if:
const mustChange = localStorage.getItem('must_change_password') === 'true'

// 4. Xóa sạch khi Logout:
localStorage.clear()
```

---

#### Cú pháp 6: Điều hướng trang bằng React Router
* **Cách 1: Chuyển hướng tức thì bằng thẻ JSX (Dùng trong Route Guard)**:
  ```tsx
  import { Navigate } from 'react-router-dom'

  // Gặp lệnh này là trình duyệt lập tức bay sang /login:
  return <Navigate to="/login" replace />
  ```
  * `to="/login"`: Đường dẫn muốn đá người dùng đến.
  * `replace`: Ghi đè lịch sử duyệt web để người dùng không bấm nút Back quay lại được.

* **Cách 2: Chuyển hướng bằng code trong hàm submit**:
  ```tsx
  import { useNavigate } from 'react-router-dom'

  const navigate = useNavigate() // Gọi ở đầu component

  // Gọi trong hàm xử lý logic:
  navigate('/dashboard')
  ```

---

#### Cú pháp 7: Ráp toàn bộ cú pháp trên thành một Route Guard hoàn chỉnh
```tsx
import { Navigate } from 'react-router-dom'

// 1. Khuôn Props
type Props = {
    children: React.ReactNode
}

// 2. Component Guard
export function ProtectedRoute({ children }: Props) {
    // Lấy dữ liệu từ localStorage
    const token = localStorage.getItem('access_token')
    const mustChangePassword = localStorage.getItem('must_change_password') === 'true'

    // Kiểm tra 1: Chưa đăng nhập -> đá về login
    if (!token) {
        return <Navigate to="/login" replace />
    }

    // Kiểm tra 2: Chưa đổi mật khẩu lần đầu -> ép sang đổi mật khẩu
    if (mustChangePassword) {
        return <Navigate to="/change-password" replace />
    }

    // Hợp lệ -> Cho phép xem trang con
    return <>{children}</>
}
```

---


## 13. TypeScript - "Tam la chan" bat loi truoc khi chay

### 1. Tai sao can TypeScript? (So sanh truc quan voi JavaScript thuan)

* **Trong JS thuần**:
  ```javascript
  const user = { phoneNumber: "0912345678" }
  console.log(user.phone_number) // Go nham chu -> undefined! Khong bao loi gi ca, web van chay va sinh ra bug ngam!
  ```
* **Trong TypeScript**:
  ```typescript
  type User = { phoneNumber: string }
  const user: User = { phoneNumber: "0912345678" }
  console.log(user.phone_number) 
  // ❌ BI GACH DO LOOM NGAY LAP TUC:
  // "Property 'phone_number' does not exist on type 'User'. Did you mean 'phoneNumber'?"
  ```
  TypeScript giúp bạn bắt sạch 90% lỗi gõ nhầm chính tả ngay khi bạn còn đang gõ phím!

---

### 2. Dinh nghia khuon bang `type` (Giong Pydantic BaseModel)

Trong file [loginTypes.ts](file:///d:/vision-education-lms/frontend/src/features/auth/login/types/loginTypes.ts):
```typescript
// Khuon cho Form nhap lieu:
export type LoginFormData = {
    phoneNumber: string
    password: string
}

// Khuon cho Response tu Backend tra ve:
export type LoginResponse = {
    access_token: string
    token_type: string
    must_change_password: boolean
}
```

---

### 3. Generics `<T>` - "May dong hop da nang"

Hãy nhìn vào cách gọi API trong [loginService.ts](file:///d:/vision-education-lms/frontend/src/features/auth/login/services/loginService.ts):
```typescript
// Truyen <LoginResponse> vao sau ham post:
const res = await api.post<LoginResponse>('/login', data)
```
* **Nếu KHÔNG có `<LoginResponse>`**: Biến `res.data` sẽ có kiểu `any` (người mù). Bạn gõ `res.data.` sẽ không có gợi ý gì cả, nếu gõ nhầm `res.data.must_change_pasword` thì IDE cũng im lặng.
* **Khi CÓ `<LoginResponse>`**: IDE biết chính xác 100% bên trong `res.data` gồm có những trường gì:
  * `res.data.access_token` (string)
  * `res.data.must_change_password` (boolean)
  Gõ phím đến đâu, IDE gợi ý tự động (IntelliSense) đến đó!

---

## 14. Tailwind CSS v4 - Giai ma Form dang nhap sang trong cua ban

Hãy nhìn đoạn code tạo chiếc hộp Form đăng nhập trong [LoginForm.tsx](file:///d:/vision-education-lms/frontend/src/features/auth/login/components/LoginForm.tsx#L39):

```tsx
<div className="w-full max-w-[430px] bg-white rounded-[32px] p-8 sm:p-9 shadow-[0_20px_60px_-15px_rgba(0,0,0,0.1)] flex flex-col items-center border border-white">
```

Giải mã từng class Tailwind:
* `w-full`: Chiều rộng 100% (chiếm trọn màn hình điện thoại).
* `max-w-[430px]`: Nhưng trên màn hình to thì tối đa chỉ rộng 430px (không bị bè ngang xấu xí).
* `bg-white`: Màu nền trắng tinh khôi.
* `rounded-[32px]`: Bo tròn 4 góc cực kỳ mềm mại với bán kính 32px (chuẩn phong cách hiện đại).
* `p-8 sm:p-9`: Khoảng cách đệm bên trong (padding): trên mobile là 32px, trên tablet/desktop là 36px.
* `shadow-[0_20px_60px_-15px_rgba(0,0,0,0.1)]`: Đổ bóng mờ mịn màng tạo cảm giác chiếc hộp đang nổi bồng bềnh trên mặt bàn.
* `flex flex-col items-center`: Xếp tất cả phần tử bên trong (logo, tiêu đề, input, nút bấm) thành **một cột dọc thẳng hàng ở giữa**.

---

## 15. Zod - Kiem tra du lieu truoc khi gui

Hãy xem cách bạn viết luật kiểm tra trong [loginSchema.ts](file:///d:/vision-education-lms/frontend/src/features/auth/login/schemas/loginSchema.ts):

```typescript
import { z } from 'zod'

export const loginSchema = z.object({
    // Luat 1: So dien thoai
    phoneNumber: z.string()
        .length(10, 'Số điện thoại phải đúng 10 số')        // Bat buoc dung 10 ky tu
        .regex(/^[0-9]+$/, 'Số điện thoại chỉ được chứa chữ số'), // Bat buoc chi chua so tu 0-9
    
    // Luat 2: Mat khau
    password: z.string()
        .min(1, 'Mật khẩu không được để trống')             // Khong duoc la chuoi rong ""
})
```

### Cu phap nang cao: `.refine()` (Kiem tra 2 o phai trung nhau)
Trong [changePasswordSchema.ts](file:///d:/vision-education-lms/frontend/src/features/auth/change_password/schemas/changePasswordSchema.ts):
```typescript
export const changePasswordSchema = z.object({
    newPassword: z.string().min(1, 'Vui lòng nhập mật khẩu mới'),
    confirmNewPassword: z.string().min(1, 'Vui lòng xác nhận mật khẩu mới')
}).refine((data) => data.newPassword === data.confirmNewPassword, {
    // Neu 2 o khong giong nhau -> Gan loi vao o confirmNewPassword:
    message: 'Mật khẩu xác nhận không khớp',
    path: ['confirmNewPassword']
})
```

---

## 16. React Hook Form & @hookform/resolvers - Dieu phoi Form dinh cao

### 1. Tai sao khong dung `useState` cho Form?
Nếu một form có 10 ô input, bạn phải tạo 10 cái `useState`. Cứ mỗi lần người dùng gõ 1 chữ cái, toàn bộ trang web bị giật và re-render lại 10 lần ➔ Rất lag!
**React Hook Form** giải quyết triệt để: Nó lắng nghe ngầm và chỉ cập nhật khi nào submit hoặc có lỗi!

---

### 2. Mo xe tung dong khoi tao trong `LoginForm.tsx`:

```tsx
const {
    register,          // 1. Ham "cam day" noi the <input> vao bo dieu khien form
    handleSubmit,      // 2. Ham chan load lai trang mac dinh va goi Zod kiem tra truoc
    formState: {
        errors,        // 3. Object chua toan bo loi (neu Zod bao loi thi errors se co du lieu)
        isSubmitting   // 4. Bien boolean: true khi nguoi dung dang bam nut va cho API tra ve
    },
    setError           // 5. Ham dung de gan thu cong loi tu server tra ve (vi du: "Sai mat khau")
} = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema) // <-- Phep thuat nam o day: Bat tay truc tiep voi Zod!
})
```

---

### 3. Cach su dung tren the JSX:

```tsx
<form onSubmit={handleSubmit(onSubmit)}>
    {/* 1. Ket noi input bang cu phap spread {...register('phoneNumber')} */}
    <input {...register("phoneNumber")} />

    {/* 2. Neu o nay co loi tu Zod -> Hien thi dong chu do ngay duoi o input */}
    {errors.phoneNumber && (
        <p className="text-red-500 text-xs mt-1">{errors.phoneNumber.message}</p>
    )}

    {/* 3. Nut bam: Khi dang submitting thi doi chu va vo hieu hoa nut bam */}
    <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Đang đăng nhập..." : "Đăng nhập"}
    </button>
</form>
```

---

## 17. Axios - Ket noi API & Interceptors tu dong hoa

File [axios.ts](file:///d:/vision-education-lms/frontend/src/lib/axios.ts):

### 1. Request Interceptor (Tram thu phi tu dong)
Mỗi khi bạn gọi bất kỳ API nào (`api.get`, `api.post`, `api.put`), request đó bắt buộc phải đi qua cái "trạm thu phí" này trước khi bay sang Backend:

```typescript
api.interceptors.request.use((config) => {
    // 1. Tu dong mo so tay lay Token ra
    const token = localStorage.getItem('access_token')

    // 2. Neu co token -> Tu dong gan vao Header: "Authorization: Bearer <TOKEN>"
    if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`
    }

    return config // Cho phep request bay di tiep
})
```
👉 **Lợi ích**: Bạn không cần phải copy-paste dòng lấy Token ở 100 hàm gọi API khác nhau. Trạm thu phí này tự động dán vé cho tất cả!

---

### 2. Response Interceptor (Bo loc thong bao loi)
Khi Backend FastAPI trả lỗi về (ví dụ lỗi 400, 401 với format `{ "detail": "Sai mật khẩu" }`):

```typescript
api.interceptors.response.use(
    (response) => response, // Neu thanh cong -> Tra ve nguyen ven
    (error) => {
        // Tu dong trich xuat thong bao loi tu FastAPI backend:
        const message = error.response?.data?.detail || error.message || 'Đã có lỗi xảy ra'
        throw new Error(message) // Nem loi duoi dang chuoi tieng Viet sach se
    }
)
Nhờ có bộ lọc này, trong component của bạn chỉ cần viết:
```typescript
catch (error: any) {
    setError("root", { message: error.message }) // error.message da la chuoi dep de hien thi!
}
```


---

## 18. React Router DOM v7 & Route Guard

Điều phối người dùng vào đúng trang và "đá" ra ngoài nếu không đủ điều kiện.

* **`<BrowserRouter>`**: Bọc toàn bộ ứng dụng ở `App.tsx` để kích hoạt tính năng định tuyến.
* **`<Routes>` & `<Route path="..." element={<Trang />} />`**: Bảng ánh xạ từ URL vào Component.
* **`<Navigate to="..." replace />`**: Component tự động chuyển hướng ngay tức khắc.
* **`useNavigate()`**: Hook để chuyển hướng bằng code (ví dụ sau khi gọi API thành công: `navigate('/dashboard')`).
* **Route Guard**: Dùng Component bọc lấy trang cần bảo vệ để kiểm tra `localStorage`.

---

## 19. Vite & Bien moi truong

* Chạy dev: `npm run dev` (khởi động máy chủ Vite trên cổng 5173).
* File `.env`: Mọi biến môi trường ở Frontend **bắt buộc phải có tiền tố `VITE_`** thì Vite mới cho phép đọc:
  ```env
  VITE_API_URL=http://localhost:8000
  ```
* Đọc biến môi trường trong code:
  ```typescript
  const apiUrl = import.meta.env.VITE_API_URL
  ```

---
---

## KIEN TRUC

---

## 20. Luong du lieu end-to-end


### Luong Login

```
[1] User nhap SDT + mat khau vao LoginForm
    | Zod validate (length 10, regex so, min 1)
    v
[2] authService.login(data)
    | axios.post('/login', { phone_number, password })
    v
[3] Backend: POST /login
    | Pydantic parse body -> LoginRequest
    | LoginService.login()
    |   +-- len(phone_number) != 10 -> InvalidPhoneNumberException -> 400
    |   +-- len(password) == 0 -> EmptyPasswordException -> 400
    |   +-- user not found -> UserNotFoundException -> 401
    |   +-- verify_password() fail -> WrongPasswordException -> 401
    | Tao JWT token -> LoginResponse
    v
[4] Response: { access_token, token_type, must_change_password }
    v
[5] localStorage.setItem('access_token', token)
    +-- must_change_password = true -> navigate('/change-password')
    +-- must_change_password = false -> navigate('/dashboard')
```

### Luong Change Password

```
[1] User nhap mat khau moi + xac nhan
    | Zod validate + refine (2 field phai khop)
    v
[2] changePasswordService.changePassword(data)
    | axios.put('/change-password', { new_password })
    | (interceptor tu gan 'Authorization: Bearer TOKEN')
    v
[3] Backend: PUT /change-password
    | HTTPBearer() doc token tu header
    | get_current_user_id() giai ma JWT -> lay user_id
    |   +-- JWTError -> 401 Unauthorized
    | ChangePasswordService.change_password()
    |   +-- new_password rong -> EmptyNewPasswordException -> 400
    |   +-- user not found -> UserNotFoundException -> 404
    |   +-- new == old -> PasswordUnchangedException -> 400
    | hash_password(new_password) -> luu DB
    v
[4] Response: { message: 'Doi mat khau thanh cong' }
    v
[5] Hien thi success -> setTimeout 1500ms -> navigate('/dashboard')
```

---

## 21. Quy tac dat ten & Status Code

### HTTP Status Codes

---

## PHAN TYPESCRIPT & REACT NANG CAO (GIAI MA TOAN BO CU PHAP "LA")

---

## 22. Giai ma toan bo ky hieu & Cu phap "la" trong TypeScript / React

### 1. Dấu ngoặc nhọn `<T>` (Generics) - "Truyền kiểu dữ liệu như truyền tham số"

Trong TypeScript, bạn thường thấy dấu `<...>` đi kèm các hàm hoặc component. Đó gọi là **Generics**.
Nó giống như việc bạn gửi thêm "hướng dẫn" cho hàm biết nó đang làm việc với loại dữ liệu nào.

```typescript
// 1. Trong useState: Khai bao state co the la string hoac null
const [message, setMessage] = useState<string | null>(null)

// 2. Trong Axios: Bao cho Axios biet API se tra ve kieu LoginResponse
const res = await api.post<LoginResponse>('/login', data)
// -> TypeScript se biet luon res.data co field .access_token, .must_change_password!

// 3. Trong useForm: Bao cho React Hook Form biet form nay gom nhung o input nao
const form = useForm<LoginFormData>({ ... })
```

---

### 2. Cu phap `{ children }: { children: React.ReactNode }` la gi?

Day la cu phap gay "hoang mang" nhat cho nguoi moi hoc React + TS. Hay che no lam 2 nua:

```typescript
export function ProtectedRoute({ children }: { children: React.ReactNode })
//                             \___________/  \___________________________/
//                                Nua 1                   Nua 2
//                            (Destructuring)       (TypeScript Type)
```

* **Nửa 1: `{ children }` (Bóc tách Props)**
  Trong React, component con duoc boc ben trong component cha duoc goi la `children`.
  Thay vi viet:
  ```typescript
  function ProtectedRoute(props) {
      const children = props.children;
  }
  ```
  Nguoi ta viet tat thanh `{ children }`.

* **Nửa 2: `: { children: React.ReactNode }` (Dinh nghia kieu cho TypeScript)**
  * Dấu hai chấm `:` trong TypeScript nghia la "co kieu du lieu la".
  * `React.ReactNode`: La kieu du lieu dai dien cho **"bat cu thu gi React co the hien thi duoc"** (mot the JSX, mot chuoi chu, mot so, hoac nhieu the long nhau).

---

### 3. Destructuring - Boc tach phan tu ra khoi Object

Thay vi phai cham cham tung bien:
```typescript
// Cach cu, dai dong:
const form = useForm()
const register = form.register
const handleSubmit = form.handleSubmit
const errors = form.formState.errors

// Cach hien dai (Destructuring):
const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting } // boc tiep ben trong formState
} = useForm()
```

---

### 4. Dau ba cham `...` (Spread Operator) trong input

Khi viet: `<input {...register('phoneNumber')} />`
Dau `...` nghia la: "Lay toan bo cac thuoc tinh ma ham `register` tao ra, trai thang vao the `<input>`".
Nó tuong duong voi:
```tsx
<input 
    name="phoneNumber"
    onChange={...}
    onBlur={...}
    ref={...}
/>
```
Nho dau `...` ma ban khong can tu viet su kien onChange, luu state thu cong nua!

---

### 5. Dau `&&` va `? :` trong JSX (Render co dieu kien)

* **Toan tu `&&` (Neu dung thi hien thi):**
  ```tsx
  {errors.phoneNumber && (
      <p className="text-red-500">{errors.phoneNumber.message}</p>
  )}
  ```
  *Dich nghia:* "Neu co loi phoneNumber thi ve the `<p>` ra, neu khong co thi dung ve gi ca".

* **Toan tu 3 ngoi `condition ? <A /> : <B />` (If...Else):**
  ```tsx
  {isSubmitting ? "Dang dang nhap..." : "Dang nhap"}
  ```
  *Dich nghia:* "Neu dang submit thi chu la 'Dang dang nhap...', nguoc lai thi la 'Dang nhap'".

---

### 6. `localStorage` - Bo nho so tay tren trinh duyet

`localStorage` la bo nho luu tru key-value (chuoi - chuoi) cua trinh duyet, **F5 hay tat trinh duyet bat lai van con nguyen**.

| Ham | Muc dich | Vi du |
|---|---|---|
| `localStorage.setItem(key, value)` | Luu gia tri | `localStorage.setItem('access_token', token)` |
| `localStorage.getItem(key)` | Lay gia tri ra | `const token = localStorage.getItem('access_token')` |
| `localStorage.removeItem(key)` | Xoa 1 gia tri | `localStorage.removeItem('access_token')` |
| `localStorage.clear()` | Xoa sach tat ca | `localStorage.clear()` (khi logout) |

> ⚠️ **LUU Y QUAN TRONG**: `localStorage` CHI LUU DUOC CHUOI (STRING).
> - Muon luu boolean: `localStorage.setItem('must_change_password', String(res.must_change_password))` -> Luu thanh chuoi `'true'` hoac `'false'`.
> - Khi doc ra de so sanh boolean:
>   `const mustChange = localStorage.getItem('must_change_password') === 'true'` (so sanh voi chuoi `'true'`).

---

### 7. `<Navigate to="..." replace />` cua React Router

* **`<Navigate />` la gi?**
  La mot component dac biet cua `react-router-dom`. Khi React render ra component nay, trinh duyet lap tuc bi "boc dau" chuyen sang URL moi.
* **`replace` la gi?**
  Binh thuong khi chuyen trang, trinh duyet se them 1 trang vao Lich su (History).
  Khi them `replace`, no se **ghi de** trang hien tai trong lich su, nguoi dung se khong the bam nut "Back" tren trinh duyet de quay lai trang bi cam duoc.

---

### 8. Arrow Function `() => { ... }`

```typescript
// Ham truyen thong:
function cong(a, b) {
    return a + b;
}

// Arrow function (viet gon):
const cong = (a, b) => a + b;

// Dùng làm callback trong React (vi du nut bam):
<button onClick={() => setShowPassword(!showPassword)}>
```

---

---

## 23. Huong dan toan tap: Tu Code Route Guard tu A den Z

### Ban chat: Route Guard hoat dong the nao?

```
                      Nguoi dung go URL tren trinh duyet
                                    |
                                    v
                         [ ROUTE GUARD kiem tra ]
                                    |
         +--------------------------+--------------------------+
         |                                                     |
  (Chua du dieu kien)                                   (Du dieu kien hop le)
         |                                                     |
         v                                                     v
Tra ve <Navigate to="..." />                             Tra ve {children}
(Da nguoi dung sang trang khac)                     (Hien thi trang nguoi dung muon xem)
```

---

### File 1: Tao file `frontend/src/features/auth/guards/AuthGuard.tsx`

```tsx
import { Navigate } from 'react-router-dom'

// --------------------------------------------------------------------------
// 1. ProtectedRoute: Bao ve trang can dang nhap (Dashboard, etc.)
// --------------------------------------------------------------------------
export function ProtectedRoute({ children }: { children: React.ReactNode }) {
    const token = localStorage.getItem('access_token')
    const mustChangePassword = localStorage.getItem('must_change_password') === 'true'

    // Dieu kien 1: Chua dang nhap -> Da ve trang login
    if (!token) {
        return <Navigate to="/login" replace />
    }

    // Dieu kien 2: Da dang nhap nhung chua doi mat khau lan dau -> Ep sang trang doi mat khau
    if (mustChangePassword) {
        return <Navigate to="/change-password" replace />
    }

    // Neu hop le -> Cho phep xem trang
    return <>{children}</>
}

// --------------------------------------------------------------------------
// 2. ForceChangePasswordRoute: Dành rieng cho trang /change-password
// --------------------------------------------------------------------------
export function ForceChangePasswordRoute({ children }: { children: React.ReactNode }) {
    const token = localStorage.getItem('access_token')
    const mustChangePassword = localStorage.getItem('must_change_password') === 'true'

    // Chua dang nhap -> Khong duoc vao doi pass -> Da ve login
    if (!token) {
        return <Navigate to="/login" replace />
    }

    // Neu da doi mat khau roi (mustChangePassword = false) ma van mo /change-password -> Day vao dashboard
    if (!mustChangePassword) {
        return <Navigate to="/dashboard" replace />
    }

    return <>{children}</>
}

// --------------------------------------------------------------------------
// 3. GuestRoute: Dành rieng cho trang /login (Chi danh cho khach chua dang nhap)
// --------------------------------------------------------------------------
export function GuestRoute({ children }: { children: React.ReactNode }) {
    const token = localStorage.getItem('access_token')
    const mustChangePassword = localStorage.getItem('must_change_password') === 'true'

    // Neu da dang nhap roi:
    if (token) {
        // Neu chua doi mat khau lan dau -> Day sang /change-password
        if (mustChangePassword) {
            return <Navigate to="/change-password" replace />
        }
        // Neu da doi xong xuoi -> Day vao /dashboard
        return <Navigate to="/dashboard" replace />
    }

    // Chua dang nhap -> Cho phep xem form Login
    return <>{children}</>
}
```

---

### File 2: Cach lap vao `App.tsx`

```tsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { LoginPage } from './features/auth/login/pages/LoginPage'
import { ChangePasswordPage } from './features/auth/change_password/pages/ChangePasswordPage'
import { ProtectedRoute, GuestRoute, ForceChangePasswordRoute } from './features/auth/guards/AuthGuard'

// Trang Dashboard tam thoi de test
function DashboardPage() {
    return (
        <div className="p-8 text-center">
            <h1 className="text-2xl font-bold text-green-600">Trang Dashboard!</h1>
            <p className="mt-2 text-gray-600">Ban da dang nhap va doi mat khau thanh cong.</p>
            <button 
                onClick={() => {
                    localStorage.clear()
                    window.location.href = '/login'
                }}
                className="mt-4 px-4 py-2 bg-red-500 text-white rounded-lg"
            >
                Dang xuat
            </button>
        </div>
    )
}

export default function App() {
    return (
        <BrowserRouter>
            <Routes>
                {/* 1. Trang Login: Duoc bao ve boi GuestRoute (da login khong duoc vao nua) */}
                <Route 
                    path="/login" 
                    element={
                        <GuestRoute>
                            <LoginPage />
                        </GuestRoute>
                    } 
                />

                {/* 2. Trang Change Password: Chi ai chua doi pass lan dau moi vao duoc */}
                <Route 
                    path="/change-password" 
                    element={
                        <ForceChangePasswordRoute>
                            <ChangePasswordPage />
                        </ForceChangePasswordRoute>
                    } 
                />

                {/* 3. Trang Dashboard: Can dang nhap va da doi mat khau */}
                <Route 
                    path="/dashboard" 
                    element={
                        <ProtectedRoute>
                            <DashboardPage />
                        </ProtectedRoute>
                    } 
                />

                {/* Cac duong dan mac dinh */}
                <Route path="/" element={<Navigate to="/dashboard" replace />} />
                <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
        </BrowserRouter>
    )
}
```

---

*Tai lieu duoc cap nhat: 2026-08-31 - Toan bo kien thuc TypeScript, ES6+ va Route Guard*