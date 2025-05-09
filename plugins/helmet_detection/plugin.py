"""
Helmet Detection Plugin - Simulates helmet detection from video frames.

Author: ItsOji Team
"""

import random
import time
from datetime import datetime
from plugins.base_plugin import BasePlugin
from core.log_manager import LogManager

class Plugin(BasePlugin):
    """Helmet Detection Plugin."""

    def __init__(self):
        super().__init__()
        self.model = None
        self.plugin_name = "helmet_detection"
        self.logger = LogManager()

    def load_model(self):
        print("[HelmetDetectionPlugin] Model loaded (simulated).")
        self.model = True

    def process(self, frame, camera_id=None):
        """
        Process the frame and simulate helmet detection.
        :param frame: Input video frame (BGR format)
        :param camera_id: Optional camera ID for metadata
        :return: Detection result dictionary
        """
        helmet_detected = random.choice([True, False])
        confidence = round(random.uniform(0.80, 0.99), 2)
        timestamp_ms = int(time.time() * 1000)

        result = {
            "helmet_detected": helmet_detected,
            "confidence": confidence,
            "camera_id": camera_id,
            "timestamp_ms": timestamp_ms
        }

        # Log via LogManager (meta-aware, smart)
        self.logger.log(self.plugin_name, result)

        return result

    def release(self):
        self.model = None
        print("[HelmetDetectionPlugin] Model released.")
