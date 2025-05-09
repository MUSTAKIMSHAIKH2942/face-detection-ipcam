# test_user_management.py (temporary)
import sys
from PyQt5.QtWidgets import QApplication
from ui.user_management import UserManagement

if __name__ == "__main__":
    app = QApplication(sys.argv)
    user_page = UserManagement()

    # Add dummy users
    user_page.add_user_entry("admin", "Admin", "2025-04-27 18:00")
    user_page.add_user_entry("operator1", "Operator", "2025-04-27 18:10")
    user_page.add_user_entry("operator2", "Operator", "2025-04-27 18:15")

    user_page.show()
    sys.exit(app.exec_())
