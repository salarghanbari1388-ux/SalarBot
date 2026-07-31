from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from database import add_user, get_user, add_score
from vip_manager import is_vip, use_free_question, add_vip_request
from riddles import get_riddle
from profile import profile_text
from ranking import ranking_text
from referral import add_referral, get_referrals, referral_link
from rewards import current_prize, days_left
from config import VIP_PRICE, CARD_NUMBER
from treasure import open_treasure

# ========== کیبورد منو (همون که قبلاً توی keyboards.py بود) ==========
def main_menu():
    keyboard = [
        ["🎮 شروع بازی"],
        ["👤 پروفایل", "🏆 رتبه‌بندی"],
        ["⭐ VIP", "🎁 دعوت دوستان"],
        ["🎧 پشتیبانی"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ========== هندلرها ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.username or user.first_name)
    
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

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    if text == "🎮 شروع بازی":
        if not is_vip(user_id) and not use_free_question(user_id):
            await update.message.reply_text("⛔ سهمیه رایگان تمام شد.")
            return
        riddle = get_riddle()
        context.user_data["current_answer"] = riddle["answer"]
        await update.message.reply_text(f"🧩 معما:\n\n{riddle['question']}")
    
    elif text == "👤 پروفایل":
        await update.message.reply_text(profile_text(user_id))
    
    elif text == "🏆 رتبه‌بندی":
        await update.message.reply_text(ranking_text())
    
    elif text == "⭐ VIP":
        context.user_data["vip_request"] = True
        await update.message.reply_text(
            f"👑 خرید VIP\n💰 مبلغ: {VIP_PRICE} تومان\n💳 شماره کارت: {CARD_NUMBER}"
        )
    
    elif text == "🎁 دعوت دوستان":
        link = referral_link(user_id)
        count = get_referrals(user_id)
        await update.message.reply_text(f"🔗 لینک دعوت:\n{link}\n👥 دعوت‌ها: {count}")
    
    elif text == "🎧 پشتیبانی":
        context.user_data["support"] = True
        await update.message.reply_text("🎧 پیام خود را ارسال کنید.")
    
    elif context.user_data.get("support"):
        await update.message.reply_text("✅ پیام شما دریافت شد.")
        context.user_data["support"] = False
    
    else:
        correct = context.user_data.get("current_answer")
        if correct and text.strip().lower() == correct.lower():
            reward = open_treasure(user_id)
            await update.message.reply_text(f"🎉 درست! +{reward} امتیاز")
            context.user_data["current_answer"] = None
        else:
            await update.message.reply_text("❌ غلط، دوباره تلاش کن.")

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("vip_request"):
        photo = update.message.photo[-1].file_id
        add_vip_request(update.effective_user.id, photo)
        await update.message.reply_text("✅ رسید دریافت شد. درخواست شما ثبت شد.")
        context.user_data["vip_request"] = False
