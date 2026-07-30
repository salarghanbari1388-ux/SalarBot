from telegram import ReplyKeyboardMarkup

def main_menu():
    keyboard = [
        ["🎮 شروع بازی", "👤 پروفایل"],
        ["🏆 رتبه‌بندی", "⭐ VIP"],
        ["🎁 دعوت دوستان"]
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )
