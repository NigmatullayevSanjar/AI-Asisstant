from datetime import datetime

from aiogram import Bot, F, Router
from aiogram.types import Message

from db.requests import get_all_users, get_tasks_by_user, get_team_tasks
from middlewares.admin import IsAdmin
from utils.text import h
from utils.weather import get_weather

router = Router(name="admin-digest")
router.message.filter(IsAdmin())

STATUS_EMOJI = {
    "NEW": "🆕",
    "IN_PROGRESS": "🔄",
    "DONE": "✅",
}


async def build_digest_text(user) -> str:
    """Builds a personal daily digest for `user`:
    - today's plans (tasks with a deadline today)
    - their own active tasks
    - what their teammates are currently working on
    No statistics/numbers block — just what's happening today.
    """
    weather = get_weather()
    if weather.get("cod") == 200:
        temp = weather["main"]["temp"]
        desc = weather["weather"][0]["description"].title()
    else:
        temp = "-"
        desc = "Noma'lum"

    today = datetime.now().date()
    today_str = datetime.now().strftime("%d.%m.%Y")

    tasks = await get_tasks_by_user(user.id)
    active_tasks = [t for t in tasks if t.status.value != "DONE"]
    today_tasks = [t for t in tasks if t.deadline and t.deadline.date() == today]

    lines = [
        "📨 <b>Kunlik Digest</b>",
        f"📅 {today_str}   🌤 {temp}°C, {desc}",
        "",
        "━━━━━━━━━━━━━━",
        "🎯 <b>Bugungi rejalar</b>",
    ]

    if today_tasks:
        for task in sorted(today_tasks, key=lambda t: t.deadline):
            emoji = STATUS_EMOJI.get(task.status.value, "📌")
            time_str = task.deadline.strftime("%H:%M")
            lines.append(f"{emoji} {time_str} — {h(task.title)}")
    else:
        lines.append("Bugunga belgilangan deadline yo'q.")

    lines += ["", "━━━━━━━━━━━━━━", "📋 <b>Sizning faol tasklaringiz</b>"]

    if active_tasks:
        for task in active_tasks:
            emoji = STATUS_EMOJI.get(task.status.value, "📌")
            deadline_str = (
                f" (⏰ {task.deadline.strftime('%d.%m %H:%M')})" if task.deadline else ""
            )
            lines.append(f"{emoji} {h(task.title)}{deadline_str}")
    else:
        lines.append("Faol tasklar yo'q. 🎉")

    if user.team_id:
        team_tasks = await get_team_tasks(user.team_id, exclude_user_id=user.id)
        active_team_tasks = [t for t in team_tasks if t.status.value != "DONE"]

        lines += ["", "━━━━━━━━━━━━━━", "👥 <b>Jamoangiz nima ish qilyapti</b>"]

        if active_team_tasks:
            by_user: dict[int, list] = {}
            for task in active_team_tasks:
                by_user.setdefault(task.assigned_to, []).append(task)

            for u_tasks in by_user.values():
                assignee = u_tasks[0].assignee
                name = h(assignee.full_name or assignee.username if assignee else "Noma'lum")
                lines.append(f"\n<b>{name}</b>")
                for task in u_tasks:
                    emoji = STATUS_EMOJI.get(task.status.value, "📌")
                    deadline_str = (
                        f" (⏰ {task.deadline.strftime('%d.%m %H:%M')})" if task.deadline else ""
                    )
                    lines.append(f"  {emoji} {h(task.title)}{deadline_str}")
        else:
            lines.append("Jamoada hozircha faol tasklar yo'q.")

    return "\n".join(lines)


@router.message(F.text == "📨 Daily Digest yuborish")
async def send_daily_digest_to_all(message: Message, bot: Bot):
    users = await get_all_users()

    sent = 0
    failed = 0

    for user in users:
        text = await build_digest_text(user)
        try:
            await bot.send_message(user.tg_id, text)
            sent += 1
        except Exception:
            failed += 1

    await message.answer(
        f"✅ Digest yuborildi: {sent} ta foydalanuvchiga.\n"
        f"❌ Xatolik: {failed} ta."
    )
