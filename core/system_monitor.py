import threading
import time
import psutil
import os
from datetime import datetime
from core.log_manager import LogManager
from core.crash_logger import log_exception

FALLBACK_LOG = "logs/system_health.log"

class SystemMonitor:
    def __init__(self, interval=10, cpu_threshold=85, mem_threshold=1024, thread_threshold=50):
        self.interval = interval
        self.cpu_threshold = cpu_threshold  # in percent
        self.mem_threshold = mem_threshold  # in MB
        self.thread_threshold = thread_threshold
        self.running = False
        self.log_manager = None

        # For live UI access
        self.latest_cpu = 0.0
        self.latest_ram = 0
        self.latest_threads = 0
        self.latest_uptime = "0s"
        self.latest_status = "OK"

        try:
            self.log_manager = LogManager()
        except Exception as e:
            log_exception(e, "SystemMonitor: Failed to load LogManager")

    def log_fallback(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        os.makedirs(os.path.dirname(FALLBACK_LOG), exist_ok=True)
        with open(FALLBACK_LOG, "a", encoding="utf-8", errors="replace") as f:
            f.write(log_entry)
        print(log_entry.strip())

    def log(self, meta_data: dict):
        if self.log_manager:
            try:
                self.log_manager.log("system_health", meta_data)
                return
            except Exception as e:
                log_exception(e, "SystemMonitor: LogManager.log failed")
        # Fallback
        fallback_line = " | ".join(f"{k}: {v}" for k, v in meta_data.items())
        self.log_fallback(fallback_line)

    def check_system_health(self):
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory().used // (1024 * 1024)  # MB
        threads = threading.active_count()
        uptime_sec = int(time.time() - psutil.boot_time())
        status = "OK"

        if cpu > self.cpu_threshold or mem > self.mem_threshold or threads > self.thread_threshold:
            status = "WARNING"

        # Store values for UI access
        self.latest_cpu = cpu
        self.latest_ram = mem
        self.latest_threads = threads
        self.latest_uptime = f"{uptime_sec}s"
        self.latest_status = status

        data = {
            "status": status,
            "uptime": self.latest_uptime,
            "cpu": f"{cpu:.1f}%",
            "ram": f"{mem}MB",
            "threads": threads
        }
        self.log(data)

    def get_cpu(self):
        return self.latest_cpu

    def get_ram(self):
        return self.latest_ram

    def get_stats(self):
        return {
            "cpu": self.latest_cpu,
            "ram": self.latest_ram,
            "threads": self.latest_threads,
            "uptime": self.latest_uptime,
            "status": self.latest_status
        }

    def start(self):
        self.running = True
        thread = threading.Thread(target=self._run, daemon=True)
        thread.start()

    def stop(self):
        self.running = False

    def _run(self):
        while self.running:
            try:
                self.check_system_health()
            except Exception as e:
                log_exception(e, "SystemMonitor Runtime Error")
            time.sleep(self.interval)

# ✅ Optional manual test
if __name__ == "__main__":
    print("[SystemMonitor] Standalone test running...")
    monitor = SystemMonitor(interval=5)
    monitor.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("System Monitor stopped.")
