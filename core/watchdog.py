import os
import json
import threading
import time
from datetime import datetime
from core.crash_logger import log_exception

# ─────────────────────────────────────────────────────────────
# 🔁 Plugin Failure Watchdog Layer (Phase 2.1 + 2.3)
# ─────────────────────────────────────────────────────────────
PluginHealthStatus = {}
LOG_PATH = "logs/stalled_plugins.log"
CONFIG_PATH = "config/logging_config.json"
os.makedirs("logs", exist_ok=True)


def get_plugin_failure_limit(plugin_name):
    """Read per-plugin max_plugin_failures from logging_config.json."""
    try:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r") as f:
                config = json.load(f)
            return config.get(plugin_name, {}).get("max_plugin_failures", config.get("max_plugin_failures", 3))
    except Exception as e:
        log_exception(e, context="Failed to read max_plugin_failures for plugin")
    return 3  # default fallback


def log_stalled_plugin(plugin_name):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] ❌ Plugin STALLED: {plugin_name}\n")
    except Exception as e:
        log_exception(e, context="Failed to write to stalled_plugins.log")


def log_plugin_recovery(plugin_name):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] 🔁 Plugin RECOVERED: {plugin_name}\n")
    except Exception as e:
        log_exception(e, context="Failed to write to plugin recovery log")


def reset_plugin_health(plugin_name):
    PluginHealthStatus[plugin_name] = {"failures": 0, "status": "OK"}
    log_plugin_recovery(plugin_name)


def report_plugin_result(plugin_name, success: bool):
    if plugin_name not in PluginHealthStatus:
        PluginHealthStatus[plugin_name] = {"failures": 0, "status": "OK"}

    if success:
        PluginHealthStatus[plugin_name]["failures"] = 0
        PluginHealthStatus[plugin_name]["status"] = "OK"
    else:
        PluginHealthStatus[plugin_name]["failures"] += 1
        max_failures = get_plugin_failure_limit(plugin_name)
        if PluginHealthStatus[plugin_name]["failures"] >= max_failures:
            if PluginHealthStatus[plugin_name]["status"] != "STALLED":
                PluginHealthStatus[plugin_name]["status"] = "STALLED"
                log_stalled_plugin(plugin_name)


def get_plugin_health():
    return PluginHealthStatus


def get_plugin_status(plugin_name):
    return PluginHealthStatus.get(plugin_name, {}).get("status", "UNKNOWN")


# ─────────────────────────────────────────────────────────────
# 🕒 Base Watchdog Timer Class
# ─────────────────────────────────────────────────────────────
class Watchdog:
    def __init__(self, timeout=10):
        self.timeout = timeout
        self.timer = None
        self.running = False
        self.callback = None
        self.last_feed_time = time.time()

    def start(self, callback):
        self.callback = callback
        self.running = True
        self._reset_timer()
        print(f"[Watchdog] ✅ Started with timeout {self.timeout}s")

    def _reset_timer(self):
        if self.timer:
            self.timer.cancel()
        self.last_feed_time = time.time()
        self.timer = threading.Timer(self.timeout, self._timeout_handler)
        self.timer.start()

    def feed(self):
        if self.running:
            print(f"[Watchdog] 🐾 Feed received at {time.strftime('%H:%M:%S')} (resetting timer)")
            self._reset_timer()

    def _timeout_handler(self):
        try:
            print(f"[Watchdog] ⏰ Timeout detected at {time.strftime('%H:%M:%S')} — executing callback.")
            if self.callback:
                self.callback()
        except Exception as e:
            log_exception(e)

    def stop(self):
        self.running = False
        if self.timer:
            self.timer.cancel()
        print(f"[Watchdog] 🛑 Stopped")
