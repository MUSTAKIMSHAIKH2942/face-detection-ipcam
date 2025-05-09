# scripts/nvr_test.py

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import json
from core.nvr_manager import NVRManager
from core.crash_logger import log_exception

def test_nvr_connection(nvr_config):
    try:
        nvr = NVRManager(nvr_config)
        if nvr.connect_to_nvr():
            print(f"[NVR Test ✅] Connected to NVR at {nvr_config['nvr_ip']}")
            return True
        else:
            print(f"[NVR Test ❌] Failed to connect to NVR at {nvr_config['nvr_ip']}")
            return False
    except Exception as e:
        log_exception(e, context="CLI NVR Test Failure")
        print(f"[NVR Test ❌] Exception: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/nvr_test.py path/to/nvr_config.json")
        sys.exit(1)

    config_file = sys.argv[1]
    try:
        with open(config_file, 'r') as f:
            data = json.load(f)
            nvr_config = data.get("nvr_settings", {})
            test_nvr_connection(nvr_config)
    except Exception as e:
        print(f"[NVR Test ❌] Failed to load config: {e}")
