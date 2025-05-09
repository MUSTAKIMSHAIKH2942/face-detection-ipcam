# tests/test_crash_logger.py

import sys
import os
sys.path.append(os.path.abspath("."))  # Add project root to sys.path

from core.crash_logger import log_exception, log_info


def test_crash_logging():
    try:
        1 / 0  # Simulated crash
    except Exception as e:
        log_exception(e, context="Division Test Failure")

    log_info("Manual info message for logging test.")


if __name__ == "__main__":
    test_crash_logging()
    print("[TEST] crash_logger.py test completed.")



