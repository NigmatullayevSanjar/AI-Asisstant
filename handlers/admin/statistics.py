from aiogram import F, Router
from aiogram.types import Message

from db.requests import get_statistics
from middlewares.admin import IsAdmin

router = Router(name="admin-statistics")
router.message.filter(IsAdmin())


@router.message(F.text == "📊 Statistics")
async def show_statistics(message: Message):
    stats = await get_statistics()
    text = (
        "📊 <b>Statistika</b>\n\n"
        f"👥 Foydalanuvchilar: {stats['users']}\n"
        f"🏷 Teamlar: {stats['teams']}\n\n"
        f"📝 Jami tasklar: {stats['total_tasks']}\n"
        f"🆕 Yangi: {stats['new']}\n"
        f"🔄 Jarayonda: {stats['in_progress']}\n"
        f"✅ Bajarilgan: {stats['done']}"
    )
    await message.answer(text)
