# test_settings_dialog.py (temporary)
import sys
from PyQt5.QtWidgets import QApplication
from ui.settings_dialog import SettingsDialog

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dlg = SettingsDialog()
    dlg.exec_()
