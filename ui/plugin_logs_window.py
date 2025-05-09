import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QComboBox,
    QLineEdit, QCheckBox, QTextEdit
)
from PyQt5.QtCore import Qt, QTimer
from core.log_manager import LogManager


class PluginLogWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Plugin Logs Viewer")
        self.setMinimumSize(700, 500)
        self.log_manager = LogManager()
        self.init_ui()
        self.load_logs()

    def init_ui(self):
        layout = QVBoxLayout()

        # Top row: plugin selector, search, auto-refresh
        filter_row = QHBoxLayout()
        self.plugin_filter = QComboBox()
        self.plugin_filter.addItem("All Plugins")
        self.plugin_filter.addItems(self.log_manager.plugin_configs.keys())
        self.plugin_filter.currentIndexChanged.connect(self.load_logs)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search keyword...")
        self.search_box.textChanged.connect(self.load_logs)

        self.auto_refresh = QCheckBox("Auto Refresh")
        self.auto_refresh.stateChanged.connect(self.toggle_auto_refresh)

        filter_row.addWidget(self.plugin_filter)
        filter_row.addWidget(self.search_box)
        filter_row.addWidget(self.auto_refresh)
        layout.addLayout(filter_row)

        # Log display
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)

        self.setLayout(layout)
        self.timer = QTimer()
        self.timer.timeout.connect(self.load_logs)

    def toggle_auto_refresh(self, state):
        if state == Qt.Checked:
            self.timer.start(5000)
        else:
            self.timer.stop()

    def load_logs(self):
        try:
            selected_plugin = self.plugin_filter.currentText()
            keyword = self.search_box.text().strip().lower()
            self.log_output.clear()

            entries = []
            if selected_plugin == "All Plugins":
                for plugin in self.log_manager.plugin_configs:
                    lines = self.log_manager.get_recent_logs(plugin, limit=10)
                    for line in lines:
                        if keyword in line.lower():
                            entries.append(line.strip())
            else:
                lines = self.log_manager.get_recent_logs(selected_plugin, limit=30)
                for line in lines:
                    if keyword in line.lower():
                        entries.append(line.strip())

            self.log_output.setText("\n".join(entries))

        except Exception as e:
            self.log_output.setText(f"[Error] Failed to load logs: {e}")
