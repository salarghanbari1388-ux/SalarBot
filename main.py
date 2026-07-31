import os
import sys
import asyncio
import threading
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from handlers import start, text_handler, photo_handler
from admin_panel import setup_admin

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    print("❌ BOT_TOKEN تنظیم نشده!")
    sys.exit(1)

flask_app = Flask(__name__)

@flask_app.route('/')
@flask_app.route('/health')
def health():
    return jsonify({"status": "ok"}), 200

@flask_app.route('/webhook', methods=['POST'])
async def webhook():
    if request.headers.get('content-type') == 'application/json':
        try:
            update = Update.de_json(request.get_json(force=True), application.bot)
            await application.process_update(update)
            return 'ok', 200
        except Exception as e:
            print(f"❌ خطا در webhook: {e}")
            return 'error', 500
    return 'bad request', 400

def run_flask():
    port = int(os.getenv("PORT", 8080))
    flask_app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

async def main():
    global application
    application = Application.builder().token(TOKEN).build()

    # ثبت هندلرها
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    setup_admin(application)  # پنل ادمین

    # تنظیم Webhook
    render_hostname = os.getenv("RENDER_EXTERNAL_HOSTNAME")
    if not render_hostname:
        print("❌ RENDER_EXTERNAL_HOSTNAME پیدا نشد!")
        sys.exit(1)

    webhook_url = f"https://{render_hostname}/webhook"
    await application.bot.set_webhook(url=webhook_url, drop_pending_updates=True)
    print(f"✅ Webhook تنظیم شد: {webhook_url}")

    # اجرای Flask در ترد جداگانه
    threading.Thread(target=run_flask, daemon=True).start()
    print(f"🚀 سرور Flask روی پورت {os.getenv('PORT', 8080)} اجرا شد.")

    # نگه‌داشتن برنامه
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
