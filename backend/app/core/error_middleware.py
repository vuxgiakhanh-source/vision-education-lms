from fastapi.responses import JSONResponse

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
            await JSONResponse(status_code=500, content={"detail": "Đã xảy ra lỗi máy chủ."})(scope, receive, send)
