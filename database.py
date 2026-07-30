users = {}


def add_user(user_id, username):
    if user_id not in users:
        users[user_id] = {
            "username": username,
            "score": 0,
            "vip": False
        }


def get_user(user_id):
    return users.get(user_id)


def add_score(user_id, points):
    if user_id in users:
        users[user_id]["score"] += points
