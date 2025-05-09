import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from PyQt5.QtWidgets import QApplication
from ui.settings_dialog import SettingsDialog

app = QApplication(sys.argv)

class TestSettingsDialogCamera(unittest.TestCase):
    def setUp(self):
        self.dialog = SettingsDialog()
        self.dialog.camera_list.clear()
        self.dialog.settings["camera_sources"] = []


    def test_add_camera_source_with_all_fields(self):
        self.dialog.camera_label_edit.setText("Cam 1")
        self.dialog.camera_url_edit.setText("rtsp://192.168.1.101/live")
        self.dialog.camera_user_edit.setText("admin")
        self.dialog.camera_pass_edit.setText("12345")
        self.dialog.add_camera_source()
        self.assertEqual(self.dialog.camera_list.count(), 1)
        self.assertIn("Cam 1", self.dialog.camera_list.item(0).text())

    def test_add_camera_source_without_credentials(self):
        self.dialog.camera_label_edit.setText("Cam 2")
        self.dialog.camera_url_edit.setText("rtsp://192.168.1.102/live")
        self.dialog.camera_user_edit.setText("")
        self.dialog.camera_pass_edit.setText("")
        self.dialog.add_camera_source()
        self.assertEqual(self.dialog.camera_list.count(), 1)
        self.assertIn("Cam 2", self.dialog.camera_list.item(0).text())

    def test_reject_duplicate_camera_source(self):
        self.dialog.camera_label_edit.setText("Cam 1")
        self.dialog.camera_url_edit.setText("rtsp://192.168.1.101/live")
        self.dialog.camera_user_edit.setText("admin")
        self.dialog.camera_pass_edit.setText("12345")
        self.dialog.add_camera_source()
        self.dialog.add_camera_source()  # Duplicate
        self.assertEqual(self.dialog.camera_list.count(), 1)

    def test_remove_camera_source(self):
        self.dialog.camera_label_edit.setText("Cam 3")
        self.dialog.camera_url_edit.setText("rtsp://192.168.1.103/live")
        self.dialog.add_camera_source()
        self.dialog.camera_list.setCurrentRow(0)
        self.dialog.remove_camera_source()
        self.assertEqual(self.dialog.camera_list.count(), 0)

    def tearDown(self):
        self.dialog.close()

if __name__ == "__main__":
    unittest.main()
