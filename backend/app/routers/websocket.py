import asyncio
import json
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.auth.jwt import verify_token
from app.config import settings
from app.sensor.factory import get_sensor, get_motor
from app.sensor.posture_detector import PostureDetector

router = APIRouter(tags=["websocket"])


class ConnectionManager:
    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active:
            self.active.remove(websocket)

    async def send_json(self, websocket: WebSocket, data: dict) -> None:
        await websocket.send_json(data)


manager = ConnectionManager()
sensor = None
motor = None
flex_sensor = None


def get_sensor_instance():
    global sensor
    if sensor is None:
        sensor = get_sensor()
    return sensor


def get_motor_instance():
    global motor
    if motor is None:
        motor = get_motor()
    return motor


def get_flex_sensor_instance():
    global flex_sensor
    if flex_sensor is None:
        try:
            from app.sensor.flex_sensor import FlexSensor
            flex_sensor = FlexSensor(bus_num=settings.I2C_BUS, address=0x48)
        except Exception:
            flex_sensor = None
    return flex_sensor


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001, reason="Missing token")
        return

    payload = verify_token(token)
    if payload is None:
        await websocket.close(code=4001, reason="Invalid token")
        return

    await manager.connect(websocket)
    sens = get_sensor_instance()
    mot = get_motor_instance()
    flex = get_flex_sensor_instance()

    sample_interval = 1.0 / settings.SENSOR_SAMPLE_RATE

    try:
        while True:
            try:
                msg = await asyncio.wait_for(websocket.receive_text(), timeout=0.01)
                command = json.loads(msg)
                cmd_type = command.get("type")

                if cmd_type == "recalibrate":
                    if hasattr(sens, "recalibrate"):
                        sens.recalibrate()
                    if flex and hasattr(flex, "recalibrate"):
                        flex.recalibrate()
                    await manager.send_json(websocket, {"type": "recalibrated"})

            except asyncio.TimeoutError:
                pass

            accel = await sens.read_accel()
            gyro = await sens.read_gyro()
            temp = await sens.read_temperature()
            angle = await sens.get_posture_angle()
            status = PostureDetector.classify(angle)

            # Read flex sensor data if available
            flex_data = None
            if flex:
                try:
                    flex_raw = await flex.read_raw_data()
                    flex_data = flex_raw
                except Exception:
                    flex_data = None

            if status == "poor":
                intensity = PostureDetector.get_intensity(angle)
                await mot.alert_feedback(intensity)
            elif status == "warning":
                await mot.correct_posture(angle)

            data = {
                "angle": angle,
                "status": status,
                "accel": {"x": accel[0], "y": accel[1], "z": accel[2]},
                "gyro": {"x": gyro[0], "y": gyro[1], "z": gyro[2]},
                "temperature": temp,
                "flex": flex_data,
                "timestamp": datetime.now().isoformat(),
            }
            await manager.send_json(websocket, data)

            await asyncio.sleep(sample_interval)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)
