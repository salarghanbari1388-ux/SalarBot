from datetime import datetime, timedelta


subscriptions = {}


def buy_subscription(user_id):
    expire_date = datetime.now() + timedelta(days=30)

    subscriptions[user_id] = {
        "vip": True,
        "expire": expire_date
    }

    return expire_date


def check_subscription(user_id):
    user = subscriptions.get(user_id)

    if not user:
        return False

    if datetime.now() < user["expire"]:
        return True

    return False


def subscription_info(user_id):
    user = subscriptions.get(user_id)

    if not user:
        return "❌ اشتراک فعال نداری."

    return (
        "⭐ اشتراک VIP فعال است\n"
        f"📅 پایان: {user['expire'].strftime('%Y-%m-%d')}"
  )
