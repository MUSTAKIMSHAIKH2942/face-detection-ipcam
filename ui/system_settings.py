from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QFormLayout
)
import json
from pathlib import Path

class SystemSettings(QWidget):
    """System settings page."""
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_nvr_settings()  # ✅ Load NVR on startup

    def init_ui(self):
        main_layout = QVBoxLayout()

        # 1. Camera Configuration
        camera_layout = QHBoxLayout()
        camera_label = QLabel("Camera Configuration:")
        self.configure_cameras_btn = QPushButton("Configure Cameras")
        camera_layout.addWidget(camera_label)
        camera_layout.addWidget(self.configure_cameras_btn)
        main_layout.addLayout(camera_layout)

        # 2. Plugin Management
        plugin_layout = QHBoxLayout()
        plugin_label = QLabel("Plugin Management:")
        self.configure_plugins_btn = QPushButton("Manage Plugins")
        plugin_layout.addWidget(plugin_label)
        plugin_layout.addWidget(self.configure_plugins_btn)
        main_layout.addLayout(plugin_layout)

        # 3. Backup Settings
        backup_layout = QHBoxLayout()
        backup_label = QLabel("Backup Configuration:")
        self.backup_settings_btn = QPushButton("Configure Backup")
        self.perform_backup_btn = QPushButton("Backup Now")
        backup_layout.addWidget(backup_label)
        backup_layout.addWidget(self.backup_settings_btn)
        backup_layout.addWidget(self.perform_backup_btn)
        main_layout.addLayout(backup_layout)

        # 4. NVR Configuration
        nvr_form = QFormLayout()
        nvr_section_label = QLabel("NVR Configuration")
        nvr_section_label.setStyleSheet("font-weight: bold; font-size: 14px")
        main_layout.addWidget(nvr_section_label)

        self.nvr_ip_input = QLineEdit()
        self.nvr_user_input = QLineEdit()
        self.nvr_pass_input = QLineEdit()
        self.nvr_chan_input = QLineEdit()

        nvr_form.addRow("NVR IP:", self.nvr_ip_input)
        nvr_form.addRow("Username:", self.nvr_user_input)
        nvr_form.addRow("Password:", self.nvr_pass_input)
        nvr_form.addRow("Channel Count:", self.nvr_chan_input)

        self.save_nvr_btn = QPushButton("Save NVR Settings")
        self.save_nvr_btn.clicked.connect(self.save_nvr_settings)
        nvr_form.addRow(self.save_nvr_btn)
        main_layout.addLayout(nvr_form)

        # 5. System Maintenance
        maintenance_layout = QHBoxLayout()
        maintenance_label = QLabel("System Maintenance:")
        self.reset_system_btn = QPushButton("Reset System")
        self.check_update_btn = QPushButton("Check for Updates")
        maintenance_layout.addWidget(maintenance_label)
        maintenance_layout.addWidget(self.reset_system_btn)
        maintenance_layout.addWidget(self.check_update_btn)
        main_layout.addLayout(maintenance_layout)

        self.setLayout(main_layout)

    def load_nvr_settings(self):
        config_path = Path("config/default_settings.json")
        try:
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    nvr = config.get("nvr_settings", {})
                    self.nvr_ip_input.setText(nvr.get("nvr_ip", ""))
                    self.nvr_user_input.setText(nvr.get("username", ""))
                    self.nvr_pass_input.setText(nvr.get("password", ""))
                    self.nvr_chan_input.setText(str(nvr.get("channel_count", "")))
                    print("[SystemSettings] ✅ NVR settings loaded.")
        except Exception as e:
            print(f"[SystemSettings] ❌ Failed to load NVR settings: {e}")

    def save_nvr_settings(self):
        config_path = Path("config/default_settings.json")
        try:
            config = {}
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)

            config["nvr_settings"] = {
                "nvr_ip": self.nvr_ip_input.text(),
                "username": self.nvr_user_input.text(),
                "password": self.nvr_pass_input.text(),
                "channel_count": int(self.nvr_chan_input.text()) if self.nvr_chan_input.text().isdigit() else 0
            }

            with open(config_path, 'w') as f:
                json.dump(config, f, indent=4)

            print("[SystemSettings] ✅ NVR settings saved.")
        except Exception as e:
            print(f"[SystemSettings] ❌ Failed to save NVR settings: {e}")
