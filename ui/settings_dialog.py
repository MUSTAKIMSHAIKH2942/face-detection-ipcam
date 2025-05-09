import json
import os
import cv2
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit,
    QPushButton, QFileDialog, QMessageBox, QLabel, QHBoxLayout,
    QCheckBox, QGroupBox, QListWidget, QGridLayout
)
from PyQt5.QtCore import Qt
from core.config_validator import validate_config_file
from core.crash_logger import log_exception
from ui.plugin_logging_ui import PluginLoggingDialog
from core.plugin_manager import PluginManager
from core.nvr_manager import NVRManager


class SettingsDialog(QDialog):
    def __init__(self, config_path="config/default_settings.json"):
        super().__init__()
        self.setWindowTitle("Settings")
        self.setMinimumWidth(960)
        self.setMinimumHeight(600)
        self.setStyleSheet("""
            QLineEdit, QPushButton, QListWidget { min-height: 32px; font-size: 13px; }
            QGroupBox { margin-top: 16px; }
            QLabel { font-weight: bold; }
        """)

        self.config_path = config_path
        self.settings = {}
        self.plugin_manager = PluginManager()
        self.plugin_checkboxes = {}

        self.load_settings()
        self.plugin_manager.load_all_plugins()
        self.init_ui()

    def load_settings(self):
        try:
            if os.path.exists(self.config_path):
                validate_config_file(self.config_path)
                with open(self.config_path, 'r') as f:
                    self.settings = json.load(f)
            else:
                self.settings = {
                    "server_ip": "",
                    "backup_folder": "",
                    "plugin_folder": "",
                    "camera_sources": [],
                    "nvr_settings": {
                        "nvr_ip": "",
                        "username": "",
                        "password": "",
                        "channel_count": 0
                    }
                }
        except Exception as e:
            log_exception(e, "While loading settings in SettingsDialog")
            QMessageBox.critical(self, "Invalid Config", f"Settings file is corrupted or invalid:\n{e}")
            self.reject()

    def init_ui(self):
        main_layout = QVBoxLayout()
        grid_layout = QGridLayout()
        grid_layout.setSpacing(20)

        # Left column
        left_panel = QVBoxLayout()
        form_layout = QFormLayout()
        self.server_ip_edit = QLineEdit(self.settings.get("server_ip", ""))
        self.backup_folder_edit = QLineEdit(self.settings.get("backup_folder", ""))
        self.plugin_folder_edit = QLineEdit(self.settings.get("plugin_folder", ""))

        browse_backup_btn = QPushButton("Browse")
        browse_backup_btn.clicked.connect(self.browse_backup_folder)
        backup_folder_layout = QHBoxLayout()
        backup_folder_layout.addWidget(self.backup_folder_edit)
        backup_folder_layout.addWidget(browse_backup_btn)

        browse_plugin_btn = QPushButton("Browse")
        browse_plugin_btn.clicked.connect(self.browse_plugin_folder)
        plugin_folder_layout = QHBoxLayout()
        plugin_folder_layout.addWidget(self.plugin_folder_edit)
        plugin_folder_layout.addWidget(browse_plugin_btn)

        form_layout.addRow("Server IP:", self.server_ip_edit)
        form_layout.addRow("Backup Folder:", backup_folder_layout)
        form_layout.addRow("Plugin Folder:", plugin_folder_layout)
        left_panel.addLayout(form_layout)

        camera_group = QGroupBox("Camera Sources")
        camera_group_layout = QVBoxLayout()

        camera_input_grid = QGridLayout()
        self.camera_label_edit = QLineEdit(); self.camera_label_edit.setPlaceholderText("Label")
        self.camera_url_edit = QLineEdit(); self.camera_url_edit.setPlaceholderText("rtsp://IP/stream")
        self.camera_user_edit = QLineEdit(); self.camera_user_edit.setPlaceholderText("Username")
        self.camera_pass_edit = QLineEdit(); self.camera_pass_edit.setPlaceholderText("Password")
        self.camera_pass_edit.setEchoMode(QLineEdit.Password)

        camera_input_grid.addWidget(self.camera_label_edit, 0, 0)
        camera_input_grid.addWidget(self.camera_url_edit, 0, 1)
        camera_input_grid.addWidget(self.camera_user_edit, 0, 2)
        camera_input_grid.addWidget(self.camera_pass_edit, 0, 3)

        add_btn = QPushButton("Add")
        remove_btn = QPushButton("Remove")
        test_btn = QPushButton("Test Cameras")
        add_btn.clicked.connect(self.add_camera_source)
        remove_btn.clicked.connect(self.remove_camera_source)
        test_btn.clicked.connect(self.test_camera_connection)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(remove_btn)
        btn_layout.addWidget(test_btn)

        self.camera_list = QListWidget()
        self.camera_list.setMinimumHeight(100)
        for src in self.settings.get("camera_sources", []):
            self.camera_list.addItem(str(src))

        camera_group_layout.addLayout(camera_input_grid)
        camera_group_layout.addLayout(btn_layout)
        camera_group_layout.addWidget(self.camera_list)
        camera_group.setLayout(camera_group_layout)
        left_panel.addWidget(camera_group)

        # Right column
        right_panel = QVBoxLayout()
        nvr_group = QGroupBox("NVR Configuration")
        nvr_form = QFormLayout()
        nvr_config = self.settings.get("nvr_settings", {})
        self.nvr_ip_edit = QLineEdit(nvr_config.get("nvr_ip", ""))
        self.nvr_user_edit = QLineEdit(nvr_config.get("username", ""))
        self.nvr_pass_edit = QLineEdit(nvr_config.get("password", ""))
        self.nvr_chan_edit = QLineEdit(str(nvr_config.get("channel_count", 0)))
        self.nvr_connect_btn = QPushButton("Connect NVR")
        self.nvr_connect_btn.clicked.connect(self.test_nvr_connection)

        nvr_form.addRow("NVR IP:", self.nvr_ip_edit)
        nvr_form.addRow("Username:", self.nvr_user_edit)
        nvr_form.addRow("Password:", self.nvr_pass_edit)
        nvr_form.addRow("Channel Count:", self.nvr_chan_edit)
        nvr_form.addRow("", self.nvr_connect_btn)
        nvr_group.setLayout(nvr_form)
        right_panel.addWidget(nvr_group)

        # Grid placement
        grid_layout.addLayout(left_panel, 0, 0)
        grid_layout.addLayout(right_panel, 0, 1)
        main_layout.addLayout(grid_layout)

        # Divider
        divider = QLabel("""<hr style='color:black; background-color:black; height:1px; border:none;'>""")
        divider.setFixedHeight(2)
        main_layout.addWidget(divider)

        # Plugin Activation Section
        plugin_group = QGroupBox("Plugin Activation")
        plugin_layout = QVBoxLayout()
        for name in self.plugin_manager.list_plugins():
            checkbox = QCheckBox(name)
            checkbox.setChecked(self.plugin_manager.is_enabled(name))
            checkbox.stateChanged.connect(lambda state, n=name: self.toggle_plugin(state, n))
            self.plugin_checkboxes[name] = checkbox
            plugin_layout.addWidget(checkbox)
        plugin_group.setLayout(plugin_layout)
        main_layout.addWidget(plugin_group)

        # Buttons with plugin logging option
        button_layout = QHBoxLayout()
        logging_btn = QPushButton("Plugin Logging Settings...")
        logging_btn.clicked.connect(lambda: self.open_logging_settings(self.plugin_manager.list_plugins()))
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        save_btn.clicked.connect(self.save_settings)
        cancel_btn.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(logging_btn)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def toggle_plugin(self, state, plugin_name):
        if state == Qt.Checked:
            self.plugin_manager.enable_plugin(plugin_name)
        else:
            self.plugin_manager.disable_plugin(plugin_name)

    def browse_backup_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Backup Folder")
        if folder:
            self.backup_folder_edit.setText(folder)

    def browse_plugin_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Plugin Folder")
        if folder:
            self.plugin_folder_edit.setText(folder)

    def add_camera_source(self):
        label = self.camera_label_edit.text().strip()
        url = self.camera_url_edit.text().strip()
        username = self.camera_user_edit.text().strip()
        password = self.camera_pass_edit.text().strip()
        if not label or not url:
            QMessageBox.warning(self, "Input Required", "Label and URL/IP are mandatory.")
            return
        if username and password:
            final_url = url.replace("rtsp://", f"rtsp://{username}:{password}@")
        else:
            final_url = url
        entry = f"{label}: {final_url}"
        self.camera_list.addItem(entry)
        self.camera_label_edit.clear()
        self.camera_url_edit.clear()
        self.camera_user_edit.clear()
        self.camera_pass_edit.clear()

    def remove_camera_source(self):
        for item in self.camera_list.selectedItems():
            self.camera_list.takeItem(self.camera_list.row(item))

    def save_settings(self):
        self.settings["server_ip"] = self.server_ip_edit.text()
        self.settings["backup_folder"] = self.backup_folder_edit.text()
        self.settings["plugin_folder"] = self.plugin_folder_edit.text()
        self.settings["camera_sources"] = [self.camera_list.item(i).text() for i in range(self.camera_list.count())]
        self.settings["nvr_settings"] = {
            "nvr_ip": self.nvr_ip_edit.text(),
            "username": self.nvr_user_edit.text(),
            "password": self.nvr_pass_edit.text(),
            "channel_count": int(self.nvr_chan_edit.text()) if self.nvr_chan_edit.text().isdigit() else 0
        }
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.settings, f, indent=4)
            QMessageBox.information(self, "✅ Settings Saved", "<b style='color:black;'>Settings saved successfully.</b>")
            self.accept()
        except Exception as e:
            log_exception(e, "While saving settings in SettingsDialog")
            QMessageBox.critical(self, "Error", f"Failed to save settings:\n{e}")

    def open_logging_settings(self, plugin_list):
        try:
            # Add system_health to plugin list if not present
            if "system_health" not in plugin_list:
                plugin_list.append("system_health")
            dlg = PluginLoggingDialog(active_plugins=plugin_list)
            dlg.exec_()
        except Exception as e:
            log_exception(e, "While opening plugin logging settings")
            QMessageBox.critical(self, "Error", f"Failed to open logging settings:\n{e}")


    def test_nvr_connection(self):
        try:
            config = {
                "nvr_ip": self.nvr_ip_edit.text(),
                "username": self.nvr_user_edit.text(),
                "password": self.nvr_pass_edit.text(),
                "channel_count": int(self.nvr_chan_edit.text()) if self.nvr_chan_edit.text().isdigit() else 0
            }
            nvr = NVRManager(config)
            if nvr.connect_to_nvr():
                QMessageBox.information(self, "✅ NVR Connected", "Connection to NVR was successful.")
            else:
                QMessageBox.warning(self, "❌ NVR Failed", "Could not connect to the NVR.")
        except Exception as e:
            log_exception(e, "Test NVR connection error")
            QMessageBox.critical(self, "Error", f"Failed to connect to NVR:\n{e}")

    def test_camera_connection(self):
        try:
            sources = [self.camera_list.item(i).text().split(": ", 1)[-1] for i in range(self.camera_list.count())]
            if not sources:
                QMessageBox.warning(self, "No Camera Source", "No camera source defined.")
                return
            failed = []
            for src in sources:
                cap = cv2.VideoCapture(src)
                if not cap.isOpened():
                    failed.append(str(src))
                cap.release()
            if failed:
                QMessageBox.warning(self, "❌ Camera Test Failed", f"Failed to connect to: {', '.join(failed)}")
            else:
                QMessageBox.information(self, "✅ Camera Connected", "All camera sources are valid.")
        except Exception as e:
            log_exception(e, "Test Camera connection error")
            QMessageBox.critical(self, "Error", f"Camera test failed:\n{e}")
