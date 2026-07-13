from aiogram import F, Router
from aiogram.types import Message

from db.requests import get_team_by_id, get_tasks_by_user, get_user_by_tg_id
from utils.text import h

router = Router(name="user-profile")


@router.message(F.text == "👤 Profil")
async def show_profile(message: Message):
    user = await get_user_by_tg_id(message.from_user.id)
    if not user:
        await message.answer("Siz hali ro'yxatdan o'tmagansiz. /start bosing.")
        return

    tasks = await get_tasks_by_user(user.id)
    team = await get_team_by_id(user.team_id) if user.team_id else None

    lines = ["👤 <b>Profil</b>\n", f"Ism: {h(user.full_name)}"]
    if user.username:
        lines.append(f"Username: @{h(user.username)}")
    lines.append(f"Team: {h(team.name) if team else '—'}")
    lines.append(f"Rol: {'Admin' if user.is_admin else 'Foydalanuvchi'}")
    lines.append(f"\n📝 Jami tasklar: {len(tasks)}")

    await message.answer("\n".join(lines))
