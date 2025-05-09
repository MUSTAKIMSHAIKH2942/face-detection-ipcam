import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGroupBox, QListWidget, QListWidgetItem,
    QDialog, QTextEdit, QScrollArea
)
from PyQt5.QtCore import Qt, QTimer
from core.log_manager import LogManager
from core.watchdog import get_plugin_health
from datetime import datetime


class PluginLogWindow(QDialog):
    def __init__(self, log_manager):
        super().__init__()
        self.setWindowTitle("Plugin Logs Viewer")
        self.resize(700, 500)
        self.log_manager = log_manager
        self.init_ui()
        self.load_logs()

    def init_ui(self):
        layout = QVBoxLayout()
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)
        self.setLayout(layout)

    def load_logs(self):
        try:
            plugin_names = self.log_manager.plugin_configs.keys()
            lines = []
            for name in plugin_names:
                entries = self.log_manager.get_recent_logs(name, limit=10)
                lines.extend(entries)
            self.log_output.setText("\n".join(lines))
        except Exception as e:
            self.log_output.setText(f"[Error] Failed to load logs: {e}")


class PluginStatusWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Plugin Health Monitor")
        self.setMinimumSize(400, 400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.status_labels = {}

        self.status_layout = QVBoxLayout()
        for plugin in get_plugin_health():
            lbl = QLabel()
            self.status_labels[plugin] = lbl
            self.status_layout.addWidget(lbl)

        group = QGroupBox("Live Plugin Status")
        group.setLayout(self.status_layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(group)
        layout.addWidget(scroll)

        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_status)
        self.timer.start(5000)

        self.refresh_status()

    def refresh_status(self):
        statuses = get_plugin_health()
        for plugin, status in statuses.items():
            label = self.status_labels.get(plugin)
            if label:
                color = "green" if status else "red"
                state = "✔️" if status else "❌"
                label.setText(f"{plugin}: {state}")
                label.setStyleSheet(f"color: {color}; font-weight: bold;")


class Dashboard(QWidget):
    def __init__(self, alerts_page=None):
        super().__init__()
        self.alerts_page = alerts_page
        self.log_manager = LogManager()
        self.plugin_status_labels = {}
        self.last_heartbeat_time = None
        self.init_ui()

    def set_monitor(self, monitor):
        self.monitor = monitor
        self.monitor_timer = QTimer(self)
        self.monitor_timer.timeout.connect(self.update_monitor_stats)
        self.monitor_timer.start(2000)

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

        # System Health
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

        # Heartbeat
        self.heartbeat_label = QLabel("Last Heartbeat: --")
        self.heartbeat_label.setAlignment(Qt.AlignCenter)
        self.heartbeat_label.setStyleSheet("color: grey;")
        main_layout.addWidget(self.heartbeat_label)

        self.heartbeat_timer = QTimer()
        self.heartbeat_timer.timeout.connect(self.check_heartbeat_status)
        self.heartbeat_timer.start(10000)

        # Cameras Overview
        cameras_group = QGroupBox("Cameras Overview")
        cameras_layout = QVBoxLayout()
        self.total_cameras_label = QLabel("Total Cameras: --")
        cameras_layout.addWidget(self.total_cameras_label)
        cameras_group.setLayout(cameras_layout)
        main_layout.addWidget(cameras_group)

        # Alerts Overview
        alerts_group = QGroupBox("Recent Alerts")
        alerts_layout = QVBoxLayout()
        self.alerts_list = QListWidget()
        alerts_layout.addWidget(self.alerts_list)
        alerts_group.setLayout(alerts_layout)
        main_layout.addWidget(alerts_group)

        # Quick Actions
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QHBoxLayout()
        self.liveview_btn = QPushButton("Open Live View")
        self.reports_btn = QPushButton("View Reports")
        self.settings_btn = QPushButton("System Settings")
        self.plugin_logs_btn = QPushButton("View Plugin Logs")
        self.plugin_status_btn = QPushButton("Plugin Health")

        self.plugin_logs_btn.clicked.connect(self.open_plugin_logs_window)
        self.plugin_status_btn.clicked.connect(self.open_plugin_status_window)

        for btn in [self.liveview_btn, self.reports_btn, self.settings_btn,
                    self.plugin_logs_btn, self.plugin_status_btn]:
            actions_layout.addWidget(btn)
        actions_group.setLayout(actions_layout)
        main_layout.addWidget(actions_group)

        self.setLayout(main_layout)

    def open_plugin_logs_window(self):
        self.log_window = PluginLogWindow(self.log_manager)
        self.log_window.show()

    def open_plugin_status_window(self):
        self.status_window = PluginStatusWindow()
        self.status_window.show()

    def update_plugin_status_label(self, plugin_name, is_enabled):
        label = self.plugin_status_labels.get(plugin_name)
        if label:
            label.setText(f"{plugin_name}: {'✅' if is_enabled else '❌'}")
            label.setStyleSheet(f"color: {'green' if is_enabled else 'red'};")

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

    def update_heartbeat(self, timestamp):
        self.last_heartbeat_time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        self.heartbeat_label.setText(f"Last Heartbeat: {timestamp}")
        self.heartbeat_label.setStyleSheet("color: green;")

    def check_heartbeat_status(self):
        if not self.last_heartbeat_time:
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
