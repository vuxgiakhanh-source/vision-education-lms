from pydantic import BaseModel, PositiveInt

from ..schemas import SessionTime


class SwapSessionsRequest(BaseModel):
    other_session_id: PositiveInt
    expected_time: SessionTime
    expected_other_time: SessionTime
