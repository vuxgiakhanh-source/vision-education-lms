import os
import sys
from pathlib import Path
from traceback import walk_tb
from loguru import logger

# Thư mục log cố định theo vị trí code (backend/logs), không theo thư mục đang chạy lệnh.
# Trước đây dùng Path("logs") nên mỗi nơi chạy uvicorn tạo ra một thư mục log riêng.
LOG_DIR = Path(os.getenv("LOG_DIR") or Path(__file__).resolve().parents[2] / "logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

logger.remove()
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:HH:mm:ss DD-MM-YYYY}</green> | <level>{level: <8}</level> | <cyan>{name}:{line}</cyan> | <level>{message}</level>",
    level="INFO",
    diagnose=False,
)
# enqueue=True: mọi tiến trình đẩy log vào một hàng đợi, một luồng duy nhất ghi file.
# Không có nó, nhiều worker cùng xoay vòng và nén một file log sẽ tranh nhau.
logger.add(
    LOG_DIR / "app.log",
    format="{time:HH:mm:ss DD-MM-YYYY} | {level: <8} | {name}:{line} | {message}",
    level="INFO",
    rotation="10 MB",
    retention="10 days",
    compression="zip",
    encoding="utf-8",
    diagnose=False,
    enqueue=True,
)
logger.add(
    LOG_DIR / "error.log",
    format="{time:HH:mm:ss DD-MM-YYYY} | {level: <8} | {name}:{line} | {message}",
    level="ERROR",
    rotation="10 MB",
    retention="30 days",
    compression="zip",
    backtrace=True,
    diagnose=False,
    encoding="utf-8",
    enqueue=True,
)


def log_unhandled_request(method: str, route: str, error: Exception) -> None:
    locations = " -> ".join(
        f"{Path(frame.f_code.co_filename).name}:{line}"
        for frame, line in walk_tb(error.__traceback__)
    )
    logger.error("Unhandled {} on {} {} [{}]", type(error).__name__, method, route, locations)
