'''
Alerts Management Page - Displays a table of active and historical alerts (Real-time Updatable).

Author: ItsOji Team
'''

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QMenu, QPushButton, QFileDialog
)
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QColor
import csv

class AlertsManagement(QWidget):
    """Alerts management page."""
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Initialise the alerts table layout."""
        layout = QVBoxLayout()

        self.alerts_table = QTableWidget()
        self.alerts_table.setColumnCount(5)
        self.alerts_table.setHorizontalHeaderLabels(
            ["Timestamp", "Camera ID", "Plugin", "Detection Info", "Severity"]
        )
        self.alerts_table.horizontalHeader().setStretchLastSection(True)
        self.alerts_table.setSortingEnabled(True)
        self.alerts_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.alerts_table.customContextMenuRequested.connect(self.show_context_menu)

        layout.addWidget(self.alerts_table)

        # Export Button
        self.export_btn = QPushButton("Export to CSV")
        self.export_btn.clicked.connect(self.export_to_csv)
        layout.addWidget(self.export_btn)

        self.setLayout(layout)

    def add_alert_entry(self, alert):
        """
        Add a new alert row to the table dynamically.

        :param alert: Dictionary with keys: timestamp, camera_id, plugin_name, detection_info, severity
        """
        row_position = self.alerts_table.rowCount()
        self.alerts_table.insertRow(row_position)

        items = [
            alert.get("timestamp", ""),
            str(alert.get("camera_id", "")),
            alert.get("plugin_name", ""),
            alert.get("detection_info", ""),
            alert.get("severity", "")
        ]

        for col, item in enumerate(items):
            cell = QTableWidgetItem(item)
            if col == 4:  # Severity column
                colour = self.get_severity_color(item)
                cell.setBackground(colour)
                cell.setTextAlignment(Qt.AlignCenter)
            self.alerts_table.setItem(row_position, col, cell)

    @staticmethod
    def get_severity_color(severity):
        """Return a QColor based on severity."""
        severity = severity.lower()
        if severity == "high":
            return QColor(255, 153, 153)  # Light Red
        elif severity == "critical":
            return QColor(255, 77, 77)    # Deep Red
        elif severity == "medium":
            return QColor(255, 204, 102)  # Orange
        else:
            return QColor(255, 255, 255)  # White

    def show_context_menu(self, position: QPoint):
        """Show right-click context menu for acknowledging alert."""
        menu = QMenu()
        acknowledge_action = menu.addAction("Acknowledge (Remove)")
        action = menu.exec_(self.alerts_table.viewport().mapToGlobal(position))
        if action == acknowledge_action:
            self.acknowledge_selected_alert()

    def acknowledge_selected_alert(self):
        """Remove the selected alert row."""
        row = self.alerts_table.currentRow()
        if row != -1:
            self.alerts_table.removeRow(row)

    def clear_alerts(self):
        """Clear all rows from the table."""
        self.alerts_table.setRowCount(0)

    def get_all_alerts(self):
        """Return a list of all alert entries as dictionaries."""
        alerts = []
        for row in range(self.alerts_table.rowCount()):
            alert = {
                "timestamp": self.alerts_table.item(row, 0).text(),
                "camera_id": self.alerts_table.item(row, 1).text(),
                "plugin_name": self.alerts_table.item(row, 2).text(),
                "detection_info": self.alerts_table.item(row, 3).text(),
                "severity": self.alerts_table.item(row, 4).text()
            }
            alerts.append(alert)
        return alerts

    def export_to_csv(self):
        """Export current alerts table to CSV."""
        path, _ = QFileDialog.getSaveFileName(self, "Export Alerts", "", "CSV Files (*.csv)")
        if path:
            try:
                with open(path, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(["Timestamp", "Camera ID", "Plugin", "Detection Info", "Severity"])
                    for alert in self.get_all_alerts():
                        writer.writerow([
                            alert["timestamp"],
                            alert["camera_id"],
                            alert["plugin_name"],
                            alert["detection_info"],
                            alert["severity"]
                        ])
                print(f"[AlertsManagement] Exported alerts to {path}")
            except Exception as e:
                print(f"[AlertsManagement] Export failed: {e}")
