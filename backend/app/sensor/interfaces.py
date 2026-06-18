from abc import ABC, abstractmethod


class SensorInterface(ABC):
    @abstractmethod
    async def read_accel(self) -> tuple[float, float, float]:
        ...

    @abstractmethod
    async def read_gyro(self) -> tuple[float, float, float]:
        ...

    @abstractmethod
    async def read_temperature(self) -> float:
        ...

    @abstractmethod
    async def get_posture_angle(self) -> float:
        ...


class MotorInterface(ABC):
    @abstractmethod
    async def correct_posture(self, angle: float) -> None:
        ...

    @abstractmethod
    async def alert_feedback(self, intensity: float) -> None:
        ...
