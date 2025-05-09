# ui/plugin_logging_ui.py

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, QSpinBox, QCheckBox,
    QLabel, QPushButton, QScrollArea, QGroupBox, QFileDialog, QHBoxLayout, QMessageBox
)
import json
import os


class PluginLoggingDialog(QDialog):
    """
    Plugin Logging Configuration Dialog - allows configuring plugin-wise log settings.
    """

    def __init__(self, config_path="config/logging_config.json", active_plugins=None):
        super().__init__()
        self.setWindowTitle("Plugin Logging Configuration")
        self.resize(600, 500)
        self.config_path = config_path
        self.plugin_settings = {}
        self.plugin_widgets = {}
        self.active_plugins = active_plugins or []

        self.load_config()
        self.init_ui()

    def load_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                self.plugin_settings = json.load(f)
        else:
            self.plugin_settings = {}

    def init_ui(self):
        layout = QVBoxLayout()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QDialog()
        form_layout = QVBoxLayout()

        for plugin in sorted(self.active_plugins):
            if plugin not in self.plugin_settings:
                self.plugin_settings[plugin] = {
                    "enabled": False,
                    "mode": "event",
                    "frequency_ms": 1000,
                    "output_path": f"logs/{plugin}/",
                    "compression_period": "daily",
                    "retention_days": 7,
                    "log_level": "info",
                    "log_trigger_filter": "distinct_only",
                    "meta_fields": ["camera_id", "confidence", "timestamp_ms"]
                }

            group_box = QGroupBox(plugin)
            group_layout = QFormLayout()
            config = self.plugin_settings[plugin]

            enabled_checkbox = QCheckBox()
            enabled_checkbox.setChecked(config.get("enabled", False))

            mode_combo = QComboBox()
            mode_combo.addItems(["event", "continuous", "sensor"])
            mode_combo.setCurrentText(config.get("mode", "event"))

            freq_spin = QSpinBox()
            freq_spin.setRange(0, 100000)
            freq_spin.setValue(config.get("frequency_ms", 1000))

            out_path_edit = QLineEdit(config.get("output_path", f"logs/{plugin}/"))
            browse_btn = QPushButton("Browse")
            browse_btn.clicked.connect(lambda _, edit=out_path_edit: self.browse_folder(edit))
            out_path_layout = QHBoxLayout()
            out_path_layout.addWidget(out_path_edit)
            out_path_layout.addWidget(browse_btn)

            compress_combo = QComboBox()
            compress_combo.addItems(["daily", "2days", "weekly"])
            compress_combo.setCurrentText(config.get("compression_period", "daily"))

            retention_spin = QSpinBox()
            retention_spin.setRange(1, 365)
            retention_spin.setValue(config.get("retention_days", 7))

            level_combo = QComboBox()
            level_combo.addItems(["info", "warning", "error"])
            level_combo.setCurrentText(config.get("log_level", "info"))

            trigger_combo = QComboBox()
            trigger_combo.addItems(["distinct_only", "all"])
            trigger_combo.setCurrentText(config.get("log_trigger_filter", "distinct_only"))

            meta_edit = QLineEdit(",".join(config.get("meta_fields", [])))

            group_layout.addRow("Enabled", enabled_checkbox)
            group_layout.addRow("Mode", mode_combo)
            group_layout.addRow("Frequency (ms)", freq_spin)
            group_layout.addRow("Output Path", out_path_layout)
            group_layout.addRow("Compression Period", compress_combo)
            group_layout.addRow("Retention Days", retention_spin)
            group_layout.addRow("Log Level", level_combo)
            group_layout.addRow("Trigger Filter", trigger_combo)
            group_layout.addRow("Meta Fields (comma-separated)", meta_edit)

            group_box.setLayout(group_layout)
            form_layout.addWidget(group_box)

            self.plugin_widgets[plugin] = {
                "enabled": enabled_checkbox,
                "mode": mode_combo,
                "frequency_ms": freq_spin,
                "output_path": out_path_edit,
                "compression_period": compress_combo,
                "retention_days": retention_spin,
                "log_level": level_combo,
                "log_trigger_filter": trigger_combo,
                "meta_fields": meta_edit
            }

        scroll_content.setLayout(form_layout)
        scroll.setWidget(scroll_content)

        save_btn = QPushButton("💾 Save Configuration")
        save_btn.clicked.connect(self.save_config)
        reset_btn = QPushButton("🔁 Reset to Default")
        reset_btn.clicked.connect(self.reset_to_default)

        layout.addWidget(scroll)
        layout.addWidget(save_btn)
        layout.addWidget(reset_btn)
        self.setLayout(layout)

    def browse_folder(self, edit_field):
        folder = QFileDialog.getExistingDirectory(self, "Select Log Output Folder")
        if folder:
            edit_field.setText(folder)

    def save_config(self):
        for plugin, widgets in self.plugin_widgets.items():
            self.plugin_settings[plugin] = {
                "enabled": widgets["enabled"].isChecked(),
                "mode": widgets["mode"].currentText(),
                "frequency_ms": widgets["frequency_ms"].value(),
                "output_path": widgets["output_path"].text(),
                "compression_period": widgets["compression_period"].currentText(),
                "retention_days": widgets["retention_days"].value(),
                "log_level": widgets["log_level"].currentText(),
                "log_trigger_filter": widgets["log_trigger_filter"].currentText(),
                "meta_fields": [
                    x.strip() for x in widgets["meta_fields"].text().split(",") if x.strip()
                ]
            }

        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.plugin_settings, f, indent=4)
                try:
                    from core.log_manager import LogManager
                    LogManager()._load_config()
                except Exception as e:
                    print("[PluginLoggingUI] Could not reload LogManager:", e)

            QMessageBox.information(self, "Saved", "✅ Logging settings saved successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"❌ Failed to save settings:\n{e}")
    

    def reset_to_default(self):
        confirm = QMessageBox.question(self, "Confirm Reset", "Reset all logging configurations to default?")
        if confirm == QMessageBox.Yes:
            for plugin in self.active_plugins:
                self.plugin_settings[plugin] = {
                    "enabled": False,
                    "mode": "event",
                    "frequency_ms": 1000,
                    "output_path": f"logs/{plugin}/",
                    "compression_period": "daily",
                    "retention_days": 7,
                    "log_level": "info",
                    "log_trigger_filter": "distinct_only",
                    "meta_fields": ["camera_id", "confidence", "timestamp_ms"]
                }
            self.init_ui()

