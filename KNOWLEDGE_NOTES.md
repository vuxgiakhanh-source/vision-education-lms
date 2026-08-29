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

## PHaN FRONTEND

---

## 10. Zod - Validate Form

**La gi?** Thu vien TypeScript de dinh nghia schema va validate du lieu form. Tuong tu Pydantic.

### Cu phap co ban

```typescript
import { z } from 'zod'

const schema = z.object({
    phoneNumber: z.string()
        .length(10, 'Phai co 10 chu so')
        .regex(/^\d+$/, 'Chi duoc chua so'),
    password: z.string().min(1, 'Khong duoc de trong'),
    email: z.string().email('Email khong hop le'),
    age: z.number().min(18, 'Phai du 18 tuoi'),
})
```

### Cu phap nang cao - refine (validate lien truong)

```typescript
const changePasswordSchema = z.object({
    newPassword: z.string().min(1, 'Khong duoc de trong'),
    confirmNewPassword: z.string().min(1, 'Khong duoc de trong')
}).refine(
    (data) => data.newPassword === data.confirmNewPassword,
    {
        message: 'Mat khau xac nhan khong trung khop',
        path: ['confirmNewPassword']
    }
)
```

### Lay TypeScript type tu schema

```typescript
// Khong can viet type rieng - infer tu dong tu schema
type LoginFormData = z.infer<typeof loginSchema>
```

---

## 11. React Hook Form - Quan ly Form

**La gi?** Thu vien quan ly state form trong React.

```typescript
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'

const {
    register,          // ket noi input voi form
    handleSubmit,      // wrapper ham submit
    formState: {
        errors,        // object chua loi cua tung field
        isSubmitting   // true khi dang submit (goi API)
    },
    setError           // set loi thu cong (dung cho loi tu server)
} = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema)  // ket noi voi Zod
})
```

### Ket noi input voi form

```typescript
// {...register('fieldName')} tu dong gan: name, onChange, onBlur, ref
<input {...register('phoneNumber')} type='tel' />
<input {...register('password')} type='password' />

// Hien thi loi
{errors.phoneNumber && <p>{errors.phoneNumber.message}</p>}
```

### Xu ly submit

```typescript
async function onSubmit(data: LoginFormData) {
    // data da duoc Zod validate, chac chan dung format
    try {
        const res = await authService.login(data)
    } catch (error: any) {
        // loi tu server -> gan vao 'root'
        setError('root', { message: error.message })
    }
}

<form onSubmit={handleSubmit(onSubmit)}>
    <button type='submit' disabled={isSubmitting}>
        {isSubmitting ? 'Dang xu ly...' : 'Dang nhap'}
    </button>
</form>
```

```typescript
// Hien thi loi server
{errors.root && <div>{errors.root.message}</div>}
```

---

## 12. Axios - Goi HTTP API

**La gi?** Thu vien JavaScript de goi HTTP request den backend.

```typescript
import axios from 'axios'

const api = axios.create({
    baseURL: 'http://localhost:8000',
    timeout: 10000   // 10 giay
})

api.get('/users')
api.post('/login', { phone_number, password })
api.put('/change-password', { new_password })
api.delete('/users/1')

// Lay data tu response - Axios boc response trong .data
const res = await api.post<LoginResponse>('/login', body)
const data = res.data   // moi la data thuc su
```

### Interceptors - Middleware tu dong

```typescript
// Request Interceptor - chay TRUOC KHI request bay di
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token')
        if (token && config.headers) {
            config.headers.Authorization = `Bearer ${token}`
        }
        return config   // phai return config
    },
    (error) => { throw error }
)

// Response Interceptor - chay KHI response ve
api.interceptors.response.use(
    (response) => response,    // thanh cong -> tra nguyen
    (error) => {
        const message = error.response?.data?.detail || error.message || 'Loi khong xac dinh'
        throw new Error(message)
    }
)
```

> Luu y: Frontend dung camelCase (phoneNumber), backend dung snake_case (phone_number).
> Phai map thu cong trong service layer.

