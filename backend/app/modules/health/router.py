from fastapi import APIRouter, HTTPException, status
from sqlalchemy import text

from app.core.logger import logger
from app.database.database import DbSession

health_router = APIRouter(tags=["health"])


@health_router.get("/health")
async def liveness():
    """Tiến trình còn sống. Không đụng DB, trả về ngay cả khi pool đang cạn."""
    return {"status": "ok"}


@health_router.get("/health/ready")
def readiness(db: DbSession):
    """Sẵn sàng phục vụ: kiểm tra được một kết nối tới MySQL."""
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        logger.error("Readiness: không truy vấn được DB ({})", type(exc).__name__)
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Database không sẵn sàng") from None
    return {"status": "ready"}
