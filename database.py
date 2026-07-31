from datetime import datetime

users = {}

def add_user(user_id, username):
    if user_id not in users:
        users[user_id] = {
            "username": username,
            "score": 0,
            "games": 0,
            "joined": datetime.now()
        }

def get_user(user_id):
    return users.get(user_id)

def add_score(user_id, points):
    if user_id in users:
        users[user_id]["score"] += points
        users[user_id]["games"] += 1

def get_score(user_id):
    user = get_user(user_id)
    return user["score"] if user else 0
