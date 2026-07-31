from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler
from vip_manager import get_vip_requests, approve_vip, reject_vip
from database import users
from ranking import ranking_text

ADMIN_ID = 8646600079

async def admin_panel(update, context):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ شما دسترسی ندارید.")
        return

    keyboard = [
        [InlineKeyboardButton("📊 آمار کلی", callback_data="stats")],
        [InlineKeyboardButton("👑 درخواست‌های VIP", callback_data="vip")],
        [InlineKeyboardButton("🎧 پیام‌های پشتیبانی", callback_data="support")],
        [InlineKeyboardButton("🎁 برترین دعوت‌کننده‌ها", callback_data="refs")],
        [InlineKeyboardButton("🏆 اطلاعات جایزه", callback_data="reward")]
    ]
    await update.message.reply_text(
        "👑 **پنل مدیریت**",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def admin_buttons(update, context):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        await query.edit_message_text("⛔ شما دسترسی ندارید.")
        return

    if query.data == "stats":
        total_users = len(users)
        total_games = sum(u.get("games", 0) for u in users.values())
        total_score = sum(u.get("score", 0) for u in users.values())
        text = (
            f"📊 **آمار کلی**\n\n"
            f"👥 تعداد کاربران: {total_users}\n"
            f"🎮 تعداد بازی‌ها: {total_games}\n"
            f"🏆 مجموع امتیازات: {total_score}"
        )
        await query.edit_message_text(text, parse_mode="Markdown")

    elif query.data == "vip":
        requests = get_vip_requests()
        if not requests:
            await query.edit_message_text("👑 درخواست VIP وجود ندارد.")
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
                await query.edit_message_text(
                    text,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode="Markdown"
                )
            else:
                await query.edit_message_text(text, parse_mode="Markdown")

    elif query.data.startswith("approve_"):
        index = int(query.data.split("_")[1])
        approve_vip(index)
        await query.edit_message_text(f"✅ درخواست {index+1} تأیید شد. کاربر VIP شد.")

    elif query.data.startswith("reject_"):
        index = int(query.data.split("_")[1])
        reject_vip(index)
        await query.edit_message_text(f"❌ درخواست {index+1} رد شد.")

    elif query.data == "support":
        # در حال توسعه
        await query.edit_message_text("🎧 **پیام‌های پشتیبانی**\n\nدر حال توسعه...")

    elif query.data == "refs":
        from referral import top_referrers
        top = top_referrers()
        if not top:
            await query.edit_message_text("🎁 هیچ دعوتی ثبت نشده است.")
        else:
            text = "🎁 **برترین دعوت‌کننده‌ها**\n\n"
            for i, (user_id, count) in enumerate(top[:5], 1):
                text += f"{i}) کاربر {user_id} - {count} دعوت\n"
            await query.edit_message_text(text, parse_mode="Markdown")

    elif query.data == "reward":
        from rewards import current_prize, days_left
        text = (
            f"🏆 **جایزه مسابقه**\n\n"
            f"💰 مبلغ: {current_prize():,} تومان\n"
            f"⏳ روزهای باقی‌مانده: {days_left()} روز"
        )
        await query.edit_message_text(text, parse_mode="Markdown")

    elif query.data == "back_admin":
        keyboard = [
            [InlineKeyboardButton("📊 آمار کلی", callback_data="stats")],
            [InlineKeyboardButton("👑 درخواست‌های VIP", callback_data="vip")],
            [InlineKeyboardButton("🎧 پیام‌های پشتیبانی", callback_data="support")],
            [InlineKeyboardButton("🎁 برترین دعوت‌کننده‌ها", callback_data="refs")],
            [InlineKeyboardButton("🏆 اطلاعات جایزه", callback_data="reward")]
        ]
        await query.edit_message_text(
            "👑 **پنل مدیریت**",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

def setup_admin(app):
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CallbackQueryHandler(admin_buttons))
