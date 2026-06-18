from app.config import settings


class PostureDetector:
    @staticmethod
    def classify(angle: float) -> str:
        if angle <= settings.POSTURE_ANGLE_THRESHOLD_GOOD:
            return "good"
        elif angle <= settings.POSTURE_ANGLE_THRESHOLD_WARNING:
            return "warning"
        else:
            return "poor"

    @staticmethod
    def get_intensity(angle: float) -> float:
        if angle <= settings.POSTURE_ANGLE_THRESHOLD_GOOD:
            return 0.0
        elif angle <= settings.POSTURE_ANGLE_THRESHOLD_WARNING:
            return 0.3
        else:
            return min((angle - settings.POSTURE_ANGLE_THRESHOLD_WARNING) / 25.0, 1.0)
