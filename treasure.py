import random


treasures = [
    {"name": "🪙 ۱۰ سکه", "coins": 10},
    {"name": "🪙 ۵۰ سکه", "coins": 50},
    {"name": "💎 گنج کوچک", "coins": 100},
    {"name": "❌ صندوق خالی", "coins": 0},
    {"name": "👑 گنج افسانه‌ای", "coins": 500}
]


def open_treasure():
    return random.choice(treasures)
