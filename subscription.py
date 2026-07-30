from database import users


def activate_vip(user_id):
    if user_id in users:
        users[user_id]["vip"] = True


def is_vip(user_id):
    if user_id not in users:
        return False

    return users[user_id]["vip"]
