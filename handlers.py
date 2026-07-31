from aiogram import Router, F, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from datetime import datetime, timedelta
import random
import database as db
import keyboards as kb
import utils

router = Router()

class QuizState(StatesGroup):
    waiting_for_answer = State()

@router.message(Command("start"))
async def start_cmd(message: types.Message):
    user = db.get_or_create_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.full_name
    )
    # اگر referral داشته باشد (برای دعوت)
    args = message.text.split()
    if len(args) > 1 and args[1].startswith("ref_"):
        referrer_id = int(args[1].split("_")[1])
        if referrer_id != message.from_user.id:
            referrer = db.get_user_by_telegram_id(referrer_id)
            if referrer:
                db.increment_invite_count(referrer['id'])
                await message.bot.send_message(
                    referrer_id,
                    f"👤 کاربر {message.from_user.full_name} با لینک شما وارد شد!"
                )

    await message.answer(
        "🎯 به ربات معمایی خوش آمدی!\n"
        "هر روز ۳ سوال رایگان داری، با پاسخ صحیح امتیاز بگیر.\n"
        "برای اطلاعات بیشتر از منو استفاده کن.",
        reply_markup=kb.main_menu()
    )

@router.message(F.text == "🔮 سوال روزانه")
async def daily_question(message: types.Message, state: FSMContext):
    user = db.get_user_by_telegram_id(message.from_user.id)
    if not user:
        await message.answer("لطفاً /start را بزنید.")
        return

    today_count = db.get_today_question_count(user['id'])
    max_free = int(db.get_setting("daily_free_questions") or 3)

    if today_count >= max_free:
        if utils.is_vip_valid(user.get('vip_expiry')):
            pass  # VIP می‌تواند بیشتر بپرسد
        else:
            await message.answer(
                "⛔ سوالات رایگان امروز تمام شد!\n"
                "برای ادامه، اشتراک VIP تهیه کن یا فردا بیا.",
                reply_markup=kb.vip_purchase_button()
            )
            return

    # سوال نمونه (جایگزین با سوال واقعی از دیتابیس)
    question_text = "۲ + ۲ چند می‌شود؟"
    correct_answer = "۴"
    await state.update_data(correct_answer=correct_answer)
    await state.set_state(QuizState.waiting_for_answer)

    await message.answer(
        f"❓ سوال شماره {today_count+1}:\n\n{question_text}",
        reply_markup=kb.cancel_button()
    )

@router.message(StateFilter(QuizState.waiting_for_answer))
async def check_answer(message: types.Message, state: FSMContext):
    data = await state.get_data()
    correct = data.get("correct_answer")
    user = db.get_user_by_telegram_id(message.from_user.id)

    if message.text.strip().lower() == correct.lower():
        db.update_user_score(user['id'], 10)
        await message.answer("✅ پاسخ درست! +۱۰ امتیاز")
    else:
        await message.answer(f"❌ پاسخ نادرست. پاسخ صحیح: {correct}")

    db.increment_daily_question(user['id'])
    await state.clear()

@router.message(F.text == "👤 پروفایل")
async def profile(message: types.Message):
    user = db.get_user_by_telegram_id(message.from_user.id)
    if not user:
        await message.answer("ابتدا /start را بزنید.")
        return
    vip_status = "✅ فعال" if utils.is_vip_valid(user.get('vip_expiry')) else "❌ غیرفعال"
    await message.answer(
        f"👤 پروفایل شما:\n"
        f"امتیاز: {user['score']}\n"
        f"تعداد دعوت‌ها: {user['invited_count']}\n"
        f"وضعیت VIP: {vip_status}\n"
        f"تعداد کل پاسخ‌ها: {user['total_questions_answered']}"
    )

@router.message(F.text == "👥 دعوت دوستانه")
async def invite(message: types.Message):
    bot_info = await message.bot.get_me()
    link = utils.get_referral_link(bot_info.username, message.from_user.id)
    threshold = int(db.get_setting("invite_threshold") or 10)
    await message.answer(
        f"👥 هر نفر با دعوت {threshold} دوست، جایزه دریافت می‌کند.\n"
        f"لینک دعوت شما:\n{link}"
    )

@router.message(F.text == "📢 اطلاعیه‌ها")
async def announcements(message: types.Message):
    items = db.get_latest_announcements(5)
    if not items:
        await message.answer("هیچ اطلاعیه‌ای وجود ندارد.")
        return
    text = "📢 آخرین اطلاعیه‌ها:\n\n" + "\n\n".join(f"{a['text']}" for a in items)
    await message.answer(text)

@router.message(F.text == "❓ پشتیبانی")
async def support(message: types.Message, state: FSMContext):
    await message.answer("سوال خود را بنویسید تا برای ادمین ارسال شود.")
    await state.set_state("waiting_support_question")

@router.message(StateFilter("waiting_support_question"))
async def process_support(message: types.Message, state: FSMContext):
    user = db.get_user_by_telegram_id(message.from_user.id)
    ticket_id = db.create_support_ticket(user['id'], message.text)
    # اطلاع به ادمین
    for admin_id in ADMIN_IDS:
        await message.bot.send_message(
            admin_id,
            f"🎫 تیکت جدید #{ticket_id} از {message.from_user.full_name}:\n{message.text}",
            reply_markup=kb.admin_ticket_answer(ticket_id)
        )
    await message.answer("✅ سوال شما ثبت شد. به زودی پاسخ داده می‌شود.")
    await state.clear()

@router.callback_query(F.data == "cancel")
async def cancel_callback(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.answer("انصراف داده شد.")
