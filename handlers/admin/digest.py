from datetime import datetime

from aiogram import Bot, F, Router
from aiogram.types import Message

from db.requests import get_all_users, get_tasks_by_user
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


def build_digest_text(tasks) -> str:
    weather = get_weather()

    if weather.get("cod") == 200:
        temp = weather["main"]["temp"]
        desc = weather["weather"][0]["description"].title()
    else:
        temp = "-"
        desc = "Noma'lum"

    today = datetime.now().strftime("%d.%m.%Y")

    total = len(tasks)
    done = sum(1 for task in tasks if task.status.value == "DONE")
    progress = sum(1 for task in tasks if task.status.value == "IN_PROGRESS")
    new = sum(1 for task in tasks if task.status.value == "NEW")

    lines = [
        "📨 <b>Kunlik Hisobot</b>",
        "",
        f"📅 <b>{today}</b>",
        f"🌤 <b>{temp}°C</b>",
        f"☁️ {desc}",
        "",
        "━━━━━━━━━━━━━━",
        "",
        "📊 <b>Statistika</b>",
        f"📌 Jami: {total}",
        f"🆕 Yangi: {new}",
        f"🔄 Jarayonda: {progress}",
        f"✅ Tugallangan: {done}",
        "",
        "━━━━━━━━━━━━━━",
        "",
        "📋 <b>Tasklar</b>",
        "",
    ]

    if not tasks:
        lines.append("🎉 Sizda hozircha tasklar yo'q.")
        return "\n".join(lines)

    for task in tasks:
        emoji = STATUS_EMOJI.get(task.status.value, "📌")

        line = (
            f"{emoji} <b>{h(task.title)}</b>\n"
            f"Status: {task.status.value}"
        )

        if task.deadline:
            line += (
                f"\n⏰ {task.deadline.strftime('%d.%m.%Y %H:%M')}"
            )

        lines.append(line)
        lines.append("")

    return "\n".join(lines)


@router.message(F.text == "📨 Daily Digest yuborish")
async def send_daily_digest_to_all(message: Message, bot: Bot):
    users = await get_all_users()

    sent = 0
    failed = 0

    for user in users:
        tasks = await get_tasks_by_user(user.id)

        try:
            await bot.send_message(
                user.tg_id,
                build_digest_text(tasks)
            )
            sent += 1

        except Exception:
            failed += 1

    await message.answer(
        f"✅ Digest yuborildi: {sent} ta foydalanuvchiga.\n"
        f"❌ Xatolik: {failed} ta."
    )