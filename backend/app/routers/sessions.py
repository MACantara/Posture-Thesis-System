from fastapi import APIRouter, Depends, Request

from app.auth.dependencies import get_current_user
from app.models.session import SessionOut, SessionStartResponse

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.get("", response_model=list[SessionOut])
async def list_sessions(
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    repos = request.app.state.repos
    sessions = await repos.sessions.get_by_user(current_user["user_id"])
    return [
        SessionOut(
            id=s.id,
            user_id=s.user_id,
            start_time=s.start_time,
            end_time=s.end_time,
            good_count=s.good_count,
            warning_count=s.warning_count,
            poor_count=s.poor_count,
            avg_angle=s.avg_angle,
        )
        for s in sessions
    ]


@router.post("/start", response_model=SessionStartResponse)
async def start_session(
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    repos = request.app.state.repos
    session_id = await repos.sessions.start_session(current_user["user_id"])
    return SessionStartResponse(session_id=session_id)


@router.post("/{session_id}/end")
async def end_session(
    session_id: int,
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    repos = request.app.state.repos
    await repos.sessions.end_session(session_id)
    return {"status": "ended", "session_id": session_id}
