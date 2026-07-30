from database import get_user


def profile_text(user_id):
    user = get_user(user_id)

    if user is None:
        return "کاربر پیدا نشد."

    vip = "⭐ دارد" if user["vip"] else "❌ ندارد"

    return (
        f"👤 نام: {user['username']}\n"
        f"🏆 امتیاز: {user['score']}\n"
        f"💎 VIP: {vip}"
    )
