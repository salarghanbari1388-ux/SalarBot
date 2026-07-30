import sqlite3

conn = sqlite3.connect("data.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    coins INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    vip INTEGER DEFAULT 0
)
""")

conn.commit()
conn.close()
