from fastapi import APIRouter, Depends, HTTPException, Request

from app.auth.dependencies import get_current_user, require_admin
from app.models.user import UserOut

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("", response_model=list[UserOut])
async def list_users(
    request: Request,
    current_user: dict = Depends(require_admin),
):
    repos = request.app.state.repos
    users = await repos.users.list_all()
    return [
        UserOut(
            id=u.id,
            username=u.username,
            role=u.role,
            location=u.location,
            created_at=u.created_at,
        )
        for u in users
    ]


@router.get("/{user_id}", response_model=UserOut)
async def get_user(
    user_id: int,
    request: Request,
    current_user: dict = Depends(require_admin),
):
    repos = request.app.state.repos
    user = await repos.users.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return UserOut(
        id=user.id,
        username=user.username,
        role=user.role,
        location=user.location,
        created_at=user.created_at,
    )


@router.patch("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: int,
    request: Request,
    current_user: dict = Depends(require_admin),
):
    repos = request.app.state.repos
    body = await request.json()
    user = await repos.users.update(user_id, **body)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return UserOut(
        id=user.id,
        username=user.username,
        role=user.role,
        location=user.location,
        created_at=user.created_at,
    )
