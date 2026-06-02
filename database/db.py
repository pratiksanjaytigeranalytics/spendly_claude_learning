import sqlite3
from werkzeug.security import generate_password_hash

DATABASE_PATH = "spendly.db"

def get_db():
    """
    Opens a connection to the SQLite database.
    Sets row_factory to sqlite3.Row and enables foreign key enforcement.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    """
    Creates the users and expenses tables if they do not already exist.
    """
    with get_db() as conn:
        # Create users table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)

        # Create expenses table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                description TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        conn.commit()

def create_user(name, email, password):
    """
    Hashes the password and inserts a new user into the database.
    Returns the ID of the created user.
    Raises sqlite3.IntegrityError if the email is already taken.
    """
    password_hash = generate_password_hash(password)
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, password_hash)
        )
        conn.commit()
        return cursor.lastrowid

def seed_db():

    """
    Seeds the database with a demo user and sample expenses if the database is empty.
    """
    with get_db() as conn:
        # Check if users table has data
        user_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        if user_count > 0:
            return

        # Insert demo user
        demo_user = {
            "name": "Demo User",
            "email": "demo@spendly.com",
            "password": generate_password_hash("demo123")
        }

        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (demo_user["name"], demo_user["email"], demo_user["password"])
        )
        user_id = cursor.lastrowid

        # Sample expenses covering all categories
        # Using a realistic date range for the current month (simulated as 2026-06)
        expenses = [
            (user_id, 12.50, "Food", "2026-06-01", "Lunch at Cafe"),
            (user_id, 45.00, "Transport", "2026-06-02", "Fuel refill"),
            (user_id, 120.00, "Bills", "2026-06-03", "Electricity bill"),
            (user_id, 60.00, "Health", "2026-06-05", "Pharmacy"),
            (user_id, 25.00, "Entertainment", "2026-06-07", "Cinema ticket"),
            (user_id, 89.99, "Shopping", "2026-06-10", "New headphones"),
            (user_id, 15.00, "Other", "2026-06-12", "Parking fee"),
            (user_id, 30.00, "Food", "2026-06-15", "Dinner party"),
        ]

        conn.executemany(
            "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
            expenses
        )
        conn.commit()
