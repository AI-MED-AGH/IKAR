from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()




class EventData(BaseModel):
    event: str
    confidence: float


class DeviceEvent(BaseModel):
    device_id: str
    timestamp: datetime
    data: EventData




@app.post("/api/device/event")
def receive_device_event(event: DeviceEvent):
    """
    Endpoint receiving data from Raspberry Pi
    """
    print("Received event:")
    print(event)

    return {
        "status": "ok",
        "message": "Event received successfully"
    }