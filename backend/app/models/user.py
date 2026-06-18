from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str


class UserOut(BaseModel):
    id: int
    username: str
    role: str
    location: str | None
    created_at: str


class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "user"
    location: str | None = None
