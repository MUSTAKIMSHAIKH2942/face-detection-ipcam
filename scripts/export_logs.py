# ─── Standalone Compatibility Fix ─────────────────────────────────────────────
if __name__ == "__main__" or __package__ is None:
    import os, sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# ─── Imports ─────────────────────────────────────────────────────────────────
import os
import csv
import argparse
from datetime import datetime
from core.log_manager import LogManager

EXPORT_FOLDER = "logs/exports"
os.makedirs(EXPORT_FOLDER, exist_ok=True)

def parse_log_line(line):
    try:
        timestamp = line.split("]")[0].strip("[")
        level = line.split("]")[1].strip(" [")
        plugin = line.split("]")[2].strip(" [")
        message = line.split("::")[1].strip()
        return [timestamp, plugin, level, message]
    except Exception as e:
        return [None, None, None, line.strip()]

def export_logs_to_csv(plugin_name=None, output_file=None, limit=100):
    manager = LogManager()
    logs = manager.get_recent_logs(plugin_name, limit)

    output_path = os.path.join(EXPORT_FOLDER, output_file or f"exported_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")

    try:
        with open(output_path, mode="w", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Timestamp", "Plugin", "Log Level", "Log Message"])

            for line in logs:
                row = parse_log_line(line)
                writer.writerow(row)

        print(f"[✔] Logs exported to: {output_path}")
    except Exception as e:
        print(f"[Error] Failed to export logs: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export plugin logs to CSV")
    parser.add_argument("--plugin", type=str, help="Plugin name (optional)", default=None)
    parser.add_argument("--limit", type=int, help="Number of lines", default=100)
    parser.add_argument("--output", type=str, help="CSV output filename", default=None)
    args = parser.parse_args()

    export_logs_to_csv(plugin_name=args.plugin, output_file=args.output, limit=args.limit)
