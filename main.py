import os

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from menu import main_menu
from game import register_user
from profile import profile_text
from riddles import get_riddle
from answers import save_answer, check_answer
from treasure import open_treasure

TOKEN = os.getenv("BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    register_user(
        user.id,
        user.username or user.first_name
    )

    await update.message.reply_text(
        "🏺 به بازی شکار گنج خوش آمدی!",
        reply_markup=main_menu()
    )


async def message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    if text == "🎮 شروع بازی":
        riddle = get_riddle()

        save_answer(
            user_id,
            riddle["answer"]
        )

        await update.message.reply_text(
            "🧩 معما:\n\n"
            + riddle["question"]
        )

    elif text == "👤 پروفایل":
        await update.message.reply_text(
            profile_text(user_id)
        )

    elif text == "🏆 رتبه‌بندی":
        await update.message.reply_text(
            "🏆 این بخش به‌زودی فعال می‌شود."
        )

    elif text == "⭐ VIP":
        await update.message.reply_text(
            "⭐ بخش VIP به‌زودی فعال می‌شود."
        )

    elif text == "🎁 دعوت دوستان":
        await update.message.reply_text(
            "🎁 این بخش به‌زودی فعال می‌شود."
        )

    else:
        if check_answer(user_id, text):

            reward = open_treasure(user_id)

            await update.message.reply_text(
                f"🎉 جواب درست بود!\n\n🎁 {reward} امتیاز گرفتی."
            )

        else:
            await update.message.reply_text(
                "❌ جواب اشتباه است."
            )


app = Application.builder().token(TOKEN).build()

app.add_handler(
    CommandHandler(
        "start",
        start
    )
)

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        message
    )
)

app.run_polling()
