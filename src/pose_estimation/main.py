from core.kinect_manager import KinectManager
from core.body_tracker import BodyTracker
from core.frame_timer import FrameTimer
from core.session_manager import SessionManager
from recorders.skeleton_recorder import SkeletonRecorder
from utils.keyboard import KeyboardListener


def main():
    kinect = KinectManager()
    body_tracker = BodyTracker()
    timer = FrameTimer()
    session = SessionManager()
    recorder = SkeletonRecorder(session.skeleton_csv_path)
    keyboard = KeyboardListener()

    recording = False
    print("Press 'r' to start recording, 'q' to quit")

    try:
        while True:
            key = keyboard.poll()
            if key == "r" and not recording:
                print("Recording started")
                recording = True
                timer.start()

            if key == "q":
                print("Stopping")
                break

            if not recording:
                continue

            body_frame = kinect.get_body_frame()
            if body_frame is None:
                continue

            frame_id, timestamp_ms = timer.next()

            skeleton_rows = body_tracker.extract(
                body_frame=body_frame, frame_id=frame_id, timestamp_ms=timestamp_ms
            )

            recorder.write_rows(skeleton_rows)

    except KeyboardInterrupt:
        print("Interrupted by user")

    finally:
        recorder.close()
        kinect.close()
        session.finalize()
        keyboard.stop()
        print("Session closed cleanly")


if __name__ == "__main__":
    main()
