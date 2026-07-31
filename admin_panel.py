# admin_panel.py - نسخه نهایی و بدون خطا

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler

ADMIN_ID = 8646600079  # آیدی عددی خودت - با @userinfobot بگیر

# داده‌های نمونه (بعداً با دیتابیس جایگزین میشه)
vip_requests = []
support_messages = []
top_referrers_data = ["کاربر1: 10 دعوت", "کاربر2: 8 دعوت"]
current_prize = "۱۰۰,۰۰۰"
days_left = "۵"

async def admin_panel(update, context):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ شما دسترسی ندارید.")
        return

    keyboard = [
        [InlineKeyboardButton("📊 آمار کلی", callback_data="stats")],
        [InlineKeyboardButton("👑 درخواست‌های VIP", callback_data="vip")],
        [InlineKeyboardButton("🎧 پیام‌های پشتیبانی", callback_data="support")],
        [InlineKeyboardButton("🎁 برترین دعوت‌کننده‌ها", callback_data="refs")],
        [InlineKeyboardButton("🏆 اطلاعات جایزه", callback_data="reward")]
    ]
    await update.message.reply_text(
        "👑 **پنل مدیریت**",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def admin_buttons(update, context):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        await query.edit_message_text("⛔ شما دسترسی ندارید.")
        return

    if query.data == "stats":
        await query.edit_message_text("📊 آمار کلی: در حال توسعه")
    elif query.data == "vip":
        if not vip_requests:
            await query.edit_message_text("👑 درخواست VIP وجود ندارد.")
        else:
            text = "👑 درخواست‌های VIP:\n\n"
            for i, r in enumerate(vip_requests, 1):
                text += f"{i}) کاربر {r['user_id']} - {r.get('status', 'در انتظار')}\n"
            await query.edit_message_text(text)
    elif query.data == "support":
        await query.edit_message_text(f"🎧 پیام‌های پشتیبانی: {len(support_messages)}")
    elif query.data == "refs":
        top = top_referrers_data[:5] if top_referrers_data else ["هیچ داده‌ای نیست"]
        await query.edit_message_text(f"🎁 برترین دعوت‌کننده‌ها:\n{chr(10).join(top)}")
    elif query.data == "reward":
        await query.edit_message_text(
            f"🏆 جایزه\n\n💰 {current_prize} تومان\n⏳ {days_left} روز باقی‌مانده"
        )

def setup_admin(app):
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CallbackQueryHandler(admin_buttons))
