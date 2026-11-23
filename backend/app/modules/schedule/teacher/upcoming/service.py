from app.core import clock
from app.modules.sessions.repository import TeachingSessionRepository
from app.modules.sessions.schemas import TeachingSessionResponse


class TeacherUpcomingSessionService:
    def __init__(self, repository: TeachingSessionRepository):
        self.repository = repository

    def get_upcoming_session(self) -> TeachingSessionResponse | None:
        session = self.repository.get_next_session(clock.center_local_now())
        return TeachingSessionResponse.model_validate(session) if session is not None else None
