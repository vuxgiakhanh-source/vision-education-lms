from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError
from sqlalchemy.exc import TimeoutError as SQLAlchemyTimeoutError

from app.core.logger import log_unhandled_request


class UnhandledErrorMiddleware:
    """Bắt lỗi chưa xử lý, ghi log rồi trả 500 JSON.

    Viết thuần ASGI thay cho @app.middleware("http") (BaseHTTPMiddleware): đo trong tiến trình cho thấy
    bản cũ tốn thêm khoảng 165 us mỗi request (558 so với 393 us), vì mỗi request bị bọc thêm một lớp
    stream và một task. HTTPException không đi qua đây, FastAPI đã xử lý ở tầng trong.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        response_started = False

        async def tracking_send(message):
            nonlocal response_started
            if message["type"] == "http.response.start":
                response_started = True
            await send(message)

        try:
            await self.app(scope, receive, tracking_send)
        except Exception as exc:
            route = getattr(scope.get("route"), "path", "<unmatched>")
            log_unhandled_request(scope["method"], route, exc)
            if response_started:
                # Đã gửi một phần phản hồi thì không thể đổi thành 500, để kết nối bị ngắt.
                raise
            if _is_overload(exc):
                # Quá tải tạm thời (hết kết nối trong pool, MySQL từ chối kết nối): báo thử lại thay vì 500 để
                # giao diện hiểu đây không phải lỗi mã và tự thử lại có độ trễ ngẫu nhiên.
                await JSONResponse(
                    status_code=503,
                    content={"detail": "Hệ thống đang đông, vui lòng thử lại sau vài giây."},
                    headers={"Retry-After": str(RETRY_AFTER_SECONDS)},
                )(scope, receive, send)
                return
            await JSONResponse(status_code=500, content={"detail": "Đã xảy ra lỗi máy chủ."})(scope, receive, send)


RETRY_AFTER_SECONDS = 2
# 1040 quá nhiều kết nối, 2003 không kết nối được, 2006 máy chủ ngắt kết nối, 2013 mất kết nối khi truy vấn.
_TRANSIENT_MYSQL_ERRORS = {1040, 2003, 2006, 2013}


def _is_overload(exc: BaseException) -> bool:
    if isinstance(exc, SQLAlchemyTimeoutError):
        return True
    if isinstance(exc, OperationalError):
        args = getattr(exc.orig, "args", ())
        return bool(args) and args[0] in _TRANSIENT_MYSQL_ERRORS
    return False
