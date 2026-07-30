# admin_panel.py


from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    CommandHandler,
    CallbackQueryHandler
)


from vip import (
    get_vip_requests,
    approve_vip,
    reject_vip
)


from support import get_support_messages


from referrals import top_referrers


from rewards import current_prize, days_left



ADMIN_ID = 8646600079



async def admin_panel(update, context):

    if update.effective_user.id != ADMIN_ID:
        return


    keyboard = [

        [
            InlineKeyboardButton(
                "📊 آمار",
                callback_data="stats"
            )
        ],

        [
            InlineKeyboardButton(
                "👑 VIP",
                callback_data="vip"
            )
        ],

        [
            InlineKeyboardButton(
                "🎧 پشتیبانی",
                callback_data="support"
            )
        ],

        [
            InlineKeyboardButton(
                "🎁 دعوت‌ها",
                callback_data="refs"
            )
        ],

        [
            InlineKeyboardButton(
                "🏆 جایزه",
                callback_data="reward"
            )
        ]

    ]


    await update.message.reply_text(
        "👑 پنل مدیریت SalarBot",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )



async def admin_buttons(update, context):

    query = update.callback_query

    await query.answer()


    if query.from_user.id != ADMIN_ID:
        return



    if query.data == "stats":

        await query.edit_message_text(
            "📊 آمار\n\n"
            "کاربران: بعداً از دیتابیس"
        )



    elif query.data == "vip":

        requests = get_vip_requests()


        if not requests:

            await query.edit_message_text(
                "👑 درخواست VIP وجود ندارد"
            )

            return


        text = "👑 درخواست‌های VIP:\n\n"


        for i,r in enumerate(requests):

            text += (
                f"{i+1}) "
                f"کاربر {r['user_id']} "
                f"- {r['status']}\n"
            )


        await query.edit_message_text(text)



    elif query.data == "support":

        msgs = get_support_messages()


        await query.edit_message_text(
            f"🎧 پیام‌های پشتیبانی: {len(msgs)}"
        )



    elif query.data == "refs":

        top = top_referrers()


        await query.edit_message_text(
            f"🎁 نفرات برتر دعوت:\n{top[:5]}"
        )



    elif query.data == "reward":

        await query.edit_message_text(
            "🏆 مسابقه\n\n"
            f"💰 جایزه فعلی: {current_prize()} تومان\n"
            f"⏳ زمان باقی‌مانده: {days_left()} روز"
        )




def setup_admin(app):

    app.add_handler(
        CommandHandler(
            "admin",
            admin_panel
        )
    )


    app.add_handler(
        CallbackQueryHandler(
            admin_buttons
        )
    )
