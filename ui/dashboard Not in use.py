import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGroupBox, QListWidget, QListWidgetItem,
    QTextEdit, QComboBox, QCheckBox, QLineEdit
)
from PyQt5.QtCore import Qt, QTimer
from core.log_manager import LogManager
from datetime import datetime


class Dashboard(QWidget):
    """Dashboard page showing system status and quick summaries."""

    def __init__(self, alerts_page=None):
        super().__init__()
        self.alerts_page = alerts_page
        self.log_manager = LogManager()
        self.plugin_status_labels = {}  # ✅ NEW: for showing red status
        self.init_ui()
        self.log_refresh_timer = QTimer()
        self.log_refresh_timer.timeout.connect(self.load_logs)

    def set_monitor(self, monitor):
        self.monitor = monitor
        self.monitor_timer = QTimer(self)
        self.monitor_timer.timeout.connect(self.update_monitor_stats)
        self.monitor_timer.start(2000)  # every 2 seconds

    def update_monitor_stats(self):
        try:
            stats = self.monitor.get_stats()
            self.cpu_label.setText(f"CPU Usage: {stats['cpu']:.1f}%")
            self.ram_label.setText(f"RAM Usage: {stats['ram']} MB")
        except Exception:
            self.cpu_label.setText("CPU Usage: --%")
            self.ram_label.setText("RAM Usage: -- MB")

    def init_ui(self):
        main_layout = QVBoxLayout()

        # 1. System Health Section
        health_group = QGroupBox("System Health")
        health_layout = QHBoxLayout()
        self.cpu_label = QLabel("CPU Usage: --%")
        self.ram_label = QLabel("RAM Usage: --%")
        self.cameras_label = QLabel("Cameras Online: --")
        for lbl in [self.cpu_label, self.ram_label, self.cameras_label]:
            lbl.setAlignment(Qt.AlignCenter)
            health_layout.addWidget(lbl)
        health_group.setLayout(health_layout)
        main_layout.addWidget(health_group)

        # 6. Heartbeat Monitor Footer
        self.heartbeat_label = QLabel("Last Heartbeat: --")
        self.heartbeat_label.setAlignment(Qt.AlignCenter)
        self.heartbeat_label.setStyleSheet("color: grey;")
        main_layout.addWidget(self.heartbeat_label)

        self.heartbeat_timer = QTimer()
        self.heartbeat_timer.timeout.connect(self.check_heartbeat_status)
        self.heartbeat_timer.start(10000)  # check every 10 seconds

        # 2. Cameras Overview
        cameras_group = QGroupBox("Cameras Overview")
        cameras_layout = QVBoxLayout()
        self.total_cameras_label = QLabel("Total Cameras: --")
        cameras_layout.addWidget(self.total_cameras_label)
        cameras_group.setLayout(cameras_layout)
        main_layout.addWidget(cameras_group)

        # 3. Recent Alerts
        alerts_group = QGroupBox("Recent Alerts")
        alerts_layout = QVBoxLayout()
        self.alerts_list = QListWidget()
        alerts_layout.addWidget(self.alerts_list)
        alerts_group.setLayout(alerts_layout)
        main_layout.addWidget(alerts_group)

        # 4. Plugin Logs Section
        log_group = QGroupBox("Live Plugin Logs")
        log_layout = QVBoxLayout()

        # 🔽 Plugin Dropdown
        filter_row = QHBoxLayout()
        self.plugin_filter = QComboBox()
        self.plugin_filter.addItem("All Plugins")
        self.plugin_filter.addItems(self.log_manager.plugin_configs.keys())
        self.plugin_filter.currentIndexChanged.connect(self.load_logs)

        # 🔍 Search Bar
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search keyword...")
        self.search_box.textChanged.connect(self.load_logs)

        # 🔁 Auto-refresh
        self.auto_refresh = QCheckBox("Auto Refresh")
        self.auto_refresh.stateChanged.connect(self.toggle_auto_refresh)

        filter_row.addWidget(self.plugin_filter)
        filter_row.addWidget(self.search_box)
        filter_row.addWidget(self.auto_refresh)
        log_layout.addLayout(filter_row)

        # 📄 Log Display
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        log_layout.addWidget(self.log_output)

        # 🔄 Manual Refresh Button
        self.refresh_logs_btn = QPushButton("Refresh Logs")
        self.refresh_logs_btn.clicked.connect(self.load_logs)
        log_layout.addWidget(self.refresh_logs_btn)

        # 💾 Download Logs Button
        self.download_logs_btn = QPushButton("Download Logs")
        self.download_logs_btn.clicked.connect(self.export_logs_to_csv)
        log_layout.addWidget(self.download_logs_btn)

        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group)

        # 7. Plugin Status Icons
        plugin_status_group = QGroupBox("Plugin Status Overview")
        plugin_status_layout = QVBoxLayout()
        for name in self.log_manager.plugin_configs.keys():
            label = QLabel(f"{name}: ✅")
            label.setStyleSheet("color: green;")
            self.plugin_status_labels[name] = label
            plugin_status_layout.addWidget(label)
        plugin_status_group.setLayout(plugin_status_layout)
        main_layout.addWidget(plugin_status_group)

        # 5. Quick Actions
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QHBoxLayout()
        self.liveview_btn = QPushButton("Open Live View")
        self.reports_btn = QPushButton("View Reports")
        self.settings_btn = QPushButton("System Settings")
        for btn in [self.liveview_btn, self.reports_btn, self.settings_btn]:
            actions_layout.addWidget(btn)
        actions_group.setLayout(actions_layout)
        main_layout.addWidget(actions_group)

        self.setLayout(main_layout)
        self.load_logs()  # ✅ Initial load

    def update_plugin_status_label(self, plugin_name, is_enabled):
        label = self.plugin_status_labels.get(plugin_name)
        if label:
            if is_enabled:
                label.setText(f"{plugin_name}: ✅")
                label.setStyleSheet("color: green;")
            else:
                label.setText(f"{plugin_name}: ❌")
                label.setStyleSheet("color: red;")

    def update_system_health(self, cpu_usage, ram_usage, cameras_online):
        self.cpu_label.setText(f"CPU Usage: {cpu_usage}%")
        self.ram_label.setText(f"RAM Usage: {ram_usage} MB")
        self.cameras_label.setText(f"Cameras Online: {cameras_online}")

    def update_cameras_overview(self, all_cameras: dict, live_cameras: dict):
        total = len(all_cameras)
        ip_cams = [cid for cid in all_cameras if cid.startswith("ip_")]
        nvr_cams = [cid for cid in all_cameras if cid.startswith("nvr_")]
        usb_cams = [cid for cid in all_cameras if cid.startswith("usb_")]

        lines = [
            f"Total Cameras: {total}",
            f"  - IP Cameras: {len(ip_cams)}",
            f"  - NVR Cameras: {len(nvr_cams)}",
            f"  - USB Cameras: {len(usb_cams)}",
            "",
            f"Online Cameras: {len(live_cameras)}"
        ]
        for cam_id in live_cameras:
            lines.append(f"  - {cam_id} ✅")

        self.total_cameras_label.setText("\n".join(lines))

    def update_recent_alerts(self, alerts):
        self.alerts_list.clear()
        for alert in alerts:
            item_text = f"{alert['timestamp']} | Cam {alert['camera_id']} | {alert['plugin_name']} - {alert['severity']}"
            self.alerts_list.addItem(item_text)

    def add_alert_entry(self, alert):
        text = f"{alert['timestamp']} | Cam {alert['camera_id']} | {alert['plugin_name']} - {alert['severity']}"
        self.alerts_list.insertItem(0, QListWidgetItem(text))
        if self.alerts_page:
            self.alerts_page.add_alert_entry(alert)

    def set_camera_count(self, count):
        self.cameras_label.setText(f"Cameras Online: {count}")

    def toggle_auto_refresh(self, state):
        if state == Qt.Checked:
            self.log_refresh_timer.start(5000)
        else:
            self.log_refresh_timer.stop()

    def load_logs(self):
        try:
            selected_plugin = self.plugin_filter.currentText()
            keyword = self.search_box.text().strip().lower()
            self.log_output.clear()

            if selected_plugin == "All Plugins":
                for plugin in self.log_manager.plugin_configs:
                    lines = self.log_manager.get_recent_logs(plugin, limit=10)
                    for line in lines:
                        if keyword in line.lower():
                            self.log_output.append(f"[{plugin}] {line.strip()}")
            else:
                lines = self.log_manager.get_recent_logs(selected_plugin, limit=30)
                for line in lines:
                    if keyword in line.lower():
                        self.log_output.append(line.strip())
        except Exception as e:
            self.log_output.append(f"[Error] Failed to load logs: {e}")

    def export_logs_to_csv(self):
        try:
            os.makedirs("logs/exports", exist_ok=True)
            export_path = f"logs/exports/logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            lines = self.log_output.toPlainText().strip().split("\n")

            with open(export_path, "w", encoding="utf-8") as f:
                f.write("Timestamp,Plugin,Log Message\n")
                for line in lines:
                    try:
                        if line.startswith("[") and "]" in line:
                            ts_end = line.find("]")
                            timestamp = line[1:ts_end].strip()
                            remaining = line[ts_end + 1:].strip()
                            if "::" in remaining:
                                plugin_part, log_message = remaining.split("::", 1)
                                plugin_name = plugin_part.strip().upper()
                                message = log_message.strip()
                            else:
                                plugin_name = "UNKNOWN"
                                message = remaining.strip()
                            f.write(f'"{timestamp}","{plugin_name}","{message}"\n')
                    except Exception:
                        continue
            self.log_output.append(f"\n✅ Logs exported to {export_path}")
        except Exception as e:
            self.log_output.append(f"[Error] Failed to export logs: {e}")

    def update_heartbeat(self, timestamp):
        self.last_heartbeat_time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        self.heartbeat_label.setText(f"Last Heartbeat: {timestamp}")
        self.heartbeat_label.setStyleSheet("color: green;")

    def check_heartbeat_status(self):
        if not hasattr(self, 'last_heartbeat_time') or self.last_heartbeat_time is None:
            return
        seconds_passed = (datetime.now() - self.last_heartbeat_time).total_seconds()
        if seconds_passed > 120:
            self.heartbeat_label.setStyleSheet("color: red;")
            self.heartbeat_label.setText("Last Heartbeat: Stale ❌")
        elif seconds_passed > 60:
            self.heartbeat_label.setStyleSheet("color: orange;")
            self.heartbeat_label.setText("Last Heartbeat: Delayed ⚠️")
        else:
            self.heartbeat_label.setStyleSheet("color: green;")

        try:
            if self.alert_manager:
                severity = None
                if seconds_passed > 120:
                    severity = "Critical"
                elif seconds_passed > 60:
                    severity = "Warning"
                if severity:
                    alert = {
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "camera_id": "system",
                        "plugin_name": "heartbeat_monitor",
                        "detection_info": "⚠️ System heartbeat delayed or missing.",
                        "severity": severity
                    }
                    self.alert_manager.add_alert(alert)
                    if self.alerts_page:
                        self.alerts_page.add_alert_entry(alert)
        except Exception as e:
            print("[Dashboard] ❌ Failed to push heartbeat alert:", e)