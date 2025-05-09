from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QStackedWidget
)
from PyQt5.QtCore import Qt, QTimer
from ui.dashboard import Dashboard
from ui.live_view import LiveView
from ui.alerts_management import AlertsManagement
from ui.reports_analytics import ReportsAnalytics
from ui.administration import AdministrationPage
from ui.settings_dialog import SettingsDialog
from ui.help_docs import HelpDocsPage
from core.system_monitor import SystemMonitor

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ItsOji EyeQ Enterprise")
        self.setGeometry(100, 100, 1280, 720)

        # Initialize page references
        self.live_view_page = None
        self.dashboard_page = None
        self.alerts_page = None
        self.camera_labels = {}

        # 🔧 Add manager references
        self.camera_manager = None
        self.plugin_manager = None
        self.alert_manager = None

        # System monitor
        self.monitor = SystemMonitor()
        self.monitor_callback_timer = QTimer()
        self.monitor_callback_timer.timeout.connect(self.poll_system_health)
        self.monitor_callback_timer.start(5000)
        self.monitor.start()

        # Initialize buttons
        self.dashboard_btn = QPushButton("Dashboard")
        self.liveview_btn = QPushButton("Live View")
        self.alerts_btn = QPushButton("Alerts")
        self.reports_btn = QPushButton("Reports")
        self.admin_btn = QPushButton("Admin")
        self.settings_btn = QPushButton("Settings")
        self.help_btn = QPushButton("Help")

        # Set up the central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.init_topbar()
        self.init_main_area()
        self.connect_events()

        self.init_pages()  # ✅ Must come after main area

    def poll_system_health(self):
        try:
            cpu = self.monitor.get_cpu()
            ram = self.monitor.get_ram()
            if self.dashboard_page:
                self.dashboard_page.update_system_health(cpu, ram, len(self.camera_labels))
        except Exception as e:
            print(f"[MainWindow] ⚠️ Failed to update system health: {e}")

    def init_topbar(self):
        self.topbar = QHBoxLayout()
        for btn in [self.dashboard_btn, self.liveview_btn, self.alerts_btn,
                    self.reports_btn, self.admin_btn, self.settings_btn, self.help_btn]:
            btn.setFixedHeight(40)
            self.topbar.addWidget(btn)
        self.layout.addLayout(self.topbar)

    def init_main_area(self):
        self.main_area = QHBoxLayout()

        # Sidebar for navigation
        self.sidebar = QListWidget()
        sidebar_items = [
            "Camera Management",
            "Plugin Management",
            "Alert Management",
            "Reports & Analytics",
            "User Management",
            "System Settings"
        ]
        for item in sidebar_items:
            self.sidebar.addItem(item)
        self.sidebar.setFixedWidth(200)

        # Main area stack
        self.central_pages = QStackedWidget()

        # Add sidebar + central stack to layout
        self.main_area.addWidget(self.sidebar)
        self.main_area.addWidget(self.central_pages)
        self.layout.addLayout(self.main_area)

    def init_pages(self):
        self.default_page = QLabel("👁️ Welcome to EyeQ Enterprise System")
        self.default_page.setAlignment(Qt.AlignCenter)

        if not self.alerts_page:
            self.alerts_page = AlertsManagement()

        if not self.dashboard_page:
            self.dashboard_page = Dashboard(alerts_page=self.alerts_page)

        if not self.live_view_page:
            self.live_view_page = LiveView()
            print("[MainWindow] Created default LiveView page")

            # Inject managers into LiveView if already available
            if self.camera_manager:
                self.live_view_page.set_camera_manager(self.camera_manager)
            if self.plugin_manager:
                self.live_view_page.set_plugin_manager(self.plugin_manager)
            if self.alert_manager:
                self.live_view_page.set_alert_manager(self.alert_manager)

        if hasattr(self.live_view_page, 'set_alerts_page'):
            self.live_view_page.set_alerts_page(self.alerts_page)
        if hasattr(self.live_view_page, 'set_dashboard_page'):
            self.live_view_page.set_dashboard_page(self.dashboard_page)

        self.reports_page = ReportsAnalytics()
        self.admin_page = AdministrationPage()
        self.help_page = HelpDocsPage()

        # Clear any old pages before adding
        while self.central_pages.count():
            widget = self.central_pages.widget(0)
            self.central_pages.removeWidget(widget)
            widget.deleteLater()

        # Add all pages to the stack
        pages = [
            self.default_page,
            self.dashboard_page,
            self.live_view_page,
            self.alerts_page,
            self.reports_page,
            self.admin_page,
            self.help_page
        ]
        for page in pages:
            self.central_pages.addWidget(page)

        # ✅ Show live view by default on launch
        self.central_pages.setCurrentIndex(2)
        print("[MainWindow] ✅ LiveView is set as the initial page.")

        self.update_camera_labels_reference()

    def update_camera_labels_reference(self):
        if self.live_view_page and hasattr(self.live_view_page, 'get_camera_labels'):
            camera_labels = self.live_view_page.get_camera_labels()
            self.camera_labels = {
                idx: label for idx, (cam_id, label) in enumerate(camera_labels.items())
            }
            print(f"[MainWindow] LiveView camera labels count: {len(camera_labels)}")
            for cam_id, label in camera_labels.items():
                print(f" - {cam_id} label initialized")
        else:
            print("[MainWindow] ⚠️ live_view_page.camera_labels not initialized.")

    def connect_events(self):
        self.dashboard_btn.clicked.connect(lambda: self.central_pages.setCurrentIndex(1))
        self.liveview_btn.clicked.connect(lambda: self.central_pages.setCurrentIndex(2))
        self.alerts_btn.clicked.connect(lambda: self.central_pages.setCurrentIndex(3))
        self.reports_btn.clicked.connect(lambda: self.central_pages.setCurrentIndex(4))
        self.admin_btn.clicked.connect(lambda: self.central_pages.setCurrentIndex(5))
        self.help_btn.clicked.connect(lambda: self.central_pages.setCurrentIndex(6))
        self.settings_btn.clicked.connect(self.open_settings)
        self.sidebar.itemClicked.connect(self.handle_sidebar_click)

    def handle_sidebar_click(self, item):
        text = item.text()
        if "Camera" in text:
            self.central_pages.setCurrentIndex(2)
        elif "Plugin" in text:
            self.central_pages.setCurrentIndex(1)
        elif "Alert" in text:
            self.central_pages.setCurrentIndex(3)
        elif "Reports" in text:
            self.central_pages.setCurrentIndex(4)
        elif "User" in text:
            self.central_pages.setCurrentIndex(5)
        elif "System" in text:
            self.open_settings()

    def open_settings(self):
        dialog = SettingsDialog()
        dialog.exec_()

    def update_status(self, message):
        print(f"[MainWindow] STATUS: {message}")

    def set_dashboard_page(self, dashboard):
        self.dashboard_page = dashboard

    def set_liveview_page(self, live_view):
        self.live_view_page = live_view
        self.update_camera_labels_reference()

    def set_alerts_page(self, alerts_page):
        self.alerts_page = alerts_page

    def set_camera_manager(self, manager):
        self.camera_manager = manager
        if self.live_view_page:
            self.live_view_page.set_camera_manager(manager)

    def set_plugin_manager(self, manager):
        self.plugin_manager = manager
        if self.live_view_page:
            self.live_view_page.set_plugin_manager(manager)

    def set_alert_manager(self, manager):
        self.alert_manager = manager
        if self.live_view_page:
            self.live_view_page.set_alert_manager(manager)

    def show_liveview(self):
        if hasattr(self, 'central_pages'):
            self.central_pages.setCurrentIndex(2)
            print("[MainWindow] ✅ Live View page switched.")
        else:
            print("[MainWindow] ⚠️ central_pages not found.")
