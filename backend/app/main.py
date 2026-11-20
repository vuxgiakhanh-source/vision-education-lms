from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.modules.auth.login.router import login_router
from app.modules.auth.change_password.router import change_password_router
from app.modules.auth.me.router import me_router
from app.modules.schedule.permanent_transfers.router import permanent_transfer_router
from app.modules.schedule.router import schedule_router
from app.modules.schedule.temporary_transfers.router import temporary_transfer_router
from app.modules.schedule.weekly.router import weekly_schedule_router
from app.core.config import settings
from app.core.logger import log_unhandled_request

app = FastAPI()

app.include_router(login_router)
app.include_router(change_password_router)
app.include_router(me_router)
app.include_router(schedule_router)
app.include_router(weekly_schedule_router)
app.include_router(temporary_transfer_router)
app.include_router(permanent_transfer_router)


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
