from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_timeout=settings.db_pool_timeout,
    pool_recycle=settings.db_pool_recycle,
)

SessionLocal = sessionmaker(bind=engine)


def get_session_factory() -> sessionmaker[Session]:
    return SessionLocal


def get_db(
    session_factory: Annotated[sessionmaker[Session], Depends(get_session_factory)],
) -> Iterator[Session]:
    with session_factory() as db:
        yield db


# scope="function". Thứ tự đã đo (FastAPI 0.143):
#   mặc định:       endpoint -> serialize -> gửi byte cuối -> ĐÓNG PHIÊN
#   scope function: endpoint -> serialize -> ĐÓNG PHIÊN -> gửi byte cuối
# Mặc định, học sinh mạng chậm giữ kết nối MySQL (và giao dịch còn mở) suốt lúc byte cuối còn đi.
#
# Trả đối tượng ORM với response_model vẫn an toàn vì serialize xảy ra TRƯỚC khi đóng phiên.
# Cái bẫy thật là mọi thứ chạy SAU khi phiên đã đóng: BackgroundTasks và StreamingResponse.
# Session.close() không làm phiên hỏng, lần dùng sau âm thầm mở kết nối mới và không ai đóng
# (rò rỉ kết nối). Việc chạy nền phải tự mở phiên bằng get_session_factory(), không dùng DbSession.
DbSession = Annotated[Session, Depends(get_db, scope="function")]
