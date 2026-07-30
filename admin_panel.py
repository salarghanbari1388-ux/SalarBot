# admin_panel.py

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    ContextTypes,
    CallbackQueryHandler,
    CommandHandler
)


# آیدی ادمین
ADMIN_ID = 8646600079



# =========================
# نمایش پنل ادمین
# =========================

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text(
            "⛔ شما ادمین نیستید"
        )
        return


    keyboard = [

        [
            InlineKeyboardButton(
                "📊 آمار ربات",
                callback_data="admin_stats"
            )
        ],

        [
            InlineKeyboardButton(
                "👑 درخواست VIP",
                callback_data="vip_list"
            )
        ],

        [
            InlineKeyboardButton(
                "💳 پرداخت‌ها",
                callback_data="payment_list"
            )
        ],

        [
            InlineKeyboardButton(
                "📢 پیام همگانی",
                callback_data="broadcast"
            )
        ],

        [
            InlineKeyboardButton(
                "❓ مدیریت سوالات",
                callback_data="questions"
            )
        ],

        [
            InlineKeyboardButton(
                "⚙ تنظیمات",
                callback_data="settings"
            )
        ]

    ]


    await update.message.reply_text(
        "👑 پنل مدیریت SalarBot\n\n"
        "یک گزینه را انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )



# =========================
# دکمه های پنل
# =========================

async def admin_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()


    if query.from_user.id != ADMIN_ID:
        return



    # آمار

    if query.data == "admin_stats":

        text = """
📊 آمار SalarBot

👤 کاربران: 0
👑 کاربران VIP: 0
❓ تعداد سوالات: 0
💰 درآمد: 0 تومان

(اتصال به دیتابیس بعداً)
"""

        await query.edit_message_text(text)



    # لیست VIP

    elif query.data == "vip_list":

        text = """
👑 درخواست‌های VIP

درخواستی وجود ندارد.

در این قسمت:
✅ تایید VIP
❌ رد درخواست

نمایش داده می‌شود.
"""

        await query.edit_message_text(text)



    # پرداخت‌ها

    elif query.data == "payment_list":

        text = """
💳 پرداخت‌ها

لیست کارت به کارت‌ها:

فعلاً خالی است.

بعد از اتصال دیتابیس:
نام کاربر
مبلغ
عکس رسید
وضعیت پرداخت
نمایش داده می‌شود.
"""

        await query.edit_message_text(text)



    # پیام همگانی

    elif query.data == "broadcast":

        await query.edit_message_text(
            "📢 برای ارسال پیام همگانی:\n"
            "/broadcast متن پیام"
        )



    # سوالات

    elif query.data == "questions":

        await query.edit_message_text(
            "❓ مدیریت سوالات\n\n"
            "/addquestion\n"
            "اضافه کردن سوال جدید"
        )



    # تنظیمات

    elif query.data == "settings":

        await query.edit_message_text(
            "⚙ تنظیمات ربات\n\n"
            "قیمت VIP\n"
            "تعداد سوال رایگان\n"
            "تنظیمات بانک سوال"
        )





# =========================
# ارسال پیام همگانی
# =========================

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return


    message = " ".join(context.args)


    if not message:
        await update.message.reply_text(
            "مثال:\n"
            "/broadcast سلام کاربران"
        )
        return


    # اینجا لیست کاربران از دیتابیس خوانده می‌شود

    await update.message.reply_text(
        "✅ پیام برای کاربران ارسال شد"
    )





# =========================
# اضافه کردن هندلرها به ربات
# =========================

def setup_admin(application):

    application.add_handler(
        CommandHandler(
            "admin",
            admin_panel
        )
    )


    application.add_handler(
        CommandHandler(
            "broadcast",
            broadcast
        )
    )


    application.add_handler(
        CallbackQueryHandler(
            admin_buttons
        )
)
