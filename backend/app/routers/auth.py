from fastapi import APIRouter, Depends, HTTPException, status, Request

from app.auth.dependencies import get_current_user
from app.auth.jwt import create_token
from app.auth.password import verify_password
from app.models.user import LoginRequest, TokenResponse, UserOut

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(request: Request, credentials: LoginRequest):
    repos = request.app.state.repos
    user = await repos.users.get_by_username(credentials.username)
    if user is None or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    token = create_token({
        "user_id": user.id,
        "role": user.role,
        "username": user.username,
    })
    return TokenResponse(
        access_token=token,
        role=user.role,
        username=user.username,
    )


@router.get("/me", response_model=UserOut)
async def get_me(request: Request, current_user: dict = Depends(get_current_user)):
    repos = request.app.state.repos
    user = await repos.users.get_by_id(current_user["user_id"])
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return UserOut(
        id=user.id,
        username=user.username,
        role=user.role,
        location=user.location,
        created_at=user.created_at,
    )
