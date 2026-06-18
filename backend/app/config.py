import os
from pathlib import Path


class Settings:
    # General — SECRET_KEY is sensitive, must be set via .env or generated
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-to-a-random-secret-key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Database — DATABASE_PATH is sensitive (contains user data location)
    DB_BACKEND: str = os.getenv("DB_BACKEND", "sqlite")
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "posture.db")

    # Sensors — non-sensitive defaults
    USE_MOCK_SENSORS: bool = os.getenv("USE_MOCK_SENSORS", "True").lower() == "true"

    # Hardware Config — non-sensitive pin/bus defaults
    I2C_BUS: int = int(os.getenv("I2C_BUS", "1"))
    MPU6050_ADDRESS: int = int(os.getenv("MPU6050_ADDRESS", "0x68"), 16)
    SERVO_GPIO_PIN: int = int(os.getenv("SERVO_GPIO_PIN", "18"))
    VIBRATOR_GPIO_PIN: int = int(os.getenv("VIBRATOR_GPIO_PIN", "23"))
    SENSOR_SAMPLE_RATE: int = int(os.getenv("SENSOR_SAMPLE_RATE", "10"))
    CALIBRATION_OFFSETS_PATH: str = os.getenv("CALIBRATION_OFFSETS_PATH", "config/calibration.json")

    # Posture Detection Thresholds (degrees from neutral) — non-sensitive
    POSTURE_ANGLE_THRESHOLD_GOOD: float = float(os.getenv("POSTURE_ANGLE_THRESHOLD_GOOD", "10"))
    POSTURE_ANGLE_THRESHOLD_WARNING: float = float(os.getenv("POSTURE_ANGLE_THRESHOLD_WARNING", "20"))

    # Server — non-sensitive defaults
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    WORKERS: int = int(os.getenv("WORKERS", "1"))

    # CORS — non-sensitive defaults
    CORS_ORIGINS: list[str] = os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://localhost:8000"
    ).split(",")

    @property
    def db_path(self) -> Path:
        return Path(self.DATABASE_PATH)


settings = Settings()


def generate_secret_key() -> str:
    """Generate a cryptographically secure secret key for JWT signing."""
    import secrets
    return secrets.token_urlsafe(48)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "generate-secret":
        key = generate_secret_key()
        print("Generated SECRET_KEY:")
        print()
        print(f"  {key}")
        print()
        print("Add this to your .env file:")
        print(f"  SECRET_KEY={key}")
    else:
        print("Usage: python -m app.config generate-secret")
        print("       Generates a cryptographically secure SECRET_KEY for JWT signing.")
