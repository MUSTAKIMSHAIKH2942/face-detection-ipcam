import os
import traceback
from datetime import datetime

LOG_DIR = "logs"
LOG_FILE = "crash.log"
MAX_LOG_SIZE_MB = 1

def _rotate_log():
    log_path = os.path.join(LOG_DIR, LOG_FILE)
    if os.path.exists(log_path) and os.path.getsize(log_path) > MAX_LOG_SIZE_MB * 1024 * 1024:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_name = f"crash_{timestamp}.log"
        os.rename(log_path, os.path.join(LOG_DIR, new_name))

def log_exception(exc=None, context="", level="ERROR", extra_info=None):
    """
    Log an exception or context to crash.log with optional extra data.
    
    :param exc: Exception object (optional)
    :param context: Description of where the error occurred
    :param level: Severity level (e.g., INFO, WARNING, ERROR, CRITICAL)
    :param extra_info: Dictionary of extra metadata (e.g., plugin, camera ID)
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = [
        "\n--- Exception Logged ---",
        f"Time     : {timestamp}",
        f"Level    : {level}",
        f"Context  : {context}"
    ]

    if extra_info:
        for key, value in extra_info.items():
            log_entry.append(f"{key.capitalize():<9}: {value}")

    log_entry.append("Traceback:")

    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        _rotate_log()
        with open(os.path.join(LOG_DIR, LOG_FILE), "a", encoding='utf-8') as f:
            f.write("\n".join(log_entry) + "\n")

            if exc:
                traceback.print_exception(type(exc), exc, exc.__traceback__, file=f)
            else:
                f.write("(No exception object passed)\n")
            f.write("\n")

        # Also print to console
        print("\n".join(log_entry))
        if exc:
            traceback.print_exception(type(exc), exc, exc.__traceback__)
        else:
            print("(No exception object passed)\n")

    except Exception as log_error:
        print("[CrashLogger] ❌ Failed to write crash log:", log_error)

def log_info(message, extra_info=None):
    """Log a simple informational message."""
    log_exception(exc=None, context=message, level="INFO", extra_info=extra_info)
