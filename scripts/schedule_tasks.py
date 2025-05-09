# scripts/schedule_tasks.py

"""
Task Scheduler — Auto-run config backup, report generation, and log maintenance daily.

Author: ItsOji Team
"""

import schedule
import time
import subprocess
from datetime import datetime
import os

def run_script(script_name, task_name):
    print(f"[SCHEDULER] 🕒 Running {task_name} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    script_path = os.path.join("scripts", script_name)
    if os.path.exists(script_path):
        result = subprocess.call(["python", script_path])
        if result == 0:
            print(f"[SCHEDULER] ✅ {task_name} completed.")
        else:
            print(f"[SCHEDULER] ❌ {task_name} failed.")
    else:
        print(f"[SCHEDULER] ❌ {script_name} not found!")

def main():
    
    # Schedule config backup at 00:01 AM
    schedule.every().day.at("00:01").do(run_script, "backup_config.py", "Config Backup")
    # Schedule report generation at 00:05 AM
    schedule.every().day.at("00:05").do(run_script, "generate_report.py", "Report Generation")
    # Schedule log cleanup at 00:10 AM
    schedule.every().day.at("00:10").do(run_script, "log_maintenance.py", "Log Cleanup")

    print("[SCHEDULER] ✅ Task scheduler started. Waiting for next task...")

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
