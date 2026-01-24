from pykinect2 import PyKinectV2

JOINT_NAMES = {
    PyKinectV2.JointType_SpineBase: "SpineBase",
    PyKinectV2.JointType_SpineMid: "SpineMid",
    PyKinectV2.JointType_Neck: "Neck",
    PyKinectV2.JointType_Head: "Head",
    PyKinectV2.JointType_ShoulderLeft: "ShoulderLeft",
    PyKinectV2.JointType_ElbowLeft: "ElbowLeft",
    PyKinectV2.JointType_WristLeft: "WristLeft",
    PyKinectV2.JointType_HandLeft: "HandLeft",
    PyKinectV2.JointType_ShoulderRight: "ShoulderRight",
    PyKinectV2.JointType_ElbowRight: "ElbowRight",
    PyKinectV2.JointType_WristRight: "WristRight",
    PyKinectV2.JointType_HandRight: "HandRight",
    PyKinectV2.JointType_HipLeft: "HipLeft",
    PyKinectV2.JointType_KneeLeft: "KneeLeft",
    PyKinectV2.JointType_AnkleLeft: "AnkleLeft",
    PyKinectV2.JointType_FootLeft: "FootLeft",
    PyKinectV2.JointType_HipRight: "HipRight",
    PyKinectV2.JointType_KneeRight: "KneeRight",
    PyKinectV2.JointType_AnkleRight: "AnkleRight",
    PyKinectV2.JointType_FootRight: "FootRight",
    PyKinectV2.JointType_SpineShoulder: "SpineShoulder",
    PyKinectV2.JointType_HandTipLeft: "HandTipLeft",
    PyKinectV2.JointType_ThumbLeft: "ThumbLeft",
    PyKinectV2.JointType_HandTipRight: "HandTipRight",
    PyKinectV2.JointType_ThumbRight: "ThumbRight",
}

TRACKING_STATE_MAP = {
    PyKinectV2.TrackingState_NotTracked: "NotTracked",
    PyKinectV2.TrackingState_Inferred: "Inferred",
    PyKinectV2.TrackingState_Tracked: "Tracked",
}


class BodyTracker:

    def __init__(self):
        self._person_map = {}
        self._next_person_id = 0

    def extract(self, body_frame, frame_id: int, timestamp_ms: int):
        rows = []

        for body in body_frame.bodies:
            if not body.is_tracked:
                continue

            tracking_id = body.tracking_id

            if tracking_id not in self._person_map:
                self._person_map[tracking_id] = self._next_person_id
                self._next_person_id += 1

            person_id = self._person_map[tracking_id]

            for joint_type, joint in body.joints.items():
                pos = joint.Position

                rows.append(
                    {
                        "frame_id": frame_id,
                        "timestamp_ms": timestamp_ms,
                        "person_id": person_id,
                        "joint_name": JOINT_NAMES[joint_type],
                        "x": pos.x,
                        "y": pos.y,
                        "z": pos.z,
                        "tracking_state": TRACKING_STATE_MAP[joint.TrackingState],
                    }
                )

        return rows
