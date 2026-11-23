from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.modules.auth.login.router import login_router
from app.modules.auth.change_password.router import change_password_router
from app.modules.auth.me.router import me_router
from app.modules.schedule.student.permanent_transfers.router import permanent_transfer_router
from app.modules.schedule.student.upcoming.router import student_upcoming_router
from app.modules.schedule.student.temporary_transfers.router import temporary_transfer_router
from app.modules.schedule.student.weekly.router import weekly_schedule_router
from app.modules.schedule.teacher.router import teacher_schedule_router
from app.modules.sessions.router import teaching_session_router
from app.core.config import settings
from app.core.logger import log_unhandled_request

app = FastAPI()

app.include_router(login_router)
app.include_router(change_password_router)
app.include_router(me_router)
app.include_router(student_upcoming_router)
app.include_router(weekly_schedule_router)
app.include_router(temporary_transfer_router)
app.include_router(permanent_transfer_router)
app.include_router(teacher_schedule_router)
app.include_router(teaching_session_router)


@app.middleware("http")
async def handle_unexpected_error(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as exc:
        route = getattr(request.scope.get("route"), "path", "<unmatched>")
        log_unhandled_request(request.method, route, exc)
        return JSONResponse(status_code=500, content={"detail": "Đã xảy ra lỗi máy chủ."})


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
