from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem
)
from PyQt5.QtCore import Qt


class UserManagement(QWidget):
    """User management page."""
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Initialise the user management layout."""
        main_layout = QVBoxLayout()

        self.user_table = QTableWidget()
        self.user_table.setColumnCount(3)
        self.user_table.setHorizontalHeaderLabels(["Username", "Role", "Last Login"])
        self.user_table.horizontalHeader().setStretchLastSection(True)
        self.user_table.setSortingEnabled(True)

        main_layout.addWidget(self.user_table)

        btns_layout = QHBoxLayout()
        self.add_user_btn = QPushButton("Add User")
        self.edit_user_btn = QPushButton("Edit User")
        self.delete_user_btn = QPushButton("Delete User")

        btns_layout.addWidget(self.add_user_btn)
        btns_layout.addWidget(self.edit_user_btn)
        btns_layout.addWidget(self.delete_user_btn)

        main_layout.addLayout(btns_layout)
        self.setLayout(main_layout)

    def add_user_entry(self, username, role, last_login):
        row = self.user_table.rowCount()
        self.user_table.insertRow(row)

        for i, val in enumerate([username, role, last_login]):
            cell = QTableWidgetItem(val)
            cell.setTextAlignment(Qt.AlignCenter)
            self.user_table.setItem(row, i, cell)
