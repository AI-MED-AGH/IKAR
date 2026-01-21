from pathlib import Path
from datetime import datetime
import json


class SessionManager:
    description: str
    session_number: int
    session_dir: Path
    base_dir: Path

    def __init__(self, base_dir="data/raw", description=""):
        self.base_dir = Path(base_dir)
        self.description = description
        self.session_number = 0

        self._prepare_session_dir()
        self.create_folders()
        self.meta_data = self._prepare_meta_data()

    @property
    def skeleton_csv_path(self) -> str:
        path = self.session_dir / "skeleton.csv"
        return str(path)

    @property
    def rgb_dir(self) -> str:
        path = self.session_dir / "rgb"
        return str(path)

    @property
    def depth_dir(self) -> str:
        path = self.session_dir / "depth"
        return str(path)

    def finalize(self) -> None:
        meta_path = self.session_dir / "meta.json"
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(self.meta_data, f, indent=4, ensure_ascii=False)

    def create_folders(self) -> None:
        self.session_dir.mkdir(parents=True, exist_ok=True)
        (self.session_dir / "rgb").mkdir(parents=True, exist_ok=True)
        (self.session_dir / "depth").mkdir(parents=True, exist_ok=True)

    def _prepare_session_dir(self) -> None:
        p = Path(self.base_dir)
        folders = [
            int(x.name[-6:])
            for x in p.iterdir()
            if x.is_dir() and x.name.startswith("session_")
        ]

        if len(folders) == 0:
            self.session_number = 1
        else:
            self.session_number = max(folders) + 1

        self.session_dir = self.base_dir / f"session_{self.session_number:06}"

    def _prepare_meta_data(self):
        meta_data = {
            "session_id": f"session_{self.session_number:06}",
            "device": "Kinect v2",
            "library": "pykinect2",
            "fps": 30,
            "joint_count": 25,
            "coordinate_system": "camera_space",
            "units": "meters",
            "start_time": datetime.now().isoformat(),
            "description": self.description,
        }
        return meta_data
