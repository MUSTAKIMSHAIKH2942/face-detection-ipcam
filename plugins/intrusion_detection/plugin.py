"""
Intrusion Detection Plugin - Simulates intrusion detection from video frames.

Author: ItsOji Team
"""

import random
import time
from datetime import datetime
from plugins.base_plugin import BasePlugin
from core.log_manager import LogManager

class Plugin(BasePlugin):
    """Intrusion Detection Plugin."""

    def __init__(self):
        super().__init__()
        self.model = None
        self.logger = LogManager()
        self.plugin_name = "intrusion_detection"
        self.last_logged_result = None

    def load_model(self):
        print("[IntrusionDetectionPlugin] Model loaded (simulated).")
        self.model = True

    def process(self, frame, camera_id=None):
        intrusion_detected = random.choice([True, False])
        confidence = round(random.uniform(0.70, 0.95), 2)
        timestamp_ms = int(time.time() * 1000)

        result = {
            "intrusion_detected": intrusion_detected,
            "confidence": confidence,
            "camera_id": camera_id,
            "timestamp_ms": timestamp_ms
        }

        log_cfg = self.logger.get_plugin_config(self.plugin_name)
        if log_cfg:
            trigger_filter = log_cfg.get("log_trigger_filter", "")
            distinct_only = trigger_filter == "distinct_only"

            if not distinct_only or (self.last_logged_result != result):
                log_line = f"{'🚨' if intrusion_detected else '✅'} Intrusion: {intrusion_detected} | Conf: {confidence} | Cam: {camera_id}"
                self.logger.log(self.plugin_name, result)
                self.last_logged_result = result

        return result

    def release(self):
        self.model = None
        print("[IntrusionDetectionPlugin] Model released.")
