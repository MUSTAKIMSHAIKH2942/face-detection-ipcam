# tests/test_main_window.py

import unittest
import sys
import os
from PyQt5.QtWidgets import QApplication
sys.path.append(os.path.abspath("."))

from ui.main_window import MainWindow

class TestMainWindow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication(sys.argv)

    def test_window_creation(self):
        """Test if MainWindow initializes without error."""
        window = MainWindow()
        self.assertIsNotNone(window)
        self.assertEqual(window.windowTitle(), "ItsOji EyeQ Enterprise")

if __name__ == "__main__":
    unittest.main()
