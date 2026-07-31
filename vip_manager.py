from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from datetime import datetime, timedelta
import database as db
import keyboards as kb
import utils
from config import ADMIN_IDS

router = Router()

class VIPPurchaseState(StatesGroup):
    waiting_for_receipt = State()

@router.callback_query(F.data == "buy_vip")
async def start_vip_purchase(callback: types.CallbackQuery, state: FSMContext):
    price = utils.calculate_vip_price()
    card_number = db.get_setting("bank_card_number") or "6219861451203524"
    bank_name = db.get_setting("bank_name") or "بانک"

    await callback.message.edit_text(
        f"💎 خرید اشتراک VIP (۷ روزه)\n"
        f"💰 قیمت: {price:,} تومان\n\n"
        f"لطفاً مبلغ را به شماره کارت زیر واریز کنید:\n"
        f"`{card_number}`\n"
        f"({bank_name})\n\n"
        "سپس روی دکمه «ارسال رسید» بزنید و عکس رسید را بفرستید.",
        parse_mode="Markdown",
        reply_markup=kb.receipt_send_button()
    )
    await state.update_data(amount=price)
    await callback.answer()

@router.callback_query(F.data == "send_receipt")
async def ask_receipt(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "📸 لطفاً عکس رسید پرداخت را ارسال کنید."
    )
    await state.set_state(VIPPurchaseState.waiting_for_receipt)
    await callback.answer()

@router.message(VIPPurchaseState.waiting_for_receipt, F.photo)
async def receive_receipt(message: types.Message, state: FSMContext):
    data = await state.get_data()
    amount = data.get("amount")
    photo_id = message.photo[-1].file_id
    user = db.get_user_by_telegram_id(message.from_user.id)

    payment_id = db.create_payment(user['id'], amount, photo_id)

    for admin_id in ADMIN_IDS:
        await message.bot.send_photo(
            admin_id,
            photo_id,
            caption=f"💳 پرداخت جدید #{payment_id}\n"
                    f"👤 {message.from_user.full_name} (@{message.from_user.username})\n"
                    f"💰 {amount:,} تومان",
            reply_markup=kb.admin_payment_actions(payment_id)
        )

    await message.answer(
        "✅ رسید شما دریافت شد.\n"
        "پس از تایید ادمین، اشتراک شما فعال می‌شود.",
        reply_markup=kb.main_menu()
    )
    await state.clear()

@router.message(VIPPurchaseState.waiting_for_receipt)
async def invalid_receipt(message: types.Message):
    await message.answer("❌ لطفاً یک عکس ارسال کنید.")
