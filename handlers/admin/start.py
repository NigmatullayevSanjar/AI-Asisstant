from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from keyboards.admin import admin_main_menu
from middlewares.admin import IsAdmin

router = Router(name="admin-start")
router.message.filter(IsAdmin())


@router.message(Command("menu"))
async def admin_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Admin menyu:", reply_markup=admin_main_menu())


@router.message(F.text == "❌ Bekor qilish")
async def cancel_action(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Bekor qilindi.", reply_markup=admin_main_menu())
