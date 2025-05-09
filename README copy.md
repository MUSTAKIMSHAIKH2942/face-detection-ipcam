# 🧠 ItsOji EyeQ Enterprise

**Industrial AI Camera Software with Real-Time Detection, Logging, and Control**

---

## 📦 Features

* Multi-Camera Live View with plugin support
* AI Plugins: Helmet, Fire, Face, Intrusion Detection
* Alerts & Reporting System
* User Management & Audit Logs
* Plugin Loader + Configurable Detection
* OPC UA & Modbus TCP Integration
* Scheduled Backups and Report Generation
* Clean Dark Theme UI
* Docker and EXE Packaging Ready

---

## 💽 Folder Structure

```
itsOji_eyeq_enterprise/
├── main_app.py
├── requirements.txt
├── .gitignore
├── README.md
├── LICENSE
├── config/
│   ├── default_settings.json
│   └── config_backup.json
├── core/
│   ├── camera_manager.py
│   ├── plugin_manager.py
│   ├── alert_manager.py
│   ├── report_manager.py
│   ├── user_manager.py
│   ├── create_inits.py
│   ├── crash_logger.py
│   ├── config_validator.py
│   ├── system_monitor.py
│   └── watchdog.py
├── ui/
│   ├── main_window.py
│   ├── settings_dialog.py
│   ├── dashboard.py
│   ├── live_view.py
│   ├── alerts_management.py
│   ├── reports_analytics.py
│   ├── user_management.py
│   ├── system_settings.py
│   ├── administration.py
│   ├── help_docs.py
│   ├── assets/
│   └── styles/
│       └── main.qss
├── plugins/
│   ├── base_plugin.py
│   ├── helmet_detection/
│   ├── fire_detection/
│   ├── intrusion_detection/
│   └── face_recognition/
├── industrial/
│   ├── opc_server.py
│   └── modbus_client.py
├── ml_ops/
│   └── model_updater.py
├── scripts/
│   ├── backup_config.py
│   ├── generate_report.py
│   ├── schedule_tasks.py
│   ├── export_logs.py
│   └── log_maintenance.py
├── tests/
│   ├── test_camera.py
│   ├── test_plugin_management.py
│   ├── test_alert_manager.py
│   ├── test_report_manager.py
│   ├── test_user_management.py
│   ├── test_opc_server.py
│   └── test_modbus_client.py
├── docs/
│   ├── user_manual.md
│   ├── technical_manual.md
│   └── installation_guide.md
├── Dockerfile
├── docker-compose.yml
└── assets/
    └── alert.wav
```

---

## ⚡ Getting Started

### 1. Install Requirements

```bash
pip install -r requirements.txt
```

### 2. Run the App

```bash
python main_app.py
```

### 3. Default Config

Update your camera streams and plugin folder in `config/default_settings.json`

### 4. Plugins

Place plugin modules under `plugins/` and use `base_plugin.py` as the base class.

---

## 🧱 Future Expansion

* Multi-camera NVR integration
* Cloud sync and dashboard
* ONNX model plugin support
* Voice alert & actuator control

---

## ✅ License

MIT License — see `LICENSE`

---

## 🌟 Credits

Developed by the ItsOji Team with love for industrial innovation.
