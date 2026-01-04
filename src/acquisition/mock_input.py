
import numpy as np

def generate_fake_sequence(frames=60, joints=25, fall=False):
    data = np.random.randn(frames, joints, 3)
    if fall:
        data[:,:,1] -= np.linspace(0,2,frames)[:,None]
    return data
