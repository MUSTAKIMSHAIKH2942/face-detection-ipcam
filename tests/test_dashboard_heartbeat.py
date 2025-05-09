import unittest
from PyQt5.QtWidgets import QApplication
from ui.dashboard import Dashboard
from datetime import datetime, timedelta

# Required to initialize the Qt Application for widget testing
app = QApplication([])

class TestDashboardHeartbeat(unittest.TestCase):

    def setUp(self):
        self.dashboard = Dashboard()

    def test_initial_heartbeat_state(self):
        """Test that the initial heartbeat label is set correctly."""
        self.assertEqual(self.dashboard.heartbeat_label.text(), "Last Heartbeat: --")

    def test_update_heartbeat_display(self):
        """Test updating heartbeat with a timestamp updates the label text."""
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.dashboard.update_heartbeat(ts)
        self.assertIn("Last Heartbeat:", self.dashboard.heartbeat_label.text())
        self.assertIn(ts, self.dashboard.heartbeat_label.text())

    def test_heartbeat_color_status(self):
        """Test that label color updates according to heartbeat freshness."""
        now = datetime.now()

        # Case 1: Fresh heartbeat (< 60s)
        self.dashboard.last_heartbeat_time = now
        self.dashboard.check_heartbeat_status()
        self.assertIn("green", self.dashboard.heartbeat_label.styleSheet())

        # Case 2: Delayed heartbeat (60–120s)
        self.dashboard.last_heartbeat_time = now - timedelta(seconds=90)
        self.dashboard.check_heartbeat_status()
        self.assertIn("orange", self.dashboard.heartbeat_label.styleSheet())

        # Case 3: Stale heartbeat (> 120s)
        self.dashboard.last_heartbeat_time = now - timedelta(seconds=130)
        self.dashboard.check_heartbeat_status()
        self.assertIn("red", self.dashboard.heartbeat_label.styleSheet())

if __name__ == '__main__':
    unittest.main()
