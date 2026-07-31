import os
import logging
from flask import Flask, request
from telegram import Update, Bot, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, CallbackQueryHandler, filters

# ---------- تنظیمات از متغیرهای محیطی ----------
TOKEN = os.environ.get('TELEGRAM_TOKEN')
if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN تنظیم نشده")

BOT_USERNAME = os.environ.get('BOT_USERNAME', 'SalarBot')
ADMIN_ID = int(os.environ.get('ADMIN_ID', 8646600079))
WEBHOOK_URL = os.environ.get('WEBHOOK_URL')  # مثل https://mybot.onrender.com
PORT = int(os.environ.get('PORT', 10000))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------- Flask ----------
app = Flask(__name__)

# ---------- ربات و دیسپچر ----------
bot = Bot(token=TOKEN)
dispatcher = Dispatcher(bot, None, workers=0)

# ======================================================
#  ** دیتابیس‌های درون‌حافظه (جایگزین database.py) **
# ======================================================
users = {}  # {user_id: {"name": str, "score": int, "free_questions": int, "vip": bool}}

def add_user(user_id, name):
    if user_id not in users:
        users[user_id] = {"name": name, "score": 0, "free_questions": 3, "vip": False}

def get_user(user_id):
    return users.get(user_id)

def add_score(user_id, points):
    if user_id in users:
        users[user_id]["score"] += points

# ======================================================
#  ** ماژول VIP (جایگزین vip_manager.py) **
# ======================================================
VIP_PRICE = 50000
CARD_NUMBER = "1234-5678-9012-3456"
vip_requests = []  # هر درخواست: {"user_id": int, "photo": str}

def is_vip(user_id):
    return users.get(user_id, {}).get("vip", False)

def use_free_question(user_id):
    user = get_user(user_id)
    if user and user.get("free_questions", 0) > 0:
        user["free_questions"] -= 1
        return True
    return False

def add_vip_request(user_id, photo):
    vip_requests.append({"user_id": user_id, "photo": photo, "status": "pending"})

def get_vip_requests():
    return vip_requests

def approve_vip(index):
    if 0 <= index < len(vip_requests):
        req = vip_requests.pop(index)
        user_id = req['user_id']
        if user_id in users:
            users[user_id]["vip"] = True

def reject_vip(index):
    if 0 <= index < len(vip_requests):
        vip_requests.pop(index)

# ======================================================
#  ** ماژول معماها (جایگزین riddles.py) **
# ======================================================
RIDDLES = [
    {"question": "چه چیزی همیشه جلو شماست ولی هرگز دیده نمی‌شود؟", "answer": "آینده"},
    {"question": "چیزی که هر چه بیشتر از آن برداری، بزرگتر می‌شود؟", "answer": "چاله"},
    {"question": "چه چیزی را می‌شکنی بدون آنکه آن را لمس کنی؟", "answer": "قول"},
]
def get_riddle():
    import random
    return random.choice(RIDDLES)

# ======================================================
#  ** ماژول گنج (جایگزین treasure.py) **
# ======================================================
import random
def open_treasure(user_id):
    reward = random.randint(1, 100)
    add_score(user_id, reward)
    return reward

# ======================================================
#  ** ماژول پروفایل (جایگزین profile.py) **
# ======================================================
def profile_text(user_id):
    user = get_user(user_id)
    if not user:
        return "کاربر یافت نشد."
    return f"👤 نام: {user['name']}\n⭐ امتیاز: {user['score']}\n🎟 سوال رایگان: {user.get('free_questions', 0)}"

# ======================================================
#  ** ماژول رتبه‌بندی (جایگزین ranking.py) **
# ======================================================
def ranking_text():
    sorted_users = sorted(users.items(), key=lambda x: x[1].get('score', 0), reverse=True)
    if not sorted_users:
        return "هیچ کاربری ثبت نشده"
    lines = []
    for i, (uid, data) in enumerate(sorted_users[:5], 1):
        lines.append(f"{i}. {data.get('name', uid)} – {data.get('score', 0)} امتیاز")
    return "\n".join(lines)

# ======================================================
#  ** سیستم دعوت (referral) **
# ======================================================
referrals = {}
invited_by = {}

def add_referral(user_id, inviter_id):
    if user_id == inviter_id or user_id in invited_by:
        return
    invited_by[user_id] = inviter_id
    referrals[inviter_id] = referrals.get(inviter_id, 0) + 1

def get_referrals(user_id):
    return referrals.get(user_id, 0)

