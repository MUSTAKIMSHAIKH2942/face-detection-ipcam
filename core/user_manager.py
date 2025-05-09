"""
User Manager - Handles user authentication, creation, and role management securely.

Author: ItsOji Team
"""

import sqlite3
import bcrypt
from datetime import datetime

class UserManager:
    """Manages user accounts, authentication, and roles."""
    def __init__(self, db_path="eyeq_users.db"):
        """
        :param db_path: Path to the SQLite database file for users.
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.create_table()

    def create_table(self):
        """Create the users table if it does not exist."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password_hash TEXT,
                    role TEXT,
                    last_login TEXT
                )
            """)
            self.conn.commit()
            print("[UserManager] Users table ensured.")
        except Exception as e:
            print(f"[UserManager] Error creating table: {e}")

    def hash_password(self, password):
        """
        Hash a plaintext password securely.
        :param password: Plain password
        :return: Hashed password
        """
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    def add_user(self, username, password, role="user"):
        """
        Add a new user.
        :param username: Username string
        :param password: Plain password
        :param role: User role ('admin' or 'user')
        """
        try:
            password_hash = self.hash_password(password)
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO users (username, password_hash, role)
                VALUES (?, ?, ?)
            """, (username, password_hash, role))
            self.conn.commit()
            print(f"[UserManager] User added: {username} ({role})")
        except sqlite3.IntegrityError:
            print(f"[UserManager] Username already exists: {username}")
        except Exception as e:
            print(f"[UserManager] Error adding user: {e}")

    def authenticate_user(self, username, password):
        """
        Authenticate a user.
        :param username: Username
        :param password: Plain password
        :return: True if authentication successful, else False
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
            result = cursor.fetchone()
            if result:
                stored_hash = result[0]
                if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                    self.update_last_login(username)
                    return True
            return False
        except Exception as e:
            print(f"[UserManager] Error authenticating user: {e}")
            return False

    def update_last_login(self, username):
        """Update last login timestamp for a user."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE users SET last_login = ?
                WHERE username = ?
            """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), username))
            self.conn.commit()
        except Exception as e:
            print(f"[UserManager] Error updating last login: {e}")

    def get_user_role(self, username):
        """
        Get the role of a user.
        :param username: Username
        :return: Role string or None
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT role FROM users WHERE username = ?", (username,))
            result = cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"[UserManager] Error fetching user role: {e}")
            return None

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            print("[UserManager] Database connection closed.")
