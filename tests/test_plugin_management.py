# tests/test_plugin_management.py

"""
Test Suite for PluginManager — Loads and validates all plugins, applies them on dummy data.

Author: ItsOji Team
"""

import sys
import os
import numpy as np
import cv2

sys.path.append(os.path.abspath("."))

from core.plugin_manager import PluginManager

def test_plugin_loading():
    print("[TEST] 🧩 Initializing Plugin Manager...")
    try:
        pm = PluginManager("plugins")
        pm.load_all_plugins()
        plugins = pm.plugins

        print(f"[TEST] ✅ Plugins loaded: {list(plugins.keys())}")
        assert len(plugins) > 0, "[ERROR] No plugins were loaded."
    except Exception as e:
        print(f"[EXCEPTION] Plugin loading failed: {e}")
        assert False, f"[FAIL] Exception occurred during plugin loading: {e}"

def test_plugin_application():
    print("[TEST] 🧪 Applying plugins to dummy frame...")
    try:
        pm = PluginManager("plugins")
        pm.load_all_plugins()

        dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        results = pm.apply_plugins(frame=dummy_frame, camera_id=0)

        assert isinstance(results, dict), "[ERROR] apply_plugins did not return a dictionary."

        for plugin_name, result in results.items():
            print(f"[RESULT] {plugin_name}: {result}")
            assert isinstance(result, dict), f"[ERROR] Plugin '{plugin_name}' did not return a dictionary."

    except Exception as e:
        print(f"[EXCEPTION] Plugin application failed: {e}")
        assert False, f"[FAIL] Exception occurred during plugin application: {e}"

if __name__ == "__main__":
    print("[TEST SUITE] 🔧 Starting PluginManager tests...\n")
    test_plugin_loading()
    test_plugin_application()
    print("\n[TEST SUITE] ✅ Plugin Manager tests completed successfully.")
