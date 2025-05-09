# test_reports_analytics.py (temporary)
import sys
from PyQt5.QtWidgets import QApplication
from ui.reports_analytics import ReportsAnalytics

if __name__ == "__main__":
    app = QApplication(sys.argv)
    reports_page = ReportsAnalytics()

    # Add dummy report entries
    reports_page.add_report("2025-04-27 17:30", 0, "Helmet Detection", "Helmet Detected", "High")
    reports_page.add_report("2025-04-27 17:35", 1, "Fire Detection", "Fire Detected", "Critical")
    reports_page.add_report("2025-04-27 17:40", 2, "Intrusion Detection", "Motion Detected", "Medium")

    reports_page.show()
    sys.exit(app.exec_())
