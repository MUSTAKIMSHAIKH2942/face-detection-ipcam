# test_face_plugin.py (temporary)
import cv2
import numpy as np
from plugins.face_recognition.plugin import Plugin

if __name__ == "__main__":
    face_plugin = Plugin()
    face_plugin.load_model()

    # Create dummy frame (blank image)
    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)

    for _ in range(5):
        result = face_plugin.process(dummy_frame)
        print("Detection Result:", result)

    face_plugin.release()
