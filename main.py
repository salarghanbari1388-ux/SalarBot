from riddles import get_riddle
from answers import save_riddle, check_answerimport os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from game import register_user
from menu import main_menu

TOKEN = os.getenv("BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    register_user(
        user.id,
        user.username or user.first_name
    )

    await update.message.reply_text(
        "🏺 به بازی شکار گنج خوش آمدی!\n\n"
        "از منوی زیر شروع کن 👇",
        reply_markup=main_menu()
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
if text == "🎮 شروع بازی":riddle = get_riddle()

save_riddle(
    update.effective_user.id,
    riddle["answer"]
)

await update.message.reply_text(
    "🧩 معما:\n\n" + riddle["question"] +
    "\n\nجوابت رو بفرست."
)
    elif text == "👤 پروفایل":
        await update.message.reply_text(
            "👤 پروفایل بازیکن در حال آماده‌سازی است."
        )

    elif text == "🏆 رتبه‌بندی":
        await update.message.reply_text(
            "🏆 جدول رتبه‌بندی به‌زودی فعال می‌شود."
        )

    elif text == "⭐ VIP":
        await update.message.reply_text(
            "⭐ بخش VIP به‌زودی فعال می‌شود."
        )

    elif text == "🎁 دعوت دوستان":
        await update.message.reply_text(
            "🎁 سیستم دعوت دوستان به‌زودی فعال می‌شود."
        )


app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, button_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_riddle_answer))
app.run_polling()
