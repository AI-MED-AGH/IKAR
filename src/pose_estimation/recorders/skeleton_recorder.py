import csv

class SkeletonRecorder:

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.file = open(self.filepath, mode='w', newline='', encoding='utf-8')
        self.writer = csv.DictWriter(
            self.file,
            fieldnames=["frame_id", "timestamp_ms", "person_id", "joint_name", "x", "y", "z", "tracking_state"]
        )
        self.writer.writeheader()


    def write_rows(self, rows: list[dict]):
        for row in rows:
            self.writer.writerow(row)
        self.file.flush()

    def close(self):
        self.file.close()
