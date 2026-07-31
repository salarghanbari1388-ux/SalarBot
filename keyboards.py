from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔮 سوال روزانه")],
            [KeyboardButton(text="💎 خرید VIP")],
            [KeyboardButton(text="🏆 جشنواره")],
            [KeyboardButton(text="👥 دعوت دوستانه")],
            [KeyboardButton(text="👤 پروفایل")],
            [KeyboardButton(text="📢 اطلاعیه‌ها")],
            [KeyboardButton(text="❓ پشتیبانی")]
        ],
        resize_keyboard=True
    )

def cancel_button():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ انصراف", callback_data="cancel")]
    ])

def vip_purchase_button():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 خرید VIP", callback_data="buy_vip")]
    ])

def receipt_send_button():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📸 ارسال رسید", callback_data="send_receipt")]
    ])

def admin_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 پرداخت‌های در انتظار", callback_data="admin_payments")],
        [InlineKeyboardButton(text="📢 ارسال اطلاعیه", callback_data="admin_announce")],
        [InlineKeyboardButton(text="🎫 تیکت‌های پشتیبانی", callback_data="admin_tickets")],
        [InlineKeyboardButton(text="🏦 ویرایش شماره کارت", callback_data="admin_card")],
        [InlineKeyboardButton(text="⚙️ سایر تنظیمات", callback_data="admin_settings")]
    ])

def admin_payment_actions(payment_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ تایید", callback_data=f"approve_pay_{payment_id}"),
            InlineKeyboardButton(text="❌ رد", callback_data=f"reject_pay_{payment_id}")
        ]
    ])

def admin_ticket_answer(ticket_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ پاسخ به تیکت", callback_data=f"answer_ticket_{ticket_id}")]
    ])

def admin_settings_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 بازگشت به پنل", callback_data="admin_back")]
    ])
