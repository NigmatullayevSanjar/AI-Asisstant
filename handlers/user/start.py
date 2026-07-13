from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from keyboards.user import user_main_menu

router = Router(name="user-start")


@router.message(Command("menu"))
async def user_menu(message: Message, state: FSMContext, is_admin: bool):
    if is_admin:
        # Admin's /menu is handled by handlers/admin/start.py
        return
    await state.clear()
    await message.answer("Asosiy menyu:", reply_markup=user_main_menu())
