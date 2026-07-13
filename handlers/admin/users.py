from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from db.requests import create_team, create_user, get_all_teams
from keyboards.admin import admin_main_menu, cancel_kb, teams_inline_kb
from middlewares.admin import IsAdmin
from states.states import CreateTeam, CreateUser
from utils.text import h

router = Router(name="admin-users")
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


# ---------------------------------------------------------------------------
# Create user
# ---------------------------------------------------------------------------


@router.message(F.text == "👤 User yaratish")
async def start_create_user(message: Message, state: FSMContext):
    await state.set_state(CreateUser.tg_id)
    await message.answer(
        "Yangi foydalanuvchining Telegram ID raqamini yuboring.\n\n"
        "(Foydalanuvchi @userinfobot orqali o'z ID sini bilib olishi mumkin)",
        reply_markup=cancel_kb(),
    )


@router.message(CreateUser.tg_id)
async def process_tg_id(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Iltimos, faqat raqam kiriting.")
        return
    await state.update_data(tg_id=int(message.text))
    await state.set_state(CreateUser.full_name)
    await message.answer("Foydalanuvchining to'liq ismini kiriting:")


@router.message(CreateUser.full_name)
async def process_full_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    teams = await get_all_teams()

    if not teams:
        data = await state.get_data()
        user = await create_user(tg_id=data["tg_id"], full_name=data["full_name"], username=None)
        await state.clear()
        await message.answer(
            f"✅ Foydalanuvchi yaratildi: {h(user.full_name)} (ID: {user.tg_id})",
            reply_markup=admin_main_menu(),
        )
        return

    await state.set_state(CreateUser.team)
    await message.answer("Qaysi teamga biriktiramiz?", reply_markup=teams_inline_kb(teams))


@router.callback_query(CreateUser.team, F.data.startswith("team:"))
async def process_team(callback: CallbackQuery, state: FSMContext):
    team_part = callback.data.split(":")[1]
    team_id = None if team_part == "none" else int(team_part)

    data = await state.get_data()
    user = await create_user(
        tg_id=data["tg_id"], full_name=data["full_name"], username=None, team_id=team_id
    )
    await state.clear()

    await callback.message.edit_text(f"✅ Foydalanuvchi yaratildi: {h(user.full_name)} (ID: {user.tg_id})")
    await callback.message.answer("Admin menyu:", reply_markup=admin_main_menu())
    await callback.answer()


# ---------------------------------------------------------------------------
# Create team
# ---------------------------------------------------------------------------


@router.message(F.text == "👥 Team yaratish")
async def start_create_team(message: Message, state: FSMContext):
    await state.set_state(CreateTeam.name)
    await message.answer("Yangi team nomini kiriting:", reply_markup=cancel_kb())


@router.message(CreateTeam.name)
async def process_team_name(message: Message, state: FSMContext):
    team = await create_team(message.text)
    await state.clear()
    await message.answer(f"✅ Team yaratildi: {h(team.name)}", reply_markup=admin_main_menu())
