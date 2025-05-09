# ui/administration.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QHBoxLayout
from datetime import datetime
import os

class AdministrationPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Administration Panel")
        self.init_ui()
        self.load_logs()

    def init_ui(self):
        layout = QVBoxLayout()

        # Audit Logs
        audit_label = QLabel("User Audit Logs")
        self.audit_logs = QTextEdit()
        self.audit_logs.setReadOnly(True)

        # System Logs
        syslog_label = QLabel("System Logs")
        self.sys_logs = QTextEdit()
        self.sys_logs.setReadOnly(True)

        # Button Section
        btn_layout = QHBoxLayout()
        self.plugin_btn = QPushButton("Run Plugin Test (Simulated)")
        self.plugin_btn.clicked.connect(self.run_plugin_test)

        self.refresh_btn = QPushButton("Refresh Logs")
        self.refresh_btn.clicked.connect(self.load_logs)

        btn_layout.addWidget(self.plugin_btn)
        btn_layout.addWidget(self.refresh_btn)

        # Assemble Layout
        layout.addWidget(audit_label)
        layout.addWidget(self.audit_logs)
        layout.addWidget(syslog_label)
        layout.addWidget(self.sys_logs)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def load_logs(self):
        """Load content from system.log and audit.log"""
        try:
            with open("logs/system.log", "r", encoding='utf-8') as f:
                self.sys_logs.setPlainText(f.read())
        except FileNotFoundError:
            self.sys_logs.setPlainText("System log file not found.")

        try:
            with open("logs/audit.log", "r", encoding='utf-8') as f:
                self.audit_logs.setPlainText(f.read())
        except FileNotFoundError:
            self.audit_logs.setPlainText("Audit log file not found.")

    def run_plugin_test(self):
        """Simulate plugin action and log it to audit file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} | Admin executed test plugin\n"

        self.audit_logs.append(f"[PLUGIN TEST] {log_entry.strip()}")
        self.audit_logs.moveCursor(self.audit_logs.textCursor().End)

        try:
            os.makedirs("logs", exist_ok=True)
            with open("logs/audit.log", "a", encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            self.audit_logs.append(f"[ERROR] Could not write audit log: {e}")
