from database import get_user

def profile_text(user_id):
    user = get_user(user_id)
    if user is None:
        return "❌ هنوز پروفایلی ساخته نشده."
    
    from vip_manager import is_vip
    vip_status = "⭐ فعال" if is_vip(user_id) else "❌ ندارد"
    
    return (
        "👤 پروفایل بازیکن\n\n"
        f"🆔 نام: {user['username']}\n"
        f"🏆 امتیاز: {user['score']}\n"
        f"🎮 تعداد بازی: {user['games']}\n"
        f"💎 VIP: {vip_status}"
    )
