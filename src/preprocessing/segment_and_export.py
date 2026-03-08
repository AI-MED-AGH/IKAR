import numpy as np
import pandas as pd
from pathlib import Path

from pose_estimation.skeleton_format import JOINTS

"""
Adjustable parameters
"""
WINDOW_SIZE = 30
OVERLAP = 10
STEP =  WINDOW_SIZE - OVERLAP

INPUT_PATH = Path("/data/raw/")
OUTPUT_PATH = Path("data/processed")

J = JOINTS
C = 3

def convert_to_skeleton_tensor(df: pd.DataFrame) -> np.ndarray:
    """
    Convert skeleton dataframe into tensor of shape (T, J, C)

    Parameters
    -------
    df : pd.DataFrame

    Returns
    -------
    np.ndarray
        Skeleton tensor (T, J, C)
    """
    frames = df["frame_id"].unique()
    joint_names = df["joint_name"].unique()

    T = len(frames)

    # Empty? Zeros?
    tensor = np.zeros((T, J, C), dtype=np.float32)

    # Czy beda one kolejno i nie bedzie ubytkow? (typu 1, 2, 3, 4, [przerwa] , 8, 9)
    # Zabezpieczenie w postaci slownika dla frame_index
    # Warto moze jakis slownik dla joint_name?
    frame_index = {frame_id: index for index, frame_id in enumerate(frames)}
    joint_index = {joint_name: index for index, joint_name in enumerate(joint_names)}

    for row in df.itertuples(index=False):
        t = frame_index[row.frame_id]
        j = joint_index[row.joint_name]

        tensor[t, j, 0] = row.x
        tensor[t, j, 1] = row.y
        tensor[t, j, 2] = row.z

    return tensor

def load_skeleton_tensor(input_path: Path) -> np.ndarray:
    """
    Read CSV file -> convert to (T, J, C)

    Parameters
    -------
    input_path : Path
        Location of input data

    Returns
    -------
    np.ndarray
        Skeleton tensor (T, J, C)
    """

    df = pd.read_csv(input_path)
    tensor = convert_to_skeleton_tensor(df)

    return tensor

def segment_skeleton_tensor(data: np.ndarray) -> np.ndarray:
    """
    Convert skeleton tensor into fixed-length temporal segments

    Parameters
    -------
    data : np.ndarray
        Skeleton tensor of shape (T, J, C)

    Returns
    -------
    np.ndarray
        Segmented data of shape (n_segments, WINDOW_SIZE, J, C)
    """

    # Zabezpieczenie
    assert STEP > 0, "STEP must be > 0"

    segments = []
    T = data.shape[0]

    if T < WINDOW_SIZE:
        return np.empty((0, WINDOW_SIZE, *data.shape[1:]), dtype=data.dtype)

    for left_idx in range(0,  T - WINDOW_SIZE + 1, STEP):
        right_idx = left_idx + WINDOW_SIZE
        segments.append(data[left_idx:right_idx])

    return np.stack(segments, axis=0)

def export_segmented_data(
        data: np.ndarray,
        split: str,
        label: str
) -> None:
    """
    Export segmented skeleton data to .npy files

    Directory structure:
    data/processed/
        ├── train/
        │   └── fall/
        │       ├── sample_0001.npy
        │       └── sample_0002.npy
        │    └── no_fall/
        │       ├── sample_0001.npy
        │       └── sample_0002.npy
        └── test/
            └── fall/
                ├── sample_0001.npy
                └── sample_0002.npy
            └── no_fall/
               ├── sample_0001.npy
               └── sample_0002.npy

    Parameters
    -------
    data : np.ndarray
        Skeleton tensor of shape (T, J, C)
    split : str
        Dataset split  ("train" or "test")
    label : str
        Class label ("fall" or "no_fall")

    Returns
    -------
    None
    """

    # Zabezpieczenie
    assert split in ["train", "test"], "Expected split to be either train or test"
    assert label in ["fall", "no_fall"], "Expected label to be either fall or nofall"

    segments = segment_skeleton_tensor(data)

    output_dir = Path(OUTPUT_PATH) / split / label
    output_dir.mkdir(parents=True, exist_ok=True)

    existing_files_count = sum(1 for _ in output_dir.glob("*.npy"))

    for i, segment in enumerate(segments, start=1):
        sample_index = existing_files_count + i

        filename = f"sample_{sample_index:04d}.npy"
        full_path = output_dir / filename

        np.save(full_path, segment)

def process_recording(
    input_path: Path,
    split: str,
    label: str
) -> None:
    """
    Process a single skeleton recording

    Parameters
    -------
    input_path : Path
        Location of input data
    split : str
        Dataset split  ("train" or "test")
    label : str
        Class label ("fall" or "no_fall")

    Returns
    -------
    None
    """

    tensor = load_skeleton_tensor(input_path)

    export_segmented_data(
        data=tensor,
        split=split,
        label=label
    )


def main():
    """
    Example usage
    """

    # recordings = [
    #     ("sample_01.csv", "train", "fall"),
    #     ("sample_02.csv", "test", "fall"),
    #     ("sample_01.csv", "train", "no_fall"),
    #     ("sample_02.csv", "test", "no_fall"),
    # ]
    #
    # for filename, split, label in recordings:
    #
    #     input_path = INPUT_PATH / filename
    #
    #     process_recording(
    #         input_path=input_path,
    #         split=split,
    #         label=label
    #     )


if __name__ == "__main__":
    main()
