from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.modules.auth.login.router import login_router
from app.modules.auth.change_password.router import change_password_router
from app.modules.auth.me.router import me_router
from app.modules.health.router import health_router
from app.modules.schedule.student.permanent_transfers.router import permanent_transfer_router
from app.modules.schedule.student.upcoming.router import student_upcoming_router
from app.modules.schedule.student.temporary_transfers.router import temporary_transfer_router
from app.modules.schedule.student.weekly.router import weekly_schedule_router
from app.modules.schedule.teacher.router import teacher_schedule_router
from app.modules.sessions.router import teaching_session_router
from app.core.config import settings
from app.core.error_middleware import UnhandledErrorMiddleware

# Production không công khai tài liệu API (/docs, /redoc, /openapi.json).
docs_urls = {"docs_url": None, "redoc_url": None, "openapi_url": None} if settings.is_production else {}
app = FastAPI(**docs_urls)

app.include_router(health_router)
app.include_router(login_router)
app.include_router(change_password_router)
app.include_router(me_router)
app.include_router(student_upcoming_router)
app.include_router(weekly_schedule_router)
app.include_router(temporary_transfer_router)
app.include_router(permanent_transfer_router)
app.include_router(teacher_schedule_router)
app.include_router(teaching_session_router)


# Thứ tự: middleware thêm SAU nằm ở NGOÀI. CORS phải ngoài cùng để phản hồi 500 vẫn có header CORS.
app.add_middleware(UnhandledErrorMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
