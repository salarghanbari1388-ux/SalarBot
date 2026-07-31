import sqlite3
import datetime
from contextlib import contextmanager
from config import DEFAULT_SETTINGS

DB_PATH = "bot_data.db"

def init_db():
    with get_connection() as conn:
        # جدول کاربران
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE,
                username TEXT,
                full_name TEXT,
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                vip_expiry TIMESTAMP NULL,
                score INTEGER DEFAULT 0,
                invited_count INTEGER DEFAULT 0,
                total_questions_answered INTEGER DEFAULT 0
            )
        """)
        # جدول سوالات روزانه
        conn.execute("""
            CREATE TABLE IF NOT EXISTS daily_questions (
                user_id INTEGER,
                date TEXT,
                questions_answered INTEGER DEFAULT 0,
                FOREIGN KEY(user_id) REFERENCES users(id),
                UNIQUE(user_id, date)
            )
        """)
        # جدول پرداخت‌ها
        conn.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                amount INTEGER,
                receipt_photo_id TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)
        # جدول اطلاعیه‌ها
        conn.execute("""
            CREATE TABLE IF NOT EXISTS announcements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # جدول تیکت‌های پشتیبانی
        conn.execute("""
            CREATE TABLE IF NOT EXISTS support_tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                question TEXT,
                answer TEXT,
                status TEXT DEFAULT 'open',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)
        # جدول تنظیمات
        conn.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        # درج تنظیمات پیش‌فرض
        for key, value in DEFAULT_SETTINGS.items():
            conn.execute(
                "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
                (key, value)
            )
        conn.commit()

@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

# ---------- کاربر ----------
def get_or_create_user(telegram_id, username=None, full_name=None):
    with get_connection() as conn:
        cur = conn.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
        user = cur.fetchone()
        if not user:
            conn.execute(
                "INSERT INTO users (telegram_id, username, full_name) VALUES (?, ?, ?)",
                (telegram_id, username, full_name)
            )
            conn.commit()
            return get_or_create_user(telegram_id)
        return dict(user)

def get_user_by_id(user_id):
    with get_connection() as conn:
        cur = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        return dict(cur.fetchone()) if cur.rowcount else None

def get_user_by_telegram_id(tg_id):
    with get_connection() as conn:
        cur = conn.execute("SELECT * FROM users WHERE telegram_id = ?", (tg_id,))
        return dict(cur.fetchone()) if cur.rowcount else None

def update_user_score(user_id, points):
    with get_connection() as conn:
        conn.execute("UPDATE users SET score = score + ? WHERE id = ?", (points, user_id))
        conn.commit()

def set_vip(user_id, expiry_date):
    with get_connection() as conn:
        conn.execute("UPDATE users SET vip_expiry = ? WHERE id = ?", (expiry_date, user_id))
        conn.commit()

def increment_invite_count(user_id):
    with get_connection() as conn:
        conn.execute("UPDATE users SET invited_count = invited_count + 1 WHERE id = ?", (user_id,))
        conn.commit()

def get_total_users_count():
    with get_connection() as conn:
        cur = conn.execute("SELECT COUNT(*) FROM users")
        return cur.fetchone()[0]

def get_all_users():
    with get_connection() as conn:
        cur = conn.execute("SELECT telegram_id FROM users")
        return [row[0] for row in cur.fetchall()]

# ---------- سوالات روزانه ----------
def get_today_question_count(user_id):
    today = datetime.date.today().isoformat()
    with get_connection() as conn:
        cur = conn.execute(
            "SELECT questions_answered FROM daily_questions WHERE user_id = ? AND date = ?",
            (user_id, today)
        )
        row = cur.fetchone()
        return row[0] if row else 0

def increment_daily_question(user_id):
    today = datetime.date.today().isoformat()
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO daily_questions (user_id, date, questions_answered) VALUES (?, ?, 1) "
            "ON CONFLICT(user_id, date) DO UPDATE SET questions_answered = questions_answered + 1",
            (user_id, today)
        )
        conn.commit()

# ---------- پرداخت ----------
def create_payment(user_id, amount, receipt_photo_id):
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO payments (user_id, amount, receipt_photo_id) VALUES (?, ?, ?)",
            (user_id, amount, receipt_photo_id)
        )
        conn.commit()
        return cur.lastrowid

def get_pending_payments():
    with get_connection() as conn:
        cur = conn.execute(
            "SELECT p.*, u.telegram_id, u.username FROM payments p "
            "JOIN users u ON p.user_id = u.id WHERE p.status = 'pending'"
        )
        return [dict(row) for row in cur.fetchall()]

def update_payment_status(payment_id, status):
    with get_connection() as conn:
        conn.execute("UPDATE payments SET status = ? WHERE id = ?", (status, payment_id))
        conn.commit()

# ---------- اطلاعیه ----------
def add_announcement(text):
    with get_connection() as conn:
        conn.execute("INSERT INTO announcements (text) VALUES (?)", (text,))
        conn.commit()

def get_latest_announcements(limit=5):
    with get_connection() as conn:
        cur = conn.execute(
            "SELECT * FROM announcements ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )
        return [dict(row) for row in cur.fetchall()]

# ---------- تیکت پشتیبانی ----------
def create_support_ticket(user_id, question):
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO support_tickets (user_id, question) VALUES (?, ?)",
            (user_id, question)
        )
        conn.commit()
        return cur.lastrowid

def get_open_tickets():
    with get_connection() as conn:
        cur = conn.execute(
            "SELECT t.*, u.telegram_id, u.username FROM support_tickets t "
            "JOIN users u ON t.user_id = u.id WHERE t.status = 'open'"
        )
        return [dict(row) for row in cur.fetchall()]

def answer_ticket(ticket_id, answer):
    with get_connection() as conn:
        conn.execute(
            "UPDATE support_tickets SET answer = ?, status = 'closed' WHERE id = ?",
            (answer, ticket_id)
        )
        conn.commit()

# ---------- تنظیمات ----------
def get_setting(key):
    with get_connection() as conn:
        cur = conn.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cur.fetchone()
        return row[0] if row else None

def set_setting(key, value):
    with get_connection() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            (key, value)
        )
        conn.commit()

def get_all_settings():
    with get_connection() as conn:
        cur = conn.execute("SELECT key, value FROM settings")
        return {row[0]: row[1] for row in cur.fetchall()}
