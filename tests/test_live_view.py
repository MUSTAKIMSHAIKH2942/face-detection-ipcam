# test_live_view.py
import sys
from PyQt5.QtWidgets import QApplication
from ui.live_view import LiveView

if __name__ == "__main__":
    app = QApplication(sys.argv)
    view = LiveView()
    view.show()
    sys.exit(app.exec_())
