# test_helmet_plugin.py (corrected)
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))  # Add project path

import cv2
import numpy as np
from plugins.helmet_detection.plugin import Plugin

if __name__ == "__main__":
    helmet_plugin = Plugin()
    helmet_plugin.load_model()

    # Create dummy frame (blank image)
    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)

    for _ in range(5):
        result = helmet_plugin.process(dummy_frame)
        print("Detection Result:", result)

    helmet_plugin.release()
