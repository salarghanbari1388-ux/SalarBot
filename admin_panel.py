from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from datetime import datetime, timedelta
import database as db
import keyboards as kb
from config import ADMIN_IDS

router = Router()

class AdminState(StatesGroup):
    waiting_announcement = State()
    waiting_ticket_answer = State()
    waiting_card_number = State()
    waiting_setting_key = State()
    waiting_setting_value = State()

def is_admin(user_id):
    return user_id in ADMIN_IDS

@router.message(Command("admin"))
async def admin_panel(message: types.Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer("🔧 پنل مدیریت", reply_markup=kb.admin_menu())

# ---------- پرداخت‌ها ----------
@router.callback_query(F.data == "admin_payments")
async def list_payments(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        return await callback.answer("دسترسی محدود", show_alert=True)
    pending = db.get_pending_payments()
    if not pending:
        await callback.message.edit_text("✅ هیچ پرداخت در انتظاری وجود ندارد.")
        return
    for p in pending:
        await callback.message.answer_photo(
            p['receipt_photo_id'],
            caption=f"👤 {p['username'] or p['telegram_id']}\n💰 {p['amount']:,} تومان",
            reply_markup=kb.admin_payment_actions(p['id'])
        )
    await callback.answer()

@router.callback_query(F.data.startswith("approve_pay_"))
async def approve_payment(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        return await callback.answer("دسترسی محدود", show_alert=True)
    payment_id = int(callback.data.split("_")[2])
    db.update_payment_status(payment_id, "approved")
    # دریافت اطلاعات پرداخت
    with db.get_connection() as conn:
        cur = conn.execute("SELECT user_id FROM payments WHERE id = ?", (payment_id,))
        row = cur.fetchone()
        if row:
            user = db.get_user_by_id(row[0])
            expiry = (datetime.now() + timedelta(days=int(db.get_setting("vip_duration_days") or 7))).isoformat()
            db.set_vip(user['id'], expiry)
            await callback.bot.send_message(
                user['telegram_id'],
                "✅ اشتراک VIP شما فعال شد! از سوالات نامحدود لذت ببرید."
            )
    await callback.message.edit_text("✅ پرداخت تایید شد و VIP فعال گردید.")
    await callback.answer()

@router.callback_query(F.data.startswith("reject_pay_"))
async def reject_payment(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        return await callback.answer("دسترسی محدود", show_alert=True)
    payment_id = int(callback.data.split("_")[2])
    db.update_payment_status(payment_id, "rejected")
    await callback.message.edit_text("❌ پرداخت رد شد.")
    await callback.answer()

# ---------- اطلاعیه ----------
@router.callback_query(F.data == "admin_announce")
async def ask_announce(callback: types.CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return await callback.answer("دسترسی محدود", show_alert=True)
    await callback.message.edit_text("📢 متن اطلاعیه را ارسال کنید:")
    await state.set_state(AdminState.waiting_announcement)
    await callback.answer()

@router.message(AdminState.waiting_announcement)
async def process_announce(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    db.add_announcement(message.text)
    # ارسال به همه کاربران
    all_users = db.get_all_users()
    sent = 0
    for tg_id in all_users:
        try:
            await message.bot.send_message(tg_id, f"📢 اطلاعیه:\n\n{message.text}")
            sent += 1
        except:
            pass
    await message.answer(f"✅ اطلاعیه برای {sent} نفر ارسال شد.")
    await state.clear()
    await message.answer("🔧 پنل مدیریت", reply_markup=kb.admin_menu())

# ---------- تیکت‌ها ----------
@router.callback_query(F.data == "admin_tickets")
async def list_tickets(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        return await callback.answer("دسترسی محدود", show_alert=True)
    tickets = db.get_open_tickets()
    if not tickets:
        await callback.message.edit_text("✅ هیچ تیکت باز وجود ندارد.")
        return
    for t in tickets:
        await callback.message.answer(
            f"🎫 تیکت #{t['id']} از {t['username']}\n"
            f"سوال: {t['question']}\n"
            f"برای پاسخ، دکمه زیر را بزنید.",
            reply_markup=kb.admin_ticket_answer(t['id'])
        )
    await callback.answer()

@router.callback_query(F.data.startswith("answer_ticket_"))
async def ask_ticket_answer(callback: types.CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return await callback.answer("دسترسی محدود", show_alert=True)
    ticket_id = int(callback.data.split("_")[2])
    await state.update_data(ticket_id=ticket_id)
    await callback.message.edit_text("✏️ پاسخ خود را برای این تیکت بنویسید:")
    await state.set_state(AdminState.waiting_ticket_answer)
    await callback.answer()

@router.message(AdminState.waiting_ticket_answer)
async def process_ticket_answer(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    data = await state.get_data()
    ticket_id = data.get("ticket_id")
    db.answer_ticket(ticket_id, message.text)
    # ارسال پاسخ به کاربر
    with db.get_connection() as conn:
        cur = conn.execute("SELECT user_id FROM support_tickets WHERE id = ?", (ticket_id,))
        row = cur.fetchone()
        if row:
            user = db.get_user_by_id(row[0])
            await message.bot.send_message(
                user['telegram_id'],
                f"✅ پاسخ ادمین به تیکت شما:\n\n{message.text}"
            )
    await message.answer("✅ پاسخ ارسال شد.")
    await state.clear()
    await message.answer("🔧 پنل مدیریت", reply_markup=kb.admin_menu())

# ---------- ویرایش شماره کارت ----------
@router.callback_query(F.data == "admin_card")
async def edit_card(callback: types.CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return await callback.answer("دسترسی محدود", show_alert=True)
    current = db.get_setting("bank_card_number") or "تنظیم نشده"
    await callback.message.edit_text(
        f"🏦 شماره کارت فعلی:\n`{current}`\n\n"
        "شماره کارت جدید را وارد کنید:",
        parse_mode="Markdown"
    )
    await state.set_state(AdminState.waiting_card_number)
    await callback.answer()

@router.message(AdminState.waiting_card_number)
async def set_card_number(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    db.set_setting("bank_card_number", message.text.strip())
    await message.answer("✅ شماره کارت به‌روز شد.")
    await state.clear()
    await message.answer("🔧 پنل مدیریت", reply_markup=kb.admin_menu())

# ---------- تنظیمات دیگر ----------
@router.callback_query(F.data == "admin_settings")
async def show_settings(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        return await callback.answer("دسترسی محدود", show_alert=True)
    settings = db.get_all_settings()
    text = "⚙️ تنظیمات فعلی:\n\n" + "\n".join(f"• {k}: {v}" for k, v in settings.items())
    await callback.message.edit_text(text, reply_markup=kb.admin_settings_menu())
    await callback.answer()

@router.callback_query(F.data == "admin_back")
async def back_to_admin(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        return await callback.answer("دسترسی محدود", show_alert=True)
    await callback.message.edit_text("🔧 پنل مدیریت", reply_markup=kb.admin_menu())
    await callback.answer()
