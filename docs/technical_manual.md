# 📑 ItsOji EyeQ Enterprise - Technical Manual

This manual is intended for developers, integrators, and advanced users of ItsOji EyeQ Enterprise.

---

## ✅ 1. Overview

ItsOji EyeQ Enterprise is a modular Python-based software platform for real-time AI detection, camera monitoring, plugin orchestration, and industrial integration.

---

## 📊 2. Architecture

### Core Components:

* `core/`: All logic modules for plugin management, user systems, alerts, reports, logging.
* `ui/`: PyQt5-based GUI split into main\_window + sub-pages.
* `plugins/`: Modular folders for AI plugins.
* `scripts/`: CLI-based automation for backup, report generation, etc.
* `industrial/`: Modbus and OPC-UA server support for external system communication.

### Threading:

* Plugin processing and system monitoring run in daemon threads.
* GUI remains responsive via PyQt signal-slot architecture.

---

## 🤖 3. Plugin API

All plugins must:

* Inherit from `BasePlugin`
* Implement a `run(frame, camera_id)` method

### Example:

```python
from plugins.base_plugin import BasePlugin

class Plugin(BasePlugin):
    def run(self, frame, camera_id=None):
        # return result dictionary
        return {"label": "helmet", "score": 0.91}
```

### Runtime Loading:

Plugins are dynamically loaded via `core/plugin_manager.py` using importlib.

---

## 🔜 4. Logging System

* `core/log_manager.py` handles plugin-specific logs
* Configurations per plugin in `config/logging_config.json`
* Logs support: log level, retention, frequency, format, compression

### Paths:

* Plugin Logs: `logs/plugins/`
* System Logs: `logs/system_health.log`
* Alerts: `logs/alerts.csv`

---

## 📅 5. Schedulers and Maintenance

* `scripts/schedule_tasks.py`: Runs recurring jobs
* `scripts/log_maintenance.py`: Compresses & cleans logs
* `scripts/backup_config.py`: Copies JSON config to backups

Automate with cron/Task Scheduler.

---

## 🛠️ 6. Industrial Integration

### Modbus (TCP Client):

* Defined in `industrial/modbus_client.py`
* Simulates coil output and reading from camera events

### OPC UA Server:

* Implemented in `industrial/opc_server.py`
* Plugin alerts and system status exposed as variables

---

## ⚡ 7. Real-Time Monitoring

### `core/system_monitor.py`

* Tracks CPU %, memory (MB), active threads
* Logs warnings if thresholds exceeded

### `core/watchdog.py`

* Feed timer pattern to restart unresponsive components

---

## 📊 8. Testing

Test cases for core functions are under `tests/`:

* `test_plugin_management.py`
* `test_opc_server.py`
* `test_alert_manager.py`

Use `pytest` to execute tests:

```bash
pytest tests/
```

---

## 🌍 9. Packaging & Deployment

### EXE:

* Use `pyinstaller` with `--onefile` for `main_app.py`

### Docker:

* Included `Dockerfile` and `docker-compose.yml`

---

## ⚖️ 10. Best Practices

* Validate config with `core/config_validator.py`
* Log all exceptions using `core/crash_logger.py`
* Use plugin toggling UI in `settings_dialog.py`
* Thread all long-running tasks

---

## 🤝 Contribution

* Fork the repo
* Create a new branch for your feature
* Submit a pull request after testing

---

End of Technical Manual.
