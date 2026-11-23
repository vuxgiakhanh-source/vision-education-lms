from fastapi import APIRouter, Depends

from app.core.dependencies import require_teacher_access

from .upcoming.router import teacher_upcoming_router
from .weekly.router import weekly_router


teacher_schedule_router = APIRouter(prefix="/teacher", dependencies=[Depends(require_teacher_access)])
teacher_schedule_router.include_router(weekly_router)
teacher_schedule_router.include_router(teacher_upcoming_router)
