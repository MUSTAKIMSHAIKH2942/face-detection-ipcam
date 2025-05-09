"""
Fire Detection Plugin - Simulates fire detection from video frames.

Author: ItsOji Team
"""

import random
import time
from datetime import datetime
from plugins.base_plugin import BasePlugin
from core.log_manager import LogManager

class Plugin(BasePlugin):
    """Fire Detection Plugin."""

    def __init__(self):
        super().__init__()
        self.model = None
        self.logger = LogManager()
        self.plugin_name = "fire_detection"
        self.last_logged_result = None

    def load_model(self):
        print("[FireDetectionPlugin] Model loaded (simulated).")
        self.model = True

    def process(self, frame, camera_id=None):
        fire_detected = random.choice([True, False])
        confidence = round(random.uniform(0.75, 0.98), 2)
        timestamp_ms = int(time.time() * 1000)

        result = {
            "fire_detected": fire_detected,
            "confidence": confidence,
            "camera_id": camera_id,
            "timestamp_ms": timestamp_ms
        }

        log_cfg = self.logger.get_plugin_config(self.plugin_name)
        if log_cfg:
            trigger_filter = log_cfg.get("log_trigger_filter", "")
            distinct_only = trigger_filter == "distinct_only"

            if not distinct_only or (self.last_logged_result != result):
                log_line = f"{'🔥' if fire_detected else '✅'} Fire: {fire_detected} | Conf: {confidence} | Cam: {camera_id}"
                self.logger.log(self.plugin_name, result)
                self.last_logged_result = result

        return result

    def release(self):
        self.model = None
        print("[FireDetectionPlugin] Model released.")
