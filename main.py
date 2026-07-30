import os

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from game import register_user
from menu import main_menu
from riddles import get_riddle
from answers import save_riddle, check_answer


TOKEN = os.getenv("BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    register_user(
        user.id,
        user.username or user.first_name
    )

    await update.message.reply_text(
        "🏺 به بازی شکار گنج خوش آمدی!\n\n"
        "یک گزینه را انتخاب کن 👇",
        reply_markup=main_menu()
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    if text == "🎮 شروع بازی":
        riddle = get_riddle()

        save_riddle(
            user_id,
            riddle["answer"]
        )

        await update.message.reply_text(
            "🧩 معما:\n\n"
            + riddle["question"]
            + "\n\nجوابت را بفرست."
        )


    elif text == "👤 پروفایل":
        await update.message.reply_text(
            "👤 پروفایل بازیکن\n"
            "به‌زودی تکمیل می‌شود."
        )


    elif text == "🏆 رتبه‌بندی":
        await update.message.reply_text(
            "🏆 رتبه‌بندی به‌زودی فعال می‌شود."
        )


    elif text == "⭐ VIP":
        await update.message.reply_text(
            "⭐ بخش VIP\n\n"
            "🧩 معماهای ویژه\n"
            "📦 صندوق‌های ویژه\n"
            "👑 نشان VIP\n\n"
            "به‌زودی فعال می‌شود."
        )


    elif text == "🎁 دعوت دوستان":
        await update.message.reply_text(
            "🎁 سیستم دعوت دوستان به‌زودی فعال می‌شود."
        )


    else:
        if check_answer(user_id, text):
            await update.message.reply_text(
                "🎉 جواب درست بود!\n📦 آماده باز کردن صندوق شو."
            )
        else:
            await update.message.reply_text(
                "❌ جواب درست نبود."
            )


app = Application.builder().token(TOKEN).build()

app.add_handler(
    CommandHandler("start", start)
)

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        button_handler
    )
)

app.run_polling()
