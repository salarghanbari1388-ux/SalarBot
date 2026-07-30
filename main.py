import os
import database
from game import register_user, get_user
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    register_user(user.id, user.username or user.first_name)

    player = get_user(user.id)

    await update.message.reply_text(
        f"""🎮 سلام {user.first_name}

👤 پروفایل شما ساخته شد.

🪙 سکه: {player[2]}
⭐ سطح: {player[3]}

به دنیای شکار گنج خوش اومدی!"""
    )

app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))

app.run_polling()
