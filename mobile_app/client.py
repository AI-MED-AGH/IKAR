import requests
from datetime import datetime

URL = f"http://127.0.0.1:8000/trigger-alert"


timestamp = datetime.now().isoformat()

data = {
    "device_id": "2",
    "timestamp": timestamp,
    "data": {
        "event": "fall detected",
        "confidence": 0.99
    }
}

try:
    response = requests.post(URL, json=data)
    response.raise_for_status()
    print("Status:", response.status_code)
    print("Server response:", response.json())

except Exception as e:
    print(f"Wystąpił błąd: {e}")