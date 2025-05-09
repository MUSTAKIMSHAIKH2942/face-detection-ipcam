# ui/help_docs.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit
from PyQt5.QtGui import QFont

class HelpDocsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Help & Documentation")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Title
        title_label = QLabel("📘 ItsOji EyeQ Enterprise – Help Guide")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))

        # Help Content
        self.help_text = QTextEdit()
        self.help_text.setReadOnly(True)
        self.help_text.setFont(QFont("Courier", 10))

        # Content
        help_content = """
🧠 HOW TO USE:

1. Go to the Settings Page to add your IP or USB cameras.
2. Use the Plugin Menu to enable required AI features like fire, face, helmet, or intrusion detection.
3. Live View will show real-time camera feed with overlays from selected plugins.
4. The Alerts section lists all real-time alerts from all cameras/plugins.
5. Reports & Analytics lets you filter, view, and export logs (CSV/PDF).
6. Administration Panel shows logs, audit actions, and lets you test plugins.
7. Use the Scheduler to automate daily backups and reports (00:01 & 00:05 AM).

📖 FAQ:

• Q: Why is my camera not showing in Live View?
  A: Check camera settings, IP, and connection status in the settings page.

• Q: How can I add a new detection plugin?
  A: Add your Python-based plugin under `/plugins/<your_plugin>/`, ensure it follows `base_plugin.py` structure, and restart the app.

• Q: Where are logs saved?
  A: All plugin logs are stored in `logs/<plugin_name>/`, compressed daily/weekly as per config.

• Q: How to export logs?
  A: Go to Reports tab or run `scripts/export_logs.py --plugin <name>`

ℹ️ CONTACT & SUPPORT:

• 🌐 Website: https://www.itsoji.com/support
• 📧 Email: support@itsoji.com
• 🛠 Powered by ItsOji Pvt Ltd | Version: v1.0.0

"""
        self.help_text.setPlainText(help_content)

        # Assemble layout
        layout.addWidget(title_label)
        layout.addWidget(self.help_text)
        self.setLayout(layout)
