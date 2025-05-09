# 🛠 Installation Guide – ItsOji EyeQ Enterprise

---

## ✅ Supported Platforms

* Windows 10 / 11 (64-bit)
* Ubuntu 20.04+ / Debian Linux
* Python 3.9+

---

## 📦 Step 1: Clone or Extract Project

If using ZIP:

* Extract folder to desired path (e.g., `E:/Project AI/itsOji_eyeq_enterprise/`)

If using Git:

```bash
git clone https://github.com/itsoji/eyeq_enterprise.git
cd eyeq_enterprise
```

---

## 🔧 Step 2: Install Requirements

Ensure you have Python 3.9+ installed.
Install dependencies:

```bash
pip install -r requirements.txt
```

You also need VLC media player (make sure it's added to your system PATH):

* Download: [https://www.videolan.org/vlc/](https://www.videolan.org/vlc/)

---

## ⚙️ Step 3: Configuration

Edit the file: `config/default_settings.json`

```json
{
  "camera_sources": ["rtsp://192.168.1.100/live"],
  "plugin_folder": "./plugins",
  "backup_folder": "config/backups/",
  "report_format": "PDF",
  "server_ip": "127.0.0.1"
}
```

---

## 🌐 Step 4: Run the Application

Run this from the root folder where `main_app.py` exists:

```bash
python main_app.py
```

You should see the GUI with Dashboard, Live View, and Alerts.

---

## 📅 Step 5: Optional Automation Setup

Use system scheduler to run these periodically:

* `scripts/backup_config.py`
* `scripts/generate_report.py`
* `scripts/schedule_tasks.py`
* `scripts/log_maintenance.py`

For Linux:

```bash
crontab -e
```

For Windows:

* Use Task Scheduler

---

## 👀 Final Check

* All cameras should display in Live View
* Alerts should appear when plugin triggers
* Logs should appear under `/logs/plugins/`

---

## 🌍 Deployment Notes

### Docker:

```bash
docker build -t eyeq_app .
docker run -p 8080:8080 eyeq_app
```

### Windows EXE:

Use PyInstaller:

```bash
pyinstaller --onefile main_app.py
```

---

## 🚀 You're Ready!

ItsOji EyeQ Enterprise is now live. Connect cameras, activate plugins, and monitor your plant with confidence.

For support, refer to the `user_manual.md` or contact the ItsOji support team.
