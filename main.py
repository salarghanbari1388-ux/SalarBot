import os
import sys
import asyncio
import threading
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from handlers import start, text_handler, photo_handler
from admin_panel import setup_admin

# ==================== تنظیمات اولیه ====================
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    print("❌ BOT_TOKEN تنظیم نشده! متغیر محیطی را اضافه کن.")
    sys.exit(1)

flask_app = Flask(__name__)
application = None  # گلوبال برای دسترسی در webhook

# ==================== مسیرهای Flask ====================
@flask_app.route('/')
@flask_app.route('/health')
def health():
    return jsonify({"status": "ok"}), 200

@flask_app.route('/webhook', methods=['POST'])
def webhook():
    """دریافت آپدیت از تلگرام (هم‌زمان)"""
    if request.headers.get('content-type') != 'application/json':
        return 'bad request', 400

    try:
        json_data = request.get_json(force=True)
        update = Update.de_json(json_data, application.bot)
        # اجرای پردازش async در همین ترد (چون ترد فلاسک event loop نداره، مشکلی پیش نمیاد)
        asyncio.run(application.process_update(update))
        return 'ok', 200
    except Exception as e:
        print(f"❌ خطا در webhook: {e}")
        return 'error', 500

def run_flask():
    """اجرای سرور Flask در یک ترد جداگانه"""
    port = int(os.getenv("PORT", 8080))
    # use_reloader=False ضروری است تا ترد اضافی ساخته نشود
    flask_app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# ==================== تابع اصلی ====================
async def main():
    global application

    # 1. ساخت اپلیکیشن
    application = Application.builder().token(TOKEN).build()

    # 2. ثبت هندلرها
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    setup_admin(application)  # پنل ادمین

    # 3. تنظیم Webhook
    # رندر برای Web Serviceها این متغیر را میدهد، برای Background Worker نه
    render_hostname = os.getenv("RENDER_EXTERNAL_HOSTNAME")
    if not render_hostname:
        # اگر در لوکال یا روی سرویس دیگری هستی، از آدرس خودت استفاده کن
        print("⚠️ RENDER_EXTERNAL_HOSTNAME پیدا نشد! از آدرس پیش‌فرض استفاده می‌شود.")
        render_hostname = "localhost"  # برای تست لوکال (با ngrok یا مشابه)

    webhook_url = f"https://{render_hostname}/webhook"
    await application.bot.set_webhook(url=webhook_url, drop_pending_updates=True)
    print(f"✅ Webhook با موفقیت روی {webhook_url} تنظیم شد.")

    # 4. اجرای Flask در ترد جداگانه
    threading.Thread(target=run_flask, daemon=True).start()
    print(f"🚀 سرور Flask روی پورت {os.getenv('PORT', 8080)} اجرا شد.")

    # 5. نگه‌داشتن برنامه با یک حلقه‌ی بی‌نهایت سبک
    print("✅ ربات آماده‌ی دریافت پیام است...")
    while True:
        await asyncio.sleep(3600)  # هر یک ساعت بیدار می‌شود تا اتصال قطع نشود

# ==================== اجرا ====================
if __name__ == "__main__":
    asyncio.run(main())
