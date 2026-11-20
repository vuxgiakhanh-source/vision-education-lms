import sys
from pathlib import Path
from traceback import walk_tb
from loguru import logger

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logger.remove()
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:HH:mm:ss DD-MM-YYYY HH}</green> | <level>{level: <8}</level> | <cyan>{name}:{line}</cyan> | <level>{message}</level>",
    level="INFO",
    diagnose=False,
)
logger.add(
    LOG_DIR / "app.log",
    format="{time:HH:mm:ss DD-MM-YYYY HH} | {level: <8} | {name}:{line} | {message}",
    level="INFO",
    rotation="10 MB",
    retention="10 days",
    compression="zip",
    encoding="utf-8",
    diagnose=False,
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
)


def log_unhandled_request(method: str, route: str, error: Exception) -> None:
    locations = " -> ".join(
        f"{Path(frame.f_code.co_filename).name}:{line}"
        for frame, line in walk_tb(error.__traceback__)
    )
    logger.error("Unhandled {} on {} {} [{}]", type(error).__name__, method, route, locations)


