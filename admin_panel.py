# admin_panel.py - نسخه نهایی و بدون خطا

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler

# ========== تنظیمات ==========
ADMIN_ID = 8646600079  # آیدی عددی خودت - با @userinfobot بگیر

# ========== داده‌های موقت (برای تست) ==========
# اینا رو بعداً با دیتابیس واقعی جایگزین میکنیم
vip_requests = []  # لیست درخواست‌های VIP
support_messages = []  # لیست پیام‌های پشتیبانی
top_referrers_data = ["کاربر1: 10 دعوت", "کاربر2: 8 دعوت"]  # نمونه
current_prize = "۱۰۰,۰۰۰"  # جایزه فعلی
days_left = "۵"  # روز باقی‌مانده

# ==========================================

async def admin_panel(update, context):
    """نمایش پنل مدیریت با دکمه‌ها"""
    # بررسی دسترسی
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ شما دسترسی به این بخش ندارید.")
        return

    keyboard = [
        [InlineKeyboardButton("📊 آمار کلی", callback_data="stats")],
        [InlineKeyboardButton("👑 درخواست‌های VIP", callback_data="vip")],
        [InlineKeyboardButton("🎧 پیام‌های پشتیبانی", callback_data="support")],
        [InlineKeyboardButton("🎁 برترین دعوت‌کننده‌ها", callback_data="refs")],
        [InlineKeyboardButton("🏆 اطلاعات جایزه", callback_data="reward")]
    ]

    await update.message.reply_text(
        "👑 **پنل مدیریت SalarBot**\n\n"
        "یکی از گزینه‌های زیر را انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


async def admin_buttons(update, context):
    """پردازش کلیک روی دکمه‌های پنل ادمین"""
    query = update.callback_query
    await query.answer()  # پاسخ به تلگرام برای جلوگیری از خطای timeout

    # بررسی دسترسی
    if query.from_user.id != ADMIN_ID:
        await query.edit_message_text("⛔ شما دسترسی به این بخش ندارید.")
        return

    # پردازش هر دکمه
    if query.data == "stats":
        text = (
            "📊 **آمار کلی ربات**\n\n"
            "👥 تعداد کل کاربران: **۰** (در انتظار اتصال دیتابیس)\n"
            "🎯 معماهای حل‌شده: **۰**\n"
            "⭐ کاربران VIP: **۰**\n"
            "📅 کاربران فعال امروز: **۰**"
        )
        await query.edit_message_text(text, parse_mode="Markdown")

    elif query.data == "vip":
        if not vip_requests:
            await query.edit_message_text("👑 هیچ درخواست VIP جدیدی وجود ندارد.")
        else:
            text = "👑 **لیست درخواست‌های VIP:**\n\n"
            for i, req in enumerate(vip_requests, 1):
                text += f"{i}) کاربر `{req['user_id']}` - وضعیت: {req.get('status', 'در انتظار')}\n"
            await query.edit_message_text(text, parse_mode="Markdown")

    elif query.data == "support":
        if not support_messages:
            await query.edit_message_text("🎧 هیچ پیام پشتیبانی جدیدی وجود ندارد.")
        else:
            text = f"🎧 **پیام‌های پشتیبانی:** {len(support_messages)} عدد\n\n"
            for i, msg in enumerate(support_messages[:5], 1):  # فقط ۵ تا آخرین
                text += f"{i}) کاربر `{msg['user_id']}`: {msg['text'][:30]}...\n"
            await query.edit_message_text(text, parse_mode="Markdown")

    elif query.data == "refs":
        if not top_referrers_data:
            await query.edit_message_text("🎁 هنوز هیچ دعوتی ثبت نشده.")
        else:
            text = "🎁 **برترین دعوت‌کننده‌ها:**\n\n"
            for i, user in enumerate(top_referrers_data[:5], 1):
                text += f"{i}) {user}\n"
            await query.edit_message_text(text)

    elif query.data == "reward":
        text = (
            "🏆 **مسابقه و جایزه**\n\n"
            f"💰 جایزه فعلی: **{current_prize}** تومان\n"
            f"⏳ زمان باقی‌مانده: **{days_left}** روز\n\n"
            "برای برنده شدن، بیشترین امتیاز را در این دوره کسب کنید!"
        )
        await query.edit_message_text(text, parse_mode="Markdown")


def setup_admin(app):
    """ثبت هندلرهای ادمین در برنامه اصلی"""
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CallbackQueryHandler(admin_buttons))