---

## 13. React Router DOM - Dieu huong

```typescript
import { BrowserRouter, Routes, Route, Navigate, useNavigate, Link } from 'react-router-dom'

// Cau hinh routes
<BrowserRouter>
    <Routes>
        <Route path='/login' element={<LoginPage />} />
        <Route path='/dashboard' element={<DashboardPage />} />
        <Route path='/' element={<Navigate to='/login' replace />} />
        <Route path='*' element={<Navigate to='/login' replace />} />
    </Routes>
</BrowserRouter>

// Dieu huong bang code
const navigate = useNavigate()
navigate('/change-password')
navigate('/dashboard', { replace: true })  // khong luu vao history

// Dieu huong bang link
<Link to='/login'>Quay lai dang nhap</Link>
```

---

## 14. TypeScript Types - Kieu du lieu

```typescript
// type - dung cho object don gian
type LoginFormData = {
    phoneNumber: string
    password: string
}

// Optional field
type UserProfile = {
    id: number
    name: string
    avatar?: string   // ? -> khong bat buoc
}

// interface - tuong tu type
interface LoginResponse {
    access_token: string
    token_type: string
    must_change_password: boolean
}

// Trong du an nay:
// frontend/src/features/auth/login/types/loginTypes.ts
export type LoginFormData = { phoneNumber: string; password: string }
export type LoginResponse = { access_token: string; token_type: string; must_change_password: boolean }

// frontend/src/features/auth/change_password/types/changePasswordTypes.ts
export type ChangePasswordFormData = { newPassword: string; confirmNewPassword: string }
export type ChangePasswordResponse = { message: string }
```

---

## 15. import.meta.env - Bien moi truong Vite

**La gi?** Cach doc bien moi truong trong du an Vite. Tuong tu os.getenv() cua Python.

```typescript
// File .env - ten bien PHAI bat dau bang VITE_
// VITE_API_URL=http://localhost:8000

const apiUrl = import.meta.env.VITE_API_URL

// frontend/src/config/config.ts
export const env = { API_URL: import.meta.env.VITE_API_URL }
```

> Bien khong bat dau bang VITE_ se khong duoc dua vao bundle (bao mat).

---
---

## KIEN TRUC

---

## 16. Luong du lieu end-to-end

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

## 17. Quy tac dat ten & Status Code

### HTTP Status Codes

| Constant | So | Y nghia | Khi nao dung |
|---|---|---|---|
| HTTP_200_OK | 200 | Thanh cong | Mac dinh FastAPI tu tra |
| HTTP_400_BAD_REQUEST | 400 | Du lieu sai | SDT sai, mat khau trong |
| HTTP_401_UNAUTHORIZED | 401 | Chua xac thuc | Sai mat khau, token loi |
| HTTP_403_FORBIDDEN | 403 | Khong co quyen | Da login nhung thieu quyen |
| HTTP_404_NOT_FOUND | 404 | Khong tim thay | User khong ton tai |

### Quy tac dat ten

| Vi tri | Quy tac | Vi du |
|---|---|---|
| Python (backend) | snake_case | phone_number, hashed_password |
| TypeScript (frontend) | camelCase | phoneNumber, hashedPassword |
| Class Python | PascalCase | LoginService, UserRole |
| Component React | PascalCase | LoginForm, ChangePasswordForm |
| File Python | snake_case | login_service.py |
| File TypeScript | camelCase / PascalCase | loginService.ts, LoginForm.tsx |

### Import chuan - KHONG dung magic number

```python
# DUNG
from fastapi import status
raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, ...)

# SAI
raise HTTPException(status_code=400, ...)
```

### Depends - KHONG goi ham trong Depends

```python
# DUNG - truyen ten ham
user_id: int = Depends(get_current_user_id)

# SAI - truyen ket qua goi ham
user_id: int = Depends(get_current_user_id())
```

---

*Tai lieu duoc cap nhat: 2026-08-29 - Toan bo kien thuc tu luong Login & Change Password*