import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))



# test_user_manager.py (temporary)
from core.user_manager import UserManager

if __name__ == "__main__":
    user_mgr = UserManager()

    # Add a new user (only once)
    user_mgr.add_user("admin", "admin123", role="admin")

    # Authenticate login
    if user_mgr.authenticate_user("admin", "admin123"):
        print("Login successful!")
    else:
        print("Login failed.")

    # Check user role
    role = user_mgr.get_user_role("admin")
    print(f"User Role: {role}")

    # Clean close
    user_mgr.close()
