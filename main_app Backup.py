# main_app.py (UPDATED with NVR Support)

import sys
import os
import subprocess
import threading
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from datetime import datetime

from ui.main_window import MainWindow
from ui.dashboard import Dashboard
from ui.live_view import LiveView
from ui.alerts_management import AlertsManagement

from core.camera_manager import CameraManager
from core.plugin_manager import PluginManager
from core.alert_manager import AlertManager
from core.report_manager import ReportManager
from core.crash_logger import log_exception
from industrial.opc_server import OPCUAServer
from core.nvr_manager import NVRManager  # ✅ NVR Manager

class EyeQEnterpriseApp:

    def __init__(self):
        self.app = QApplication(sys.argv)
        self._init_system_monitoring()
        self._setup_industrial_features()

        try:
            with open("ui/styles/main.qss", "r") as f:
                self.app.setStyleSheet(f.read())
                print("[UI] Theme loaded from main.qss")
        except FileNotFoundError:
            print("[UI] Theme file not found. Proceeding with default style.")

        self.camera_manager = CameraManager()
        self.plugin_manager = PluginManager()
        self.alert_manager = AlertManager()
        self.report_manager = ReportManager()

        self.alerts_page = AlertsManagement()
        self.dashboard = Dashboard()
        self.live_view = LiveView()

        self.plugin_manager.load_all_plugins()
        self._setup_all_cameras()  # ✅ Centralized NVR + USB/IP

        self.live_view.set_camera_manager(self.camera_manager)
        self.live_view.set_plugin_manager(self.plugin_manager)
        self.live_view.set_alert_manager(self.alert_manager)
        self.live_view.set_alerts_page(self.alerts_page)

        QTimer.singleShot(1000, self.live_view.refresh_camera_grid)
        self.live_view.refresh_camera_grid()

        self.window = MainWindow()
        self.window.live_view_page = self.live_view
        self.window.dashboard_page = self.dashboard
        self.window.alerts_page = self.alerts_page

        self.window.init_pages()
        self.window.connect_events()

        if hasattr(self.live_view, 'camera_labels'):
            self.window.camera_labels = {
                idx: label for idx, (cam_id, label) in enumerate(self.live_view.camera_labels.items())
            }
            print(f"[MainApp] LiveView camera labels count: {len(self.live_view.camera_labels)}")
            for cam_id, label in self.live_view.camera_labels.items():
                print(f" - {cam_id} label initialized")
        else:
            print("[MainApp] ⚠️ No camera labels found in live_view.")

        self.window.update_status("System Initialized")
        self.window.show()
        QTimer.singleShot(1000, self.safe_show_liveview)

        self.opc_server = OPCUAServer()
        threading.Thread(target=self.opc_server.start, daemon=True).start()

        self.heartbeat_timer = QTimer()
        self.heartbeat_timer.timeout.connect(self.log_heartbeat)
        self.heartbeat_timer.start(600_000)

        self.timer = QTimer()
        self.timer.timeout.connect(self.process_frames)
        self.timer.start(500)

        self.run_log_maintenance()

    def _setup_all_cameras(self):
        self.camera_manager.auto_initialize_all_cameras()

        # ✅ NVR Support Here
        nvr_cfg = {
            "nvr_ip": "192.168.1.201",
            "username": "admin",
            "password": "12345",
            "channel_count": 4
        }
        self.nvr_manager = NVRManager(nvr_config=nvr_cfg)
        if self.nvr_manager.connect_to_nvr():
            for ch in range(nvr_cfg["channel_count"]):
                stream_url = self.nvr_manager.get_channel_stream_url(ch)
                cam_id = f"nvr_{ch}"
                self.camera_manager.add_camera(cam_id, "nvr", stream_url)

    def safe_show_liveview(self):
        try:
            self.window.show_liveview()
        except Exception as e:
            print(f"[MainApp] ⚠️ Failed to show LiveView: {e}")
        self.live_view.refresh_camera_grid()

    def process_frames(self):
        for cam_id in self.camera_manager.cameras:
            frame = self.camera_manager.get_frame(cam_id)
            if frame is None:
                continue
            try:
                plugin_results = self.plugin_manager.apply_plugins(frame, camera_id=cam_id)
                self.alert_manager.handle_plugin_results(cam_id, plugin_results)

                for plugin, result in plugin_results.items():
                    alert = {
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "camera_id": cam_id,
                        "plugin_name": plugin,
                        "detection_info": str(result),
                        "severity": "High"
                    }
                    if self.alerts_page:
                        self.alerts_page.add_alert_entry(alert)
                    if self.dashboard:
                        self.dashboard.add_alert_entry(alert)
            except Exception as e:
                log_exception(
                    e,
                    context="Plugin frame processing failure",
                    extra_info={"camera_id": cam_id}
                )
                if self.window:
                    self.window.update_status(f"⚠️ Plugin crash for Cam {cam_id}")

    def log_heartbeat(self):
        print(f"[Heartbeat] EyeQ System Running OK - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    def run_log_maintenance(self):
        maintenance_script = "scripts/log_maintenance.py"
        if os.path.exists(maintenance_script):
            try:
                subprocess.Popen([sys.executable, maintenance_script])
                print("[MainApp] ✅ Log cleanup script triggered.")
            except Exception as e:
                log_exception(e, context="Failed to run log cleanup script")

    def run(self):
        exit_code = self.app.exec_()
        self.shutdown()
        sys.exit(exit_code)

    def shutdown(self):
        print("[EyeQEnterpriseApp] Shutting down...")
        self.camera_manager.stop_all_cameras()
        self.plugin_manager.unload_all_plugins()

    def _init_system_monitoring(self):
        print("[SystemMonitor] Placeholder: Not yet implemented.")

    def _setup_industrial_features(self):
        print("[Industrial] Placeholder for OPC/Modbus setup.")

if __name__ == "__main__":
    try:
        app = EyeQEnterpriseApp()
        app.run()
    except Exception as e:
        log_exception(
            e,
            context="EyeQ Main Application Crash",
            extra_info={"module": "main_app", "stage": "entry_point"}
        )
