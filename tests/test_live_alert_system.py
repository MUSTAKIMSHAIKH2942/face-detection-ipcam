# test_live_alert_system.py

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget

from ui.live_view import LiveView
from ui.alerts_management import AlertsManagement

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EyeQ Enterprise - Live System Test")
        self.setGeometry(100, 100, 1200, 800)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Create Pages
        self.live_view = LiveView()
        self.alerts_page = AlertsManagement()

        # Link LiveView → AlertsManagement
        self.live_view.set_alerts_page(self.alerts_page)

        # Add Tabs
        self.tabs.addTab(self.live_view, "Live View")
        self.tabs.addTab(self.alerts_page, "Alerts Management")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
