import importlib
import os
import threading
from datetime import datetime
import time
import cv2
from PyQt5.QtWidgets import QMessageBox  # ✅ NEW: for popup alerts
from core.crash_logger import log_exception
from core.log_manager import LogManager
from core.watchdog import (
    report_plugin_result,
    reset_plugin_health,
    get_plugin_status
)
from PyQt5.QtCore import QTimer


class PluginManager:
    def __init__(self, plugin_folder="plugins", parent_ui=None):
        self.plugin_folder = plugin_folder
        self.plugins = {}
        self.plugin_locks = {}
        self.plugin_status = {}
        self.logger = LogManager()
        self.last_process_time = {}
        self.parent_ui = parent_ui  # ✅ Context for UI interaction

    def load_plugin(self, plugin_name):
        try:
            module_path = f"{self.plugin_folder}.{plugin_name}.plugin"
            module = importlib.import_module(module_path)
            plugin_class = getattr(module, "Plugin")
            plugin_instance = plugin_class()
            self.plugins[plugin_name] = plugin_instance
            self.plugin_locks[plugin_name] = threading.Lock()
            self.plugin_status[plugin_name] = True
            print(f"[PluginManager] ✅ Loaded plugin: {plugin_name} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            # ✅ Update dashboard
            if hasattr(self.parent_ui, "update_plugin_status_label"):
                self.parent_ui.update_plugin_status_label(plugin_name, True)

        except Exception as e:
            log_exception(
                e,
                context=f"❌ Error loading plugin: {plugin_name}",
                extra_info={"plugin": plugin_name, "stage": "load_plugin"}
            )

    def attempt_plugin_recovery(self, plugin_name):
        print(f"[PluginManager] ♻️ Retrying plugin: {plugin_name}")
        self.unload_plugin(plugin_name)
        time.sleep(5)
        self.load_plugin(plugin_name)
        reset_plugin_health(plugin_name)
        print(f"[PluginManager] 🔁 Plugin {plugin_name} reloaded and health reset.")

        # ✅ Dashboard hook
        if hasattr(self.parent_ui, "update_plugin_status_label"):
            self.parent_ui.update_plugin_status_label(plugin_name, True)

        # ✅ Safe popup
        def show_popup():
            try:
                if self.parent_ui:
                    QMessageBox.critical(
                        self.parent_ui,
                        "Plugin Auto-Recovered",
                        f"⚠️ Plugin '{plugin_name}' failed 3 times and was auto-recovered successfully."
                    )
            except Exception as e:
                log_exception(e, context=f"❌ Popup failed for plugin: {plugin_name}")

        QTimer.singleShot(0, show_popup)

    def apply_plugins(self, frame, camera_id=None):
        results = {}
        now = time.time()
        if camera_id:
            last = self.last_process_time.get(camera_id, 0)
            if now - last < 1.0:
                return {}
            self.last_process_time[camera_id] = now

        try:
            resized = cv2.resize(frame, (640, 360))
        except Exception:
            resized = frame

        plugin_items = list(self.plugins.items())

        for name, plugin in plugin_items:
            if get_plugin_status(name) == "STALLED":
                try:
                    self.attempt_plugin_recovery(name)
                    continue
                except Exception as e:
                    log_exception(e, context=f"❌ Retry failed for plugin: {name}")
                    continue

            if not self.plugin_status.get(name, False):
                continue

            try:
                with self.plugin_locks[name]:
                    result = plugin.process(resized)
                    results[name] = result

                    if result is None:
                        report_plugin_result(name, False)
                    else:
                        report_plugin_result(name, True)

                    self.logger.log(name, result)
                    print(f"[PluginManager] Applied {name} on Cam {camera_id} at {datetime.now().strftime('%H:%M:%S')}")
            except Exception as e:
                log_exception(
                    e,
                    context=f"⚠️ Plugin '{name}' failed on camera {camera_id}",
                    extra_info={"plugin": name, "camera_id": camera_id}
                )
                report_plugin_result(name, False)

        return results

    def unload_plugin(self, plugin_name):
        if plugin_name in self.plugins:
            del self.plugins[plugin_name]
            self.plugin_locks.pop(plugin_name, None)
            self.plugin_status.pop(plugin_name, None)
            print(f"[PluginManager] 🔄 Unloaded plugin: {plugin_name}")

            # ✅ Update dashboard
            if hasattr(self.parent_ui, "update_plugin_status_label"):
                self.parent_ui.update_plugin_status_label(plugin_name, False)

    def enable_plugin(self, plugin_name):
        if plugin_name in self.plugin_status:
            self.plugin_status[plugin_name] = True
            print(f"[PluginManager] ✅ Enabled plugin: {plugin_name}")
            if hasattr(self.parent_ui, "update_plugin_status_label"):
                self.parent_ui.update_plugin_status_label(plugin_name, True)

    def disable_plugin(self, plugin_name):
        if plugin_name in self.plugin_status:
            self.plugin_status[plugin_name] = False
            print(f"[PluginManager] 🚫 Disabled plugin: {plugin_name}")
            if hasattr(self.parent_ui, "update_plugin_status_label"):
                self.parent_ui.update_plugin_status_label(plugin_name, False)

    def is_enabled(self, plugin_name):
        return self.plugin_status.get(plugin_name, False)

    def load_all_plugins(self):
        try:
            for entry in os.listdir(self.plugin_folder):
                full_path = os.path.join(self.plugin_folder, entry)
                if os.path.isdir(full_path) and not entry.startswith("__"):
                    self.load_plugin(entry)
        except Exception as e:
            log_exception(
                e,
                context="❌ Error loading all plugins",
                extra_info={"stage": "load_all_plugins"}
            )

    def unload_all_plugins(self):
        self.plugins.clear()
        self.plugin_locks.clear()
        self.plugin_status.clear()
        print("[PluginManager] 🔻 All plugins unloaded.")

    def list_plugins(self):
        return list(self.plugins.keys())
