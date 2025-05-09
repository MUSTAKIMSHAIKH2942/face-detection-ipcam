# main_app.py (UPDATED with NVR Support)

import json
import sys
import os
import subprocess
import threading
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from datetime import datetime
from core.system_monitor import SystemMonitor

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
        self.plugin_manager = PluginManager(parent_ui=None)  # ⏳ temp placeholder
        self.alert_manager = AlertManager()
        self.report_manager = ReportManager()

        self.alerts_page = AlertsManagement()
        self.dashboard = Dashboard()

        # ✅ Now safe to inject monitor
        try:
            self.dashboard.set_monitor(self.system_monitor)
            print("[SystemMonitor] ✅ Dashboard monitor linked.")
        except Exception as e:
            log_exception(e, context="System Monitor → Dashboard Injection Failure")

        self.live_view = LiveView()

        self.plugin_manager.load_all_plugins()
        self._setup_all_cameras()

        working_cams = sum(1 for cam in self.camera_manager.cameras.values() if cam.frame is not None)
        live_cams = self.live_view.camera_labels if hasattr(self.live_view, "camera_labels") else {}

        self.dashboard.set_camera_count(len(live_cams))
        self.dashboard.update_cameras_overview(
            self.camera_manager.cameras,
            live_cams
        )

        self.live_view.set_camera_manager(self.camera_manager)
        self.live_view.set_plugin_manager(self.plugin_manager)
        self.live_view.set_alert_manager(self.alert_manager)
        self.live_view.set_alerts_page(self.alerts_page)

        QTimer.singleShot(1000, self.live_view.refresh_camera_grid)
        self.live_view.refresh_camera_grid()

        self.window = MainWindow()
        self.plugin_manager.parent_ui = self.window  # ✅ Now inject parent for popups

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

        # ✅ NVR Support via Config
        try:
            with open("config/default_settings.json", "r") as f:
                config = json.load(f)
            nvr_cfg = config.get("nvr_settings", {})
            self.nvr_manager = NVRManager(nvr_cfg)
            if self.nvr_manager.connect_to_nvr():
                for ch in range(nvr_cfg.get("channel_count", 0)):
                    stream_url = self.nvr_manager.get_channel_stream_url(ch)
                    cam_id = f"nvr_{ch}"
                    self.camera_manager.add_camera(cam_id, "nvr", stream_url)
        except Exception as e:
            log_exception(e, context="NVR camera load failure")


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
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[Heartbeat] EyeQ System Running OK - {timestamp}")

        # ✅ Update dashboard heartbeat label
        if self.dashboard:
            try:
                self.dashboard.update_heartbeat(timestamp)
            except Exception as e:
                log_exception(e, context="Dashboard Heartbeat UI Update Failure")


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
        try:
            self.system_monitor = SystemMonitor(interval=10)
            self.system_monitor.start()
            print("[SystemMonitor] ✅ Monitoring started.")
        except Exception as e:
            log_exception(e, context="SystemMonitor Init Failure")

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
