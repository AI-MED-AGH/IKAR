from pykinect2 import PyKinectV2
from pykinect2 import PyKinectRuntime


class KinectManager:

    def __init__(self, enable_color=False, enable_depth=False):
        sources = PyKinectV2.FrameSourceTypes_Body

        if enable_color:
            sources |= PyKinectV2.FrameSourceTypes_Color

        if enable_depth:
            sources |= PyKinectV2.FrameSourceTypes_Depth

        self.kinect = PyKinectRuntime.PyKinectRuntime(sources)

    def get_body_frame(self):
        if not self.kinect.has_new_body_frame():
            return None
        return self.kinect.get_last_body_frame()

    def get_color_frame(self):
        if not self.kinect.has_new_color_frame():
            return None
        return self.kinect.get_last_color_frame()

    def get_depth_frame(self):
        if not self.kinect.has_new_depth_frame():
            return None
        return self.kinect.get_last_depth_frame()

    def close(self):
        self.kinect.close()
