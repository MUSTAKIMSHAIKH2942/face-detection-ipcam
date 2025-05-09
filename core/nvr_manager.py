# core/nvr_manager.py

"""
NVR Manager - Prepares for multi-channel NVR/DVR integration via IP or RTSP.

Author: ItsOji Team
"""

import json
import os

SUPPORTED_PATTERNS = {
    "hikvision": "rtsp://{ip}/Streaming/Channels/{channel}01",
    "dahua": "rtsp://{ip}/cam/realmonitor?channel={channel}&subtype=0",
    "uniview": "rtsp://{ip}/media/video{channel}/stream1"
}

class NVRManager:
    def __init__(self, nvr_config=None):
        """
        Initialize with optional NVR config dictionary.
        Each config could contain:
          - nvr_ip
          - username
          - password
          - channel_count
          - brand
        """
        self.nvr_config = nvr_config or {}
        self.channels = {}
        self.pattern = SUPPORTED_PATTERNS.get(self.nvr_config.get("brand", "hikvision").lower())

    def connect_to_nvr(self):
        """
        Simulate NVR connection.
        Future: Replace with ONVIF or RTSP pull for real-world NVRs.
        """
        print("[NVRManager] Connecting to NVR...")
        # Simulated connection success
        return True

    def list_available_channels(self):
        """
        List simulated channels from config.
        """
        if not self.nvr_config:
            print("[NVRManager] No NVR config available.")
            return []

        count = self.nvr_config.get("channel_count", 4)
        return [f"Channel {i+1}" for i in range(count)]

    def get_channel_stream_url(self, channel_index):
        """
        Construct RTSP stream URL for the channel using the known brand pattern.
        """
        ip = self.nvr_config.get("nvr_ip", "192.168.1.100")
        if not self.pattern:
            print("[NVRManager] ⚠️ Unsupported brand, using fallback pattern.")
            return f"rtsp://{ip}/channel/{channel_index}"

        return self.pattern.format(ip=ip, channel=channel_index)

    def inject_into_config(self, config_path="config/default_settings.json"):
        """
        Generate stream URLs and inject them into the config file.
        """
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config not found: {config_path}")

        links = [self.get_channel_stream_url(i+1) for i in range(self.nvr_config.get("channel_count", 4))]

        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        config["camera_sources"] = links
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)

        print(f"[NVRManager] Injected {len(links)} streams into config for brand: {self.nvr_config.get('brand', 'hikvision')}")

    def simulate_fetch_frame(self, channel_index):
        """
        Placeholder to simulate getting a frame.
        """
        print(f"[NVRManager] Fetching frame from Channel {channel_index}...")
        return None  # Can be extended with OpenCV frame

# Example usage
if __name__ == "__main__":
    config = {
        "nvr_ip": "192.168.1.64",
        "channel_count": 4,
        "brand": "hikvision"
    }
    manager = NVRManager(config)
    manager.inject_into_config()
