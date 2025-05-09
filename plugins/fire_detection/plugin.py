"""
Fire Detection Plugin - Simulates fire detection from video frames.

Author: ItsOji Team
"""

import random
import time
import hashlib
from datetime import datetime
from plugins.base_plugin import BasePlugin
from core.log_manager import LogManager

class Plugin(BasePlugin):
    """Fire Detection Plugin (Enterprise-Ready)"""

    def __init__(self):
        super().__init__()
        self.model = None
        self.logger = LogManager()
        self.plugin_name = "fire_detection"
        self.last_logged_hash = None
        self.model_path = "models/fire_detection.onnx"  # Optional if used in Phase 2.2

    def load_model(self):
        try:
            # ✅ Phase 2.2 Ready — placeholder for ONNX loading
            self.model = "SIMULATED_MODEL"
            print(f"[{self.plugin_name}] ✅ Model loaded (simulated).")
        except Exception as e:
            print(f"[{self.plugin_name}] ❌ Model load failed: {e}")
            self.model = None

    def process(self, frame, camera_id=None):
        # Simulated inference result
        fire_detected = random.choice([True, False])
        confidence = round(random.uniform(0.75, 0.98), 2)
        timestamp_ms = int(time.time() * 1000)

        result = {
            "fire_detected": fire_detected,
            "confidence": confidence,
            "camera_id": camera_id,
            "timestamp_ms": timestamp_ms
        }

        # 🔐 Plugin log config (Phase 1)
        log_cfg = self.logger.get_plugin_config(self.plugin_name)
        if log_cfg:
            trigger_filter = log_cfg.get("log_trigger_filter", "")
            distinct_only = trigger_filter == "distinct_only"

            # ✅ Better comparison via hash
            result_hash = self._hash_result(result)
            if not distinct_only or (self.last_logged_hash != result_hash):
                self.logger.log(self.plugin_name, result)
                self.last_logged_hash = result_hash
        else:
            print(f"[{self.plugin_name}] ⚠️ Missing plugin config.")

        return result

    def _hash_result(self, result_dict):
        """Create a stable hash to detect unique results."""
        base_str = f"{result_dict['fire_detected']}_{result_dict['confidence']}_{result_dict['camera_id']}"
        return hashlib.sha256(base_str.encode()).hexdigest()

    def release(self):
        self.model = None
        print(f"[{self.plugin_name}] 🧹 Model released.")
