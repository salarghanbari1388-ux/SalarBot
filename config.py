import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN در فایل .env تنظیم نشده است")

# آیدی عددی ادمین‌ها (از @userinfobot بگیر)
ADMIN_IDS = [123456789, 987654321]  # نمونه، خودت جایگزین کن

# تنظیمات پیش‌فرض (در دیتابیس هم ذخیره می‌شوند)
DEFAULT_SETTINGS = {
    "base_vip_price": "40000",
    "vip_duration_days": "7",
    "price_increment_per_100_users": "2000",
    "contest_first_prize": "200000",
    "contest_second_prize": "100000",
    "prize_increment_per_60_topics": "100000",
    "invite_threshold": "10",
    "daily_free_questions": "3",
    "bank_card_number": "6219861451203524",
    "bank_name": "بانک تجارت"
}
