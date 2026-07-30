from telegram import Update
from telegram.ext import ContextTypes

from answers import check_answer


async def check_riddle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    answer = update.message.text

    if check_answer(user_id, answer):
        await update.message.reply_text(
            "🎉 جواب درست بود!\nحالا مرحله بعد: صندوق گنج 📦"
        )
    else:
        await update.message.reply_text(
            "❌ جواب اشتباه بود. دوباره امتحان کن."
        )
