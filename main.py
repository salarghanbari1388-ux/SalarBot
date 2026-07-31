import os
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

TOKEN = os.getenv("BOT_TOKEN")
BOT_USERNAME = "SalarPlay137Bot"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    register_user(user.id, user.username or user.first_name)

    # بررسی دعوت‌کننده (referral)
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

    # ---- دکمه‌های منو ----
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
            "🧩 معما:\n\n" + riddle["question"] +
            "\n\nجوابت رو بفرست."
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

    # ---- حالت پشتیبانی (ارسال پیام به ادمین) ----
    elif context.user_data.get("support"):
        add_support_message(user_id, text)
        await update.message.reply_text("✅ پیام شما برای پشتیبانی ارسال شد.")
        context.user_data["support"] = False

    # ---- پاسخ به معما ----
    else:
        if check_answer(user_id, text):
            reward = open_treasure(user_id)
            await update.message.reply_text(
                f"🎉 جواب درست بود!\n🎁 {reward} امتیاز گرفتی."
            )
        else:
            await update.message.reply_text("❌ جواب درست نیست، دوباره تلاش کن.")


async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # اگر کاربر درخواست VIP داشته باشد
    if context.user_data.get("vip_request"):
        photo = update.message.photo[-1].file_id
        add_vip_request(update.effective_user.id, photo)
        await update.message.reply_text(
            "✅ رسید VIP ارسال شد.\n⏳ منتظر تایید ادمین باشید."
        )
        context.user_data["vip_request"] = False


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    setup_admin(app)  # اگر تابع setup_admin هندلرهای ادمین را اضافه می‌کند

    app.run_polling()


if __name__ == "__main__":
    main()
