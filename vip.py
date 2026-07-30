from datetime import datetime

# ذخیره اطلاعات کاربران
users = {}


def is_vip(user_id):
    """بررسی می‌کند کاربر VIP است یا نه"""
    if user_id not in users:
        return False

    expire = users[user_id].get("vip_until")

    if expire is None:
        return False

    return expire > datetime.now()


def activate_vip(user_id, days=7):
    """فعال کردن VIP"""
    users.setdefault(user_id, {})
    users[user_id]["vip_until"] = datetime.now().replace(
        hour=23, minute=59, second=59
    )


def use_free_question(user_id):
    """۳ سؤال رایگان در روز"""
    today = datetime.now().strftime("%Y-%m-%d")

    users.setdefault(user_id, {})

    if users[user_id].get("date") != today:
        users[user_id]["date"] = today
        users[user_id]["count"] = 0

    if users[user_id]["count"] >= 3:
        return False

    users[user_id]["count"] += 1
    return True
