# test_system_settings.py (temporary)
import sys
from PyQt5.QtWidgets import QApplication
from ui.system_settings import SystemSettings

if __name__ == "__main__":
    app = QApplication(sys.argv)
    sys_settings = SystemSettings()
    sys_settings.show()
    sys.exit(app.exec_())
