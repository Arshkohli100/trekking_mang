import sqlite3
from werkzeug.security import generate_password_hash

DB = 'trekking.db'

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        status TEXT DEFAULT 'active'
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS treks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        location TEXT NOT NULL,
        difficulty TEXT NOT NULL,
        duration INTEGER NOT NULL,
        slots INTEGER NOT NULL,
        staff_id INTEGER,
        status TEXT DEFAULT 'Pending',
        start_date TEXT,
        end_date TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        trek_id INTEGER NOT NULL,
        booking_date TEXT DEFAULT (date('now')),
        status TEXT DEFAULT 'Booked'
    )''')

    c.execute("SELECT id FROM users WHERE role='admin'")
    if not c.fetchone():
        c.execute("INSERT INTO users (name, email, password, role, status) VALUES (?, ?, ?, ?, ?)",
                  ('Admin', 'admin@trek.com', generate_password_hash('admin123'), 'admin', 'active'))

    conn.commit()
    conn.close()
