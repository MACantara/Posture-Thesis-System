from fastapi import APIRouter, Depends, Query, Request

from app.auth.dependencies import get_current_user
from app.models.posture import PostureRecordOut, PostureRecordCreate, PostureStatsOut

router = APIRouter(prefix="/api/posture", tags=["posture"])


@router.get("/records", response_model=list[PostureRecordOut])
async def get_records(
    request: Request,
    status: str = Query("all"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
):
    repos = request.app.state.repos
    records = await repos.posture.get_by_user(
        user_id=current_user["user_id"],
        status_filter=status,
        limit=limit,
        offset=offset,
    )
    return [
        PostureRecordOut(
            id=r.id,
            user_id=r.user_id,
            session_id=r.session_id,
            timestamp=r.timestamp,
            status=r.status,
            angle=r.angle,
            duration=r.duration,
            notes=r.notes,
        )
        for r in records
    ]


@router.get("/stats", response_model=PostureStatsOut)
async def get_stats(
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    repos = request.app.state.repos
    stats = await repos.posture.get_stats(current_user["user_id"])
    return PostureStatsOut(
        total_sessions=stats.total_sessions,
        good_posture_count=stats.good_posture_count,
        average_angle=stats.average_angle,
        improvement_rate=stats.improvement_rate,
    )


@router.post("/records", response_model=PostureRecordOut, status_code=201)
async def create_record(
    request: Request,
    record: PostureRecordCreate,
    current_user: dict = Depends(get_current_user),
):
    repos = request.app.state.repos
    r = await repos.posture.insert(
        user_id=current_user["user_id"],
        status=record.status,
        angle=record.angle,
        duration=record.duration,
        session_id=record.session_id,
        notes=record.notes,
    )
    return PostureRecordOut(
        id=r.id,
        user_id=r.user_id,
        session_id=r.session_id,
        timestamp=r.timestamp,
        status=r.status,
        angle=r.angle,
        duration=r.duration,
        notes=r.notes,
    )
