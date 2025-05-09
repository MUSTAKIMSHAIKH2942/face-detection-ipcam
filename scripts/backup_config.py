# scripts/backup_config.py

import os
import shutil
from datetime import datetime

def backup_config():
    source_file = os.path.join("config", "default_settings.json")
    backup_folder = os.path.join("config", "backups")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file_timestamped = os.path.join(backup_folder, f"config_backup_{timestamp}.json")
    backup_file_latest = os.path.join("config", "config_backup.json")

    if not os.path.exists(source_file):
        print(f"[ERROR] Source config not found: {source_file}")
        return

    try:
        os.makedirs(backup_folder, exist_ok=True)

        # Save both timestamped and latest backup
        shutil.copy(source_file, backup_file_timestamped)
        shutil.copy(source_file, backup_file_latest)

        print(f"[BACKUP] Timestamped backup saved to: {backup_file_timestamped}")
        print(f"[BACKUP] Latest backup also saved to: {backup_file_latest}")
    except Exception as e:
        print(f"[ERROR] Backup failed: {e}")

if __name__ == "__main__":
    backup_config()
