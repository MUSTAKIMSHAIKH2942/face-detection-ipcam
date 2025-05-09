# scripts/log_maintenance.py

"""
Log Maintenance Script — Auto clean, compress, and manage logs via LogManager.

Author: ItsOji Team
"""

if __name__ == "__main__" or __package__ is None:
    import os, sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.log_manager import LogManager
from core.crash_logger import log_exception


def clean_and_compress_logs():
    print("[LogMaintenance] 🔁 Starting scheduled cleanup...")
    try:
        manager = LogManager()
        manager.cleanup_logs()
        print("[LogMaintenance] ✅ Completed log cleanup.")
    except Exception as e:
        print(f"[LogMaintenance] ❌ Critical error during cleanup: {e}")
        log_exception(e, context="log_maintenance.py")


if __name__ == "__main__":
    clean_and_compress_logs()