def referral_link(user_id):
    return f"https://t.me/{BOT_USERNAME}?start={user_id}"

def top_referrers():
    return sorted(referrals.items(), key=lambda x: x[1], reverse=True)

# ======================================================
#  ** کیبورد منوی اصلی (از handlers.py) **
# ======================================================
def main_menu():
    keyboard = [
        ["🎮 شروع بازی"],
        ["👤 پروفایل", "🏆 رتبه‌بندی"],
        ["⭐ VIP", "🎁 دعوت دوستان"],
        ["🎧 پشتیبانی"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ======================================================
#  ** هندلرها (همگام) **
# ======================================================

def start(update, context):
    user = update.effective_user
    user_id = user.id
    add_user(user_id, user.username or user.first_name)

    # پردازش لینک دعوت (deep linking)
    args = context.args
    if args and args[0].isdigit():
        inviter_id = int(args[0])
        if inviter_id != user_id:
            add_referral(user_id, inviter_id)
            bot.send_message(
                chat_id=inviter_id,
                text=f"👤 کاربر جدید {user.mention_html()} از طریق لینک شما وارد شد!",
                parse_mode='HTML'
            )

    update.message.reply_text(
        "🏺 به بازی شکار گنج خوش آمدی!",
        reply_markup=main_menu()
    )

def text_handler(update, context):
    text = update.message.text
    user_id = update.effective_user.id

    if text == "🎮 شروع بازی":
        if not is_vip(user_id) and not use_free_question(user_id):
            update.message.reply_text("⛔ سهمیه رایگان تمام شد.")
            return
        riddle = get_riddle()
        context.user_data["current_answer"] = riddle["answer"]
        update.message.reply_text(f"🧩 معما:\n\n{riddle['question']}")

    elif text == "👤 پروفایل":
        update.message.reply_text(profile_text(user_id))

    elif text == "🏆 رتبه‌بندی":
        update.message.reply_text(ranking_text())

    elif text == "⭐ VIP":
        context.user_data["vip_request"] = True
        update.message.reply_text(
            f"👑 خرید VIP\n💰 مبلغ: {VIP_PRICE} تومان\n💳 شماره کارت: {CARD_NUMBER}"
        )

    elif text == "🎁 دعوت دوستان":
        link = referral_link(user_id)
        count = get_referrals(user_id)
        update.message.reply_text(f"🔗 لینک دعوت:\n{link}\n👥 دعوت‌ها: {count}")

    elif text == "🎧 پشتیبانی":
        context.user_data["support"] = True
        update.message.reply_text("🎧 پیام خود را ارسال کنید.")

    elif context.user_data.get("support"):
        update.message.reply_text("✅ پیام شما دریافت شد.")
        context.user_data["support"] = False

    else:
        correct = context.user_data.get("current_answer")
        if correct and text.strip().lower() == correct.lower():
            reward = open_treasure(user_id)
            update.message.reply_text(f"🎉 درست! +{reward} امتیاز")
            context.user_data["current_answer"] = None
        else:
            update.message.reply_text("❌ غلط، دوباره تلاش کن.")

def photo_handler(update, context):
    if context.user_data.get("vip_request"):
        photo = update.message.photo[-1].file_id
        add_vip_request(update.effective_user.id, photo)
        update.message.reply_text("✅ رسید دریافت شد. درخواست شما ثبت شد.")
        context.user_data["vip_request"] = False

# ======================================================
#  ** پنل مدیریت (از admin_panel.py) **
# ======================================================
def admin_panel(update, context):
    if update.effective_user.id != ADMIN_ID:
        update.message.reply_text("⛔ شما دسترسی ندارید.")
        return

    keyboard = [
        [InlineKeyboardButton("📊 آمار کلی", callback_data="stats")],
        [InlineKeyboardButton("👑 درخواست‌های VIP", callback_data="vip")],
        [InlineKeyboardButton("🎧 پیام‌های پشتیبانی", callback_data="support")],
        [InlineKeyboardButton("🎁 برترین دعوت‌کننده‌ها", callback_data="refs")],
        [InlineKeyboardButton("🏆 اطلاعات جایزه", callback_data="reward")]
    ]
    update.message.reply_text(
        "👑 **پنل مدیریت**",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

def admin_buttons(update, context):
    query = update.callback_query
    query.answer()

    if query.from_user.id != ADMIN_ID:
        query.edit_message_text("⛔ شما دسترسی ندارید.")
        return

    if query.data == "stats":
        total_users = len(users)
        total_score = sum(u.get("score", 0) for u in users.values())
        text = (
            f"📊 **آمار کلی**\n\n"
            f"👥 تعداد کاربران: {total_users}\n"
            f"🏆 مجموع امتیازات: {total_score}"
        )
        query.edit_message_text(text, parse_mode="Markdown")

    elif query.data == "vip":
        requests = get_vip_requests()
        if not requests:
            query.edit_message_text("👑 درخواست VIP وجود ندارد.")
        else:
            text = "👑 **درخواست‌های VIP**\n\n"
            keyboard = []
            for i, r in enumerate(requests):
                status = r.get('status', 'در انتظار')
                text += f"{i+1}) کاربر {r['user_id']} - {status}\n"
                if status == "pending":
                    keyboard.append([
                        InlineKeyboardButton(f"✅ تأیید {i+1}", callback_data=f"approve_{i}"),
                        InlineKeyboardButton(f"❌ رد {i+1}", callback_data=f"reject_{i}")
                    ])
            if keyboard:
                keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back_admin")])
                query.edit_message_text(
                    text,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode="Markdown"
                )
            else:
                query.edit_message_text(text, parse_mode="Markdown")

    elif query.data.startswith("approve_"):
        index = int(query.data.split("_")[1])
        approve_vip(index)
        query.edit_message_text(f"✅ درخواست {index+1} تأیید شد. کاربر VIP شد.")

    elif query.data.startswith("reject_"):
        index = int(query.data.split("_")[1])
        reject_vip(index)
        query.edit_message_text(f"❌ درخواست {index+1} رد شد.")

    elif query.data == "support":
        query.edit_message_text("🎧 **پیام‌های پشتیبانی**\n\nدر حال توسعه...")

    elif query.data == "refs":
        top = top_referrers()
        if not top:
            query.edit_message_text("🎁 هیچ دعوتی ثبت نشده است.")
        else:
            text = "🎁 **برترین دعوت‌کننده‌ها**\n\n"
            for i, (user_id, count) in enumerate(top[:5], 1):
                user = get_user(user_id)
                name = user['name'] if user else str(user_id)
                text += f"{i}) {name} - {count} دعوت\n"
            query.edit_message_text(text, parse_mode="Markdown")

    elif query.data == "reward":
        # جایزه (مثلاً ۵ میلیون تومان)
        text = (
            f"🏆 **جایزه مسابقه**\n\n"
            f"💰 مبلغ: ۵,۰۰۰,۰۰۰ تومان\n"
            f"⏳ روزهای باقی‌مانده: ۱۵ روز"
        )
        query.edit_message_text(text, parse_mode="Markdown")

    elif query.data == "back_admin":
        keyboard = [
            [InlineKeyboardButton("📊 آمار کلی", callback_data="stats")],
            [InlineKeyboardButton("👑 درخواست‌های VIP", callback_data="vip")],
            [InlineKeyboardButton("🎧 پیام‌های پشتیبانی", callback_data="support")],
            [InlineKeyboardButton("🎁 برترین دعوت‌کننده‌ها", callback_data="refs")],
            [InlineKeyboardButton("🏆 اطلاعات جایزه", callback_data="reward")]
        ]
        query.edit_message_text(
            "👑 **پنل مدیریت**",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

# ======================================================
#  ** ثبت هندلرها در دیسپچر **
# ======================================================
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("admin", admin_panel))
dispatcher.add_handler(MessageHandler(filters.PHOTO, photo_handler))
dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
dispatcher.add_handler(CallbackQueryHandler(admin_buttons))

# ======================================================
#  ** مسیرهای Flask (برای Webhook) **
# ======================================================
@app.route('/', methods=['GET'])
def index():
    return "ربات در حال اجراست ✅", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        json_data = request.get_json(force=True)
        update = Update.de_json(json_data, bot)
        dispatcher.process_update(update)
        return 'ok', 200
    except Exception as e:
        logger.error(f"خطا در وب‌هوک: {e}")
        return 'error', 500

# ======================================================
#  ** اجرای اصلی **
# ======================================================
if __name__ == '__main__':
    if WEBHOOK_URL:
        webhook_path = f"{WEBHOOK_URL}/webhook"
        try:
            bot.set_webhook(url=webhook_path)
            logger.info(f"✅ Webhook تنظیم شد: {webhook_path}")
        except Exception as e:
            logger.error(f"❌ خطا در تنظیم Webhook: {e}")
    else:
        logger.warning("⚠️ WEBHOOK_URL تنظیم نشده!")

    app.run(host='0.0.0.0', port=PORT)
