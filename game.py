import sqlite3

def register_user(user_id, username):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT OR IGNORE INTO users(user_id, username) VALUES(?, ?)",
        (user_id, username)
    )

    conn.commit()
    conn.close()


def get_user(user_id):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE user_id=?",
        (user_id,)
    )

    user = cursor.fetchone()

    conn.close()

    return user
