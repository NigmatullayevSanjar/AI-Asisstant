from aiogram import F, Router
from aiogram.types import Message

from db.requests import get_user_by_tg_id
from handlers.admin.digest import build_digest_text

router = Router(name="user-digest")


@router.message(F.text == "📨 Daily Digest")
async def my_digest(message: Message):
    user = await get_user_by_tg_id(message.from_user.id)
    if not user:
        await message.answer("Siz hali ro'yxatdan o'tmagansiz. /start bosing.")
        return

    await message.answer(await build_digest_text(user))
