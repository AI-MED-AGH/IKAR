import time


class FrameTimer:
    frame_id: int
    start_time: float

    def __init__(self):
        self.frame_id = 0
        self.start_time = 0

    def start(self) -> None:
        self.frame_id = 0
        self.start_time = time.time()

    def next(self) -> tuple[int, int]:
        actual_time: float = time.time()
        timestamp_ms: int = int((actual_time - self.start_time) * 1000)

        frame_id: int = self.frame_id
        self.frame_id += 1

        return frame_id, timestamp_ms
