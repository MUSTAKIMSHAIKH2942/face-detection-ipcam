import sys
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QGroupBox, QScrollArea
)
from PyQt5.QtCore import QTimer
from core.watchdog import get_plugin_health


class PluginStatusWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Plugin Health Monitor")
        self.setMinimumSize(400, 400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.status_labels = {}

        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_status)
        self.timer.start(5000)

        # Create the internal status layout
        self.status_layout = QVBoxLayout()
        for plugin in get_plugin_health():
            lbl = QLabel()
            self.status_labels[plugin] = lbl
            self.status_layout.addWidget(lbl)

        # Wrap status layout in group
        group = QGroupBox("Live Plugin Status")
        group.setLayout(self.status_layout)

        # Add group to scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(group)

        layout.addWidget(scroll)
        self.setLayout(layout)

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
