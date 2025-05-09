import sqlite3
import json
from datetime import datetime

class ReportManager:
    """Manages storage and querying of alerts for reporting purposes."""
    def __init__(self, db_path="eyeq_alerts.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.create_table()

    def create_table(self):
        """Create the alerts and archive tables if they do not exist."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    camera_id INTEGER,
                    plugin_name TEXT,
                    detection_info TEXT,
                    severity TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alerts_archive (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    camera_id INTEGER,
                    plugin_name TEXT,
                    detection_info TEXT,
                    severity TEXT
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON alerts(timestamp)")
            self.conn.commit()
            print("[ReportManager] Alerts table and archive ensured.")
        except Exception as e:
            print(f"[ReportManager] Error creating table: {e}")

    def insert_alert(self, camera_id, plugin_name, detection_info, severity="Medium"):
        """Insert a new alert into the database."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO alerts (timestamp, camera_id, plugin_name, detection_info, severity)
                VALUES (?, ?, ?, ?, ?)
            """, (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                camera_id,
                plugin_name,
                detection_info,
                severity
            ))
            self.conn.commit()
            print(f"[ReportManager] Alert inserted: Camera {camera_id}, Plugin {plugin_name}")
        except Exception as e:
            print(f"[ReportManager] Error inserting alert: {e}")

    def query_alerts(self, start_time=None, end_time=None, camera_id=None, severity=None, limit=None, offset=None):
        """
        Query alerts with filters, pagination, and return list of alerts.

        :param start_time: 'YYYY-MM-DD HH:MM:SS'
        :param end_time:   'YYYY-MM-DD HH:MM:SS'
        :param camera_id:  Camera ID to filter
        :param severity:   'High', 'Medium', 'Low', etc.
        :param limit:      Max results
        :param offset:     Offset for pagination
        :return: List of dicts
        """
        try:
            cursor = self.conn.cursor()
            query = "SELECT * FROM alerts WHERE 1=1"
            params = []

            if start_time and end_time:
                query += " AND timestamp BETWEEN ? AND ?"
                params.extend([start_time, end_time])
            if camera_id is not None:
                query += " AND camera_id = ?"
                params.append(camera_id)
            if severity:
                query += " AND severity = ?"
                params.append(severity)
            if limit:
                query += " LIMIT ?"
                params.append(limit)
                if offset:
                    query += " OFFSET ?"
                    params.append(offset)

            cursor.execute(query, params)
            rows = cursor.fetchall()
            result = [
                {
                    "id": row[0],
                    "timestamp": row[1],
                    "camera_id": row[2],
                    "plugin_name": row[3],
                    "detection_info": row[4],
                    "severity": row[5]
                }
                for row in rows
            ]
            return result
        except Exception as e:
            print(f"[ReportManager] Error querying alerts: {e}")
            return []

    def export_alerts_as_json(self, file_path, start_time=None, end_time=None):
        """Export filtered alerts as JSON to given file."""
        try:
            data = self.query_alerts(start_time=start_time, end_time=end_time)
            with open(file_path, "w") as f:
                json.dump(data, f, indent=4)
            print(f"[ReportManager] Exported alerts to {file_path}")
        except Exception as e:
            print(f"[ReportManager] Error exporting alerts to JSON: {e}")

    def archive_alerts(self, older_than: str):
        """
        Move old alerts (older than the given date) to archive.

        :param older_than: Date string 'YYYY-MM-DD'
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO alerts_archive (timestamp, camera_id, plugin_name, detection_info, severity)
                SELECT timestamp, camera_id, plugin_name, detection_info, severity
                FROM alerts
                WHERE date(timestamp) < ?
            """, (older_than,))
            cursor.execute("DELETE FROM alerts WHERE date(timestamp) < ?", (older_than,))
            self.conn.commit()
            print(f"[ReportManager] Archived alerts older than {older_than}")
        except Exception as e:
            print(f"[ReportManager] Error archiving alerts: {e}")

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            print("[ReportManager] Database connection closed.")
