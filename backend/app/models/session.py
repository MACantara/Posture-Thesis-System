from pydantic import BaseModel


class SessionOut(BaseModel):
    id: int
    user_id: int
    start_time: str
    end_time: str | None
    good_count: int
    warning_count: int
    poor_count: int
    avg_angle: float | None


class SessionStartResponse(BaseModel):
    session_id: int
