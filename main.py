import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN, ADMIN_IDS
from database import init_db
from handlers import user, vip, admin, contest

async def main():
    init_db()
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.include_routers(
        user.router,
        vip.router,
        admin.router,
        contest.router
    )

    # ارسال پیام به ادمین‌ها هنگام استارت
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, "🤖 ربات با موفقیت راه‌اندازی شد!")
        except:
            pass

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
