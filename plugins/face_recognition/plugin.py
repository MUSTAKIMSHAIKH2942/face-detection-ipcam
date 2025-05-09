"""
Face Recognition Plugin - Simulates face recognition from video frames.

Author: ItsOji Team
"""

import random
import time
from datetime import datetime
from plugins.base_plugin import BasePlugin
from core.log_manager import LogManager


class Plugin(BasePlugin):
    """Face Recognition Plugin."""

    def __init__(self):
        super().__init__()
        self.model = None
        self.logger = LogManager()
        self.plugin_name = "face_recognition"
        self.last_logged_result = None
        self.known_faces = ["Person_1", "Person_2", "Person_3"]

    def load_model(self):
        print("[FaceRecognitionPlugin] Model loaded (simulated).")
        self.model = True

    def process(self, frame, camera_id=None):
        recognized = random.choice([True, False])
        if recognized:
            person_name = random.choice(self.known_faces)
            confidence = round(random.uniform(0.85, 0.98), 2)
        else:
            person_name = "Unknown"
            confidence = round(random.uniform(0.50, 0.70), 2)

        timestamp_ms = int(time.time() * 1000)

        result = {
            "face_recognized": recognized,
            "person_name": person_name,
            "confidence": confidence,
            "camera_id": camera_id,
            "timestamp_ms": timestamp_ms
        }

        # Smart logging
        log_cfg = self.logger.get_plugin_config(self.plugin_name)
        if log_cfg:
            trigger_filter = log_cfg.get("log_trigger_filter", "")
            distinct_only = trigger_filter == "distinct_only"

            if not distinct_only or (self.last_logged_result != result):
                self.logger.log(self.plugin_name, result)
                self.last_logged_result = result

        return result

    def release(self):
        self.model = None
        print("[FaceRecognitionPlugin] Model released.")
