import os
import threading
from flask import Flask, jsonify
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from menu import main_menu
from game import register_user
from profile import profile_text
from ranking import ranking_text
from riddles import get_riddle
from answers import save_answer, check_answer
from treasure import open_treasure
from vip import (
    is_vip,
    use_free_question,
    add_vip_request
)
from referrals import (
    add_referral,
    get_referrals,
    referral_link
)
from support import add_support_message
from admin_panel import setup_admin

# ========== تنظیمات اولیه ==========
TOKEN = os.getenv("BOT_TOKEN")
BOT_USERNAME = "SalarPlay137Bot"
ADMIN_ID = 8646600079

if not TOKEN:
    raise ValueError("BOT_TOKEN تنظیم نشده!")

# ========== سرور Flask برای Health Check ==========
flask_app = Flask(__name__)

@flask_app.route('/')
@flask_app.route('/health')
def health_check():
    return jsonify({"status": "ok"}), 200

def run_flask():
    port = int(os.getenv("PORT", 8080))
    flask_app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# ==========================================

# ========== توابع ربات (بدون تغییر) ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    register_user(
        user.id,
        user.username or user.first_name
    )

    if context.args:
        try:
            inviter_id = int(context.args[0])
            add_referral(user.id, inviter_id)
        except ValueError:
            pass

    await update.message.reply_text(
        "🏺 به بازی شکار گنج خوش آمدی!",
        reply_markup=main_menu()
    )


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    if text == "🎮 شروع بازی":
        if not is_vip(user_id):
            if not use_free_question(user_id):
                await update.message.reply_text(
                    "⛔ سهمیه رایگان امروزت تمام شده.\n\n"
                    "⭐ برای ادامه بازی VIP بگیر."
                )
                return

        riddle = get_riddle()
        save_answer(user_id, riddle["answer"])

        await update.message.reply_text(
            f"🧩 معما:\n\n{riddle['question']}\n\nجوابت رو بفرست."
        )

    elif text == "👤 پروفایل":
        await update.message.reply_text(profile_text(user_id))

    elif text == "🏆 رتبه‌بندی":
        await update.message.reply_text(ranking_text())

    elif text == "⭐ VIP":
        context.user_data["vip_request"] = True
        await update.message.reply_text(
            "👑 خرید VIP\n\n"
            "💰 مبلغ: ۴۰ هزار تومان\n\n"
            "💳 شماره کارت:\n"
            "6219-8614-5120-3524\n\n"
            "بعد از پرداخت عکس رسید را ارسال کن."
        )

    elif text == "🎁 دعوت دوستان":
        link = referral_link(user_id)
        count = get_referrals(user_id)
        await update.message.reply_text(
            f"🎁 دعوت دوستان\n\n"
            f"🔗 لینک تو:\n{link}\n\n"
            f"👥 دعوت موفق: {count}"
        )

    elif text == "🎧 پشتیبانی":
        context.user_data["support"] = True
        await update.message.reply_text("🎧 پیام خود را ارسال کنید.")

    elif context.user_data.get("support"):
        add_support_message(user_id, text)
        await update.message.reply_text("✅ پیام شما برای پشتیبانی ارسال شد.")
        context.user_data["support"] = False

    else:
        if check_answer(user_id, text):
            reward = open_treasure(user_id)
            await update.message.reply_text(
                f"🎉 جواب درست بود!\n🎁 {reward} امتیاز گرفتی."
            )
        else:
            await update.message.reply_text("❌ جواب درست نیست، دوباره تلاش کن.")


async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("vip_request"):
        photo = update.message.photo[-1].file_id
        add_vip_request(update.effective_user.id, photo)

        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=photo,
            caption=(
                "💳 رسید VIP جدید\n\n"
                f"👤 کاربر: {update.effective_user.id}\n"
                "⏳ منتظر بررسی"
            )
        )

        await update.message.reply_text(
            "✅ رسید دریافت شد.\n⏳ منتظر تایید ادمین باشید."
        )
        context.user_data["vip_request"] = False

# ==========================================

# ========== تابع اصلی ==========
def main():
    # ساخت اپلیکیشن
    application = Application.builder().token(TOKEN).build()

    # اضافه کردن هندلرها
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    setup_admin(application)

    # حذف webhook قبلی (اگر وجود داشته باشد)
    application.bot.delete_webhook(drop_pending_updates=True)
    print("✅ Webhook قبلی حذف شد.")

    # اجرای Flask در ترد جداگانه
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    print(f"🚀 سرور HTTP روی پورت {os.getenv('PORT', 8080)} راه افتاد.")

    # اجرای Polling (با drop_pending_updates=True برای جلوگیری از Conflict)
    print("🤖 ربات با Polling شروع به کار کرد...")
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
