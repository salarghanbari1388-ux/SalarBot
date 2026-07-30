from datetime import datetime, timedelta

users = {}


def add_user(user_id, username):
    if user_id not in users:
        users[user_id] = {
            "username": username,
            "score": 0,
            "games": 0,
            "vip": False,
            "vip_until": None,
            "free_questions": 3,
            "last_reset": datetime.now()
        }


def get_user(user_id):
    return users.get(user_id)


def add_score(user_id, points):
    if user_id in users:
        users[user_id]["score"] += points
        users[user_id]["games"] += 1


def get_score(user_id):
    if user_id in users:
        return users[user_id]["score"]

    return 0


def is_vip(user_id):
    user = get_user(user_id)

    if not user:
        return False

    if user["vip_until"]:
        if datetime.now() < user["vip_until"]:
            return True
        else:
            user["vip"] = False
            user["vip_until"] = None

    return False


def use_free_question(user_id):
    user = get_user(user_id)

    if not user:
        return False

    # ریست روزانه سهمیه
    if datetime.now() - user["last_reset"] >= timedelta(days=1):
        user["free_questions"] = 3
        user["last_reset"] = datetime.now()

    if user["free_questions"] > 0:
        user["free_questions"] -= 1
        return True

    return False


def activate_vip(user_id, days=7):
    user = get_user(user_id)

    if user:
        user["vip"] = True
        user["vip_until"] = datetime.now() + timedelta(days=days)
