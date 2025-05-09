# 📖 ItsOji EyeQ Enterprise - User Manual

This manual is designed to help end users operate the ItsOji EyeQ Enterprise system effectively.

---

## ✅ 1. Introduction

ItsOji EyeQ Enterprise is a real-time AI-powered multi-camera monitoring platform designed for industrial environments. It provides intelligent detection using custom plugins and manages alerts, reports, and system health.

---

## ⚖️ 2. System Requirements

* OS: Windows 10/11 or Linux
* Python 3.10+
* VLC Media Player (for video playback)
* RAM: 4 GB minimum (8 GB recommended)
* Disk Space: 1 GB minimum for logs and backups

---

## 📊 3. Installation

1. Clone or download the project.
2. Install Python dependencies:

```bash
pip install -r requirements.txt
```

3. Install VLC player from [https://www.videolan.org/vlc/](https://www.videolan.org/vlc/)
4. Launch the application:

```bash
python main_app.py
```

---

## 🔍 4. Interface Overview

### Main Sections:

* **Dashboard**: View CPU/RAM usage, alerts, and camera summaries.
* **Live View**: Watch all active camera streams.
* **Alerts**: View recent AI detection alerts.
* **Reports**: Export detection logs as CSV or PDF.
* **Admin**: View audit logs and run test plugins.
* **Settings**: Change backup paths, server IP, and enable/disable plugins.
* **Help**: Access user help and contact support.

---

## 🚀 5. First-Time Setup

1. Edit `config/default_settings.json`:

   * Add camera RTSP streams under `camera_sources`
   * Set `plugin_folder` path (usually `plugins/`)
   * Define `backup_folder` for saving reports

2. Run the app:

```bash
python main_app.py
```

3. You should now see the Live View and Dashboard.

---

## 💻 6. Using Plugins

* Plugins are auto-loaded from the `plugins/` folder.
* Enable or disable plugins from Settings.
* All plugins must subclass `BasePlugin` and have a `run()` method.

---

## 🗕️ 7. Scheduling

Automated scripts:

* `scripts/schedule_tasks.py`: Runs scheduled backups and report generation
* `scripts/log_maintenance.py`: Cleans old logs and compresses data

Use Windows Task Scheduler or Linux `cron` to automate.

---

## 📊 8. Reports and Logs

* Reports are saved as CSV and PDF in `/logs/reports/`
* Plugin logs are saved in `/logs/plugins/`
* System health logs: `/logs/system_health.log`
* Alerts and events: `/logs/alerts.csv`

---

## ⚡ 9. Troubleshooting

| Issue             | Solution                                          |
| ----------------- | ------------------------------------------------- |
| App not launching | Check Python version and required modules         |
| Camera feed blank | Check RTSP stream and camera power                |
| Plugin error      | Check plugin folder, structure, and logs          |
| UI lagging        | Reduce number of cameras or close background apps |

---

## 🌐 10. Support

For help, contact the ItsOji team via the support email provided in the Help section of the app.

---

## ✨ 11. Tips

* Use smaller camera resolutions for faster performance
* Schedule backups during low-usage hours
* Regularly clean up old logs to save space

---

## 🔧 12. Advanced Features

* NVR integration support (Phase 8)
* AI plugin auto-updater (planned)
* External actuator (DI/DO) support via Modbus/OPC

---

Stay safe. Stay smart. Stay ItsOji.
