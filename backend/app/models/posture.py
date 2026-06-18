from pydantic import BaseModel


class PostureRecordOut(BaseModel):
    id: int
    user_id: int
    session_id: int | None
    timestamp: str
    status: str
    angle: float
    duration: float | None
    notes: str | None


class PostureRecordCreate(BaseModel):
    status: str
    angle: float
    duration: float | None = None
    session_id: int | None = None
    notes: str | None = None


class PostureStatsOut(BaseModel):
    total_sessions: int
    good_posture_count: int
    average_angle: float
    improvement_rate: float
