"""
Full System Simulation Test - Camera Feed + Plugin Processing + Alert Generation.

Author: ItsOji Team
"""

import cv2
import numpy as np
import time

from core.camera_manager import CameraManager
from core.plugin_manager import PluginManager
from core.alert_manager import AlertManager

def main():
    # Initialise Managers
    camera_mgr = CameraManager()
    plugin_mgr = PluginManager(plugin_folder="plugins")
    alert_mgr = AlertManager()

    # Simulate a dummy camera source (create a black image)
    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)

    # Load Plugins
    plugin_mgr.load_plugin('helmet_detection')
    plugin_mgr.load_plugin('fire_detection')
    plugin_mgr.load_plugin('intrusion_detection')
    plugin_mgr.load_plugin('face_recognition')

    print("\n[System] Plugins loaded successfully.")
    print("[System] Starting full simulation...\n")

    # Start Simulation
    for frame_id in range(10):  # Simulate 10 frames
        print(f"\n[Frame {frame_id+1}] Processing...")
        results = plugin_mgr.apply_plugins(dummy_frame)

        for plugin_name, result in results.items():
            print(f" - {plugin_name} Detection:", result)

            if plugin_name == "helmet_detection" and not result.get("helmet_detected", True):
                alert_mgr.add_alert(camera_id=0, plugin_name="HelmetDetection", detection_info="Helmet Missing", severity="High")

            if plugin_name == "fire_detection" and result.get("fire_detected", False):
                alert_mgr.add_alert(camera_id=0, plugin_name="FireDetection", detection_info="Fire Detected", severity="Critical")

            if plugin_name == "intrusion_detection" and result.get("intrusion_detected", False):
                alert_mgr.add_alert(camera_id=0, plugin_name="IntrusionDetection", detection_info="Intrusion Detected", severity="High")

            if plugin_name == "face_recognition" and result.get("face_recognized", False) and result.get("person_name", "Unknown") != "Unknown":
                alert_mgr.add_alert(camera_id=0, plugin_name="FaceRecognition", detection_info=f"Known Person: {result['person_name']}", severity="Medium")

        time.sleep(1)  # Small delay to simulate frame rate

    print("\n[System] Simulation Completed.\n")
    print("[Active Alerts Recorded:]")
    for alert in alert_mgr.get_active_alerts():
        print(alert)

if __name__ == "__main__":
    main()
