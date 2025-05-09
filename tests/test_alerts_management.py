# test_alerts_management.py (temporary)
import sys
from PyQt5.QtWidgets import QApplication
from ui.alerts_management import AlertsManagement

if __name__ == "__main__":
    app = QApplication(sys.argv)
    alerts_page = AlertsManagement()

    # Add dummy alerts
    alerts_page.add_alert("2025-04-27 17:00", 0, "Helmet Detection", "Helmet Detected", "High")
    alerts_page.add_alert("2025-04-27 17:05", 1, "Fire Detection", "Fire Detected", "Critical")
    alerts_page.add_alert("2025-04-27 17:10", 2, "Intrusion Detection", "Motion Detected", "Medium")

    alerts_page.show()
    sys.exit(app.exec_())
