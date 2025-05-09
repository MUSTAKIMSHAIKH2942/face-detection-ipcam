# ─── Standalone Compatibility Fix ─────────────────────────────────────────────
if __name__ == "__main__" or __package__ is None:
    import os, sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# ─── Imports ─────────────────────────────────────────────────────────────────
import os
import json
import threading
import gzip
from datetime import datetime, timedelta
from core.crash_logger import log_exception


class LogManager:
    """
    Smart Log Manager — controls AI plugin logging dynamically.
    Supports: event vs continuous vs sensor, compression, retention, frequency, meta fields, filters.
    """

    def __init__(self, config_path="config/logging_config.json", log_dir="logs"):
        self.config_path = config_path
        self.log_dir = log_dir
        self.lock = threading.Lock()
        self.plugin_configs = {}
        self.last_logged = {}  # plugin: timestamp_ms
        self.last_data = {}    # plugin: last_meta snapshot
        self._load_config()
        os.makedirs(self.log_dir, exist_ok=True)

    def _load_config(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    self.plugin_configs = json.load(f)
            else:
                self.plugin_configs = {}
        except Exception as e:
            log_exception(e, context="Failed to load log config")
            self.plugin_configs = {}

  # (No change to standalone fix, imports, or initial class docstring...)

    def log(self, plugin_name, data: dict):
        cfg = self.plugin_configs.get(plugin_name, {})
        if not cfg.get("enabled", False):
            return

        now = datetime.now()
        timestamp_ms = int(now.timestamp() * 1000)
        freq = cfg.get("frequency_ms", 1000)

        mode = cfg.get("mode", "event")
        last_time = self.last_logged.get(plugin_name, 0)

        if mode == "continuous" and (timestamp_ms - last_time < freq):
            return

        if cfg.get("log_trigger_filter") == "distinct_only":
            if data == self.last_data.get(plugin_name):
                return
            if data:
                self.last_data[plugin_name] = data.copy()

        # Compose log line
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        meta_fields = cfg.get("meta_fields", [])
        log_level = cfg.get("log_level", "INFO")
        source_name = cfg.get("source_name", plugin_name.upper())

        # ✅ FIX: handle NoneType safely
        if not data or not isinstance(data, dict):
            meta_info = "NO_DATA"
        else:
            meta_info = " | ".join(f"{k}:{data.get(k, '')}" for k in meta_fields)

        log_line = f"[{timestamp}] [{log_level}] [{source_name}] :: {meta_info}\n"

        output_path = cfg.get("output_path", f"logs/{plugin_name}/")
        os.makedirs(output_path, exist_ok=True)

        file_name = f"{now.strftime('%Y-%m-%d')}.log"
        full_path = os.path.join(output_path, file_name)

        try:
            with self.lock:
                with open(full_path, "a", encoding="utf-8") as f:
                    f.write(log_line)
            self.last_logged[plugin_name] = timestamp_ms
        except Exception as e:
            log_exception(e, context=f"Failed to log data for {plugin_name}", extra_info={"file": full_path})


    def _should_compress(self, fname, compress_rule, now):
        try:
            if not fname.endswith(".log"):
                return False
            fdate = datetime.strptime(fname.replace(".log", ""), "%Y-%m-%d")
            delta = (now - fdate).days

            if compress_rule == "daily" and delta >= 1:
                return True
            elif compress_rule == "2days" and delta >= 2:
                return True
            elif compress_rule == "weekly" and delta >= 7:
                return True
        except Exception as e:
            log_exception(e, context="Failed to parse date for log compression", extra_info={"file": fname})
            return False
        return False

    def cleanup_logs(self):
        """Compress and delete old logs based on config."""
        now = datetime.now()
        for plugin, cfg in self.plugin_configs.items():
            folder = cfg.get("output_path", f"logs/{plugin}/")
            os.makedirs(folder, exist_ok=True)

            compress_rule = cfg.get("compression_period", "daily")
            retention_days = cfg.get("retention_days", 30)

            for fname in os.listdir(folder):
                path = os.path.join(folder, fname)

                try:
                    if fname.endswith(".log") and self._should_compress(fname, compress_rule, now):
                        gz_path = path.replace(".log", ".gz")
                        with open(path, 'rb') as f_in, gzip.open(gz_path, 'wb') as f_out:
                            f_out.writelines(f_in)
                        os.remove(path)
                        print(f"[LogManager] 📦 Compressed → {gz_path}")

                    # Auto delete old files
                    if os.path.exists(path):  # ← Add existence check
                        mtime = datetime.fromtimestamp(os.path.getmtime(path))
                        if (now - mtime).days > retention_days:
                            os.remove(path)
                            print(f"[LogManager] 🗑 Deleted → {path}")


                except Exception as e:
                    log_exception(e, context="Error processing plugin log file", extra_info={"plugin": plugin, "file": path})

    def get_plugin_config(self, plugin_name):
        return self.plugin_configs.get(plugin_name, {})
    
    def get_recent_logs(self, plugin_name=None, limit=30):
        """Read last N lines from plugin logs (all or specific)."""
        lines = []
        today = datetime.now().strftime("%Y-%m-%d")

        plugins_to_read = [plugin_name] if plugin_name else list(self.plugin_configs.keys())

        for plugin in plugins_to_read:
            cfg = self.plugin_configs.get(plugin, {})
            log_path = os.path.join(cfg.get("output_path", f"logs/{plugin}/"), f"{today}.log")

            if os.path.exists(log_path):
                try:
                    with open(log_path, "r", encoding="utf-8") as f:
                        file_lines = f.readlines()
                        tagged_lines = [f"[{plugin}] {line.strip()}" for line in file_lines[-limit:]]
                        lines.extend(tagged_lines)
                except Exception as e:
                    lines.append(f"[{plugin}] Error reading log: {e}")
        return lines[-limit:]



# ─── Optional: Allow Direct Script Execution ────────────────────────────────
if __name__ == "__main__":
    print("[LogManager] Standalone execution started...")
    manager = LogManager()
    manager.cleanup_logs()
