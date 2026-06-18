from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    id: int
    username: str
    password_hash: str
    role: str
    location: str | None
    created_at: str


@dataclass
class PostureRecord:
    id: int | None
    user_id: int
    session_id: int | None
    timestamp: str
    status: str
    angle: float
    duration: float | None
    notes: str | None


@dataclass
class PostureStats:
    total_sessions: int
    good_posture_count: int
    average_angle: float
    improvement_rate: float


@dataclass
class Session:
    id: int | None
    user_id: int
    start_time: str
    end_time: str | None
    good_count: int
    warning_count: int
    poor_count: int
    avg_angle: float | None


class UserRepository(ABC):
    @abstractmethod
    async def get_by_username(self, username: str) -> User | None:
        ...

    @abstractmethod
    async def get_by_id(self, user_id: int) -> User | None:
        ...

    @abstractmethod
    async def create(self, username: str, password_hash: str, role: str, location: str | None = None) -> User:
        ...

    @abstractmethod
    async def list_all(self) -> list[User]:
        ...

    @abstractmethod
    async def update(self, user_id: int, **fields) -> User | None:
        ...


class PostureRepository(ABC):
    @abstractmethod
    async def insert(self, user_id: int, status: str, angle: float, duration: float | None = None,
                     session_id: int | None = None, notes: str | None = None) -> PostureRecord:
        ...

    @abstractmethod
    async def get_by_user(self, user_id: int, status_filter: str | None = None,
                          limit: int = 50, offset: int = 0) -> list[PostureRecord]:
        ...

    @abstractmethod
    async def get_stats(self, user_id: int) -> PostureStats:
        ...


class SessionRepository(ABC):
    @abstractmethod
    async def start_session(self, user_id: int) -> int:
        ...

    @abstractmethod
    async def end_session(self, session_id: int, good_count: int = 0,
                          warning_count: int = 0, poor_count: int = 0,
                          avg_angle: float | None = None) -> None:
        ...

    @abstractmethod
    async def get_by_user(self, user_id: int) -> list[Session]:
        ...
