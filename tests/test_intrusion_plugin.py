# test_intrusion_plugin.py (temporary)
import cv2
import numpy as np
from plugins.intrusion_detection.plugin import Plugin

if __name__ == "__main__":
    intrusion_plugin = Plugin()
    intrusion_plugin.load_model()

    # Create dummy frame (blank image)
    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)

    for _ in range(5):
        result = intrusion_plugin.process(dummy_frame)
        print("Detection Result:", result)

    intrusion_plugin.release()
