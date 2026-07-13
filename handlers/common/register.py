from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from db.requests import get_or_create_user
from keyboards.admin import admin_main_menu
from keyboards.user import user_main_menu
from utils.text import h

router = Router(name="common-register")


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, is_admin: bool):
    await state.clear()

    await get_or_create_user(
        tg_id=message.from_user.id,
        full_name=message.from_user.full_name,
        username=message.from_user.username,
        is_admin=is_admin,
    )

    name = h(message.from_user.full_name)

    if is_admin:
        await message.answer(
            f"Salom, {name}! 👋\n\n"
            "Siz <b>admin</b> sifatida tizimga kirdingiz.",
            reply_markup=admin_main_menu(),
        )
    else:
        await message.answer(
            f"Salom, {name}! 👋\n\n"
            "Xush kelibsiz, task management botiga.",
            reply_markup=user_main_menu(),
        )
