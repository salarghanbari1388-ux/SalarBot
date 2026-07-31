import os
import sys
import threading
import asyncio
from flask import Flask, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# ========== تنظیمات ==========
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    print("❌ BOT_TOKEN تنظیم نشده!")
    sys.exit(1)

ADMIN_ID = 8646600079  # آیدی عددی خودت

# ========== داده‌های نمونه (جایگزین ماژول‌ها) ==========
def main_menu():
    keyboard = [
        ["🎮 شروع بازی"],
        ["👤 پروفایل", "🏆 رتبه‌بندی"],
        ["⭐ VIP", "🎁 دعوت دوستان"],
        ["🎧 پشتیبانی"]
    ]
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(text, callback_data=text)] for row in keyboard for text in row]
    )

def register_user(user_id, username):
    # ذخیره کاربر در دیتابیس (الان فقط چاپ می‌کنیم)
    print(f"👤 کاربر جدید: {user_id} - {username}")
    return True

def profile_text(user_id):
    return f"👤 پروفایل شما\n\nشناسه: {user_id}\nامتیاز: ۰\nVIP: خیر"

def ranking_text():
    return "🏆 رتبه‌بندی:\n1. کاربر نمونه (۱۰۰ امتیاز)"

def get_riddle():
    return {"question": "چه چیزی همیشه جلو شماست ولی نمی‌تونید ببینیدش؟", "answer": "آینده"}

def save_answer(user_id, answer):
    print(f"📝 پاسخ برای {user_id} ذخیره شد: {answer}")

def check_answer(user_id, text):
    return text.strip().lower() == "آینده"

def open_treasure(user_id):
    return 10  # امتیاز

def is_vip(user_id):
    return False

def use_free_question(user_id):
    return True

def add_vip_request(user_id, photo_id):
    print(f"📸 درخواست VIP از {user_id} با عکس {photo_id}")

def add_referral(user_id, inviter_id):
    print(f"🔗 کاربر {user_id} توسط {inviter_id} دعوت شد")

def get_referrals(user_id):
    return 0

def referral_link(user_id):
    return f"https://t.me/YourBot?start={user_id}"

def add_support_message(user_id, text):
    print(f"🎧 پیام پشتیبانی از {user_id}: {text}")

# ========== سرور Flask ==========
flask_app = Flask(__name__)

@flask_app.route('/')
@flask_app.route('/health')
def health():
    return jsonify({"status": "ok"}), 200

def run_flask():
    port = int(os.getenv("PORT", 8080))
    flask_app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# ========== پنل ادمین ==========
vip_requests = []
support_messages = []
top_referrers = ["کاربر1: ۱۰ دعوت", "کاربر2: ۸ دعوت"]
current_prize = "۱۰۰,۰۰۰"
days_left = "۵"

async def admin_panel(update, context):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ شما دسترسی ندارید.")
        return
    keyboard = [
        [InlineKeyboardButton("📊 آمار", callback_data="stats")],
        [InlineKeyboardButton("👑 VIP", callback_data="vip")],
        [InlineKeyboardButton("🎧 پشتیبانی", callback_data="support")],
        [InlineKeyboardButton("🎁 دعوت‌ها", callback_data="refs")],
        [InlineKeyboardButton("🏆 جایزه", callback_data="reward")]
    ]
    await update.message.reply_text(
        "👑 پنل مدیریت",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def admin_buttons(update, context):
    query = update.callback_query
    await query.answer()
    if query.from_user.id != ADMIN_ID:
        await query.edit_message_text("⛔ شما دسترسی ندارید.")
        return
    if query.data == "stats":
        await query.edit_message_text("📊 آمار: در حال توسعه")
    elif query.data == "vip":
        await query.edit_message_text("👑 درخواست VIP: هیچ")
    elif query.data == "support":
        await query.edit_message_text("🎧 پیام‌ها: ۰")
    elif query.data == "refs":
        await query.edit_message_text("🎁 برترین دعوت‌کننده‌ها:\n" + "\n".join(top_referrers))
    elif query.data == "reward":
        await query.edit_message_text(f"🏆 جایزه: {current_prize} تومان - {days_left} روز باقی‌مانده")

# ========== توابع اصلی ربات ==========
async def start(update, context):
    user = update.effective_user
    register_user(user.id, user.username or user.first_name)
    if context.args:
        try:
            inviter_id = int(context.args[0])
            add_referral(user.id, inviter_id)
        except:
            pass
    await update.message.reply_text(
        "🏺 به بازی شکار گنج خوش آمدی!",
        reply_markup=main_menu()
    )

async def text_handler(update, context):
    text = update.message.text
    user_id = update.effective_user.id

    if text == "🎮 شروع بازی":
        if not is_vip(user_id) and not use_free_question(user_id):
            await update.message.reply_text("⛔ سهمیه رایگان تمام شد.")
            return
        riddle = get_riddle()
        save_answer(user_id, riddle["answer"])
        await update.message.reply_text(f"🧩 معما:\n\n{riddle['question']}")
    elif text == "👤 پروفایل":
        await update.message.reply_text(profile_text(user_id))
    elif text == "🏆 رتبه‌بندی":
        await update.message.reply_text(ranking_text())
    elif text == "⭐ VIP":
        context.user_data["vip_request"] = True
        await update.message.reply_text(
            "👑 خرید VIP\n💰 مبلغ: ۴۰ هزار تومان\n💳 شماره کارت: 6219-8614-5120-3524"
        )
    elif text == "🎁 دعوت دوستان":
        link = referral_link(user_id)
        count = get_referrals(user_id)
        await update.message.reply_text(f"🔗 لینک دعوت:\n{link}\n👥 دعوت‌ها: {count}")
    elif text == "🎧 پشتیبانی":
        context.user_data["support"] = True
        await update.message.reply_text("🎧 پیام خود را ارسال کنید.")
    elif context.user_data.get("support"):
        add_support_message(user_id, text)
        await update.message.reply_text("✅ پیام ارسال شد.")
        context.user_data["support"] = False
    else:
        if check_answer(user_id, text):
            reward = open_treasure(user_id)
            await update.message.reply_text(f"🎉 درست! +{reward} امتیاز")
        else:
            await update.message.reply_text("❌ غلط، دوباره تلاش کن.")

async def photo_handler(update, context):
    if context.user_data.get("vip_request"):
        photo = update.message.photo[-1].file_id
        add_vip_request(update.effective_user.id, photo)
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=photo,
            caption=f"رسید VIP از {update.effective_user.id}"
        )
        await update.message.reply_text("✅ رسید دریافت شد.")
        context.user_data["vip_request"] = False

# ========== تابع اصلی ==========
async def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    application.add_handler(CommandHandler("admin", admin_panel))
    application.add_handler(CallbackQueryHandler(admin_buttons))

    # پاک‌سازی Webhook
    try:
        await application.bot.delete_webhook(drop_pending_updates=True)
        print("✅ Webhook پاک شد")
    except Exception as e:
        print(f"⚠️ خطا: {e}")

    # اجرای Flask در ترد جداگانه
    threading.Thread(target=run_flask, daemon=True).start()
    print(f"🚀 سرور روی پورت {os.getenv('PORT', 8080)} راه افتاد.")

    # شروع Polling
    print("🤖 ربات شروع به کار کرد...")
    await application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    asyncio.run(main())
