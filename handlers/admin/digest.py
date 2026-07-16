from datetime import datetime

from aiogram import Bot, F, Router
from aiogram.types import Message

from ai.openrouter import get_digest_recommendation
from db.requests import get_all_users, get_tasks_by_user, get_team_tasks
from middlewares.admin import IsAdmin
from utils.quotes import get_daily_quote
from utils.text import h
from utils.weather import get_weather

router = Router(name="admin-digest")
router.message.filter(IsAdmin())

SEPARATOR = "━━━━━━━━━━━━━━"

WEEKDAYS_UZ = {
    0: "Dushanba",
    1: "Seshanba",
    2: "Chorshanba",
    3: "Payshanba",
    4: "Juma",
    5: "Shanba",
    6: "Yakshanba",
}

MONTHS_UZ = {
    1: "yanvar",
    2: "fevral",
    3: "mart",
    4: "aprel",
    5: "may",
    6: "iyun",
    7: "iyul",
    8: "avgust",
    9: "sentyabr",
    10: "oktyabr",
    11: "noyabr",
    12: "dekabr",
}


def _section(title: str, body_lines: list[str]) -> str:
    return title + "\n\n" + "\n\n".join(body_lines)


async def build_digest_text(user) -> str:
    now = datetime.now()
    today = now.date()

    weather = get_weather()
    if weather.get("cod") == 200:
        temp = round(weather["main"]["temp"])
        desc = weather["weather"][0]["description"].title()
    else:
        temp = "-"
        desc = "Noma'lum"

    tasks = await get_tasks_by_user(user.id)
    active_tasks = [t for t in tasks if t.status.value != "DONE"]
    today_tasks = sorted(
        [t for t in tasks if t.deadline and t.deadline.date() == today],
        key=lambda t: t.deadline,
    )
    urgent_tasks = sorted(
        [t for t in active_tasks if t.deadline],
        key=lambda t: t.deadline,
    )[:3]

    name = user.full_name or user.username or "do'stim"

    header = "\n\n".join(
        [
            f"🌅 Xayrli tong, {h(name)}!",
            f"📅 {WEEKDAYS_UZ[now.weekday()]} | {now.day}-{MONTHS_UZ[now.month]}",
            f"🌤 {temp}°C\n{desc}",
        ]
    )

    sections = []

    if today_tasks:
        lines = [f"{t.deadline.strftime('%H:%M')} {h(t.title)}" for t in today_tasks]
    else:
        lines = ["Bugunga reja belgilanmagan."]
    sections.append(_section("🗓 Bugungi reja", lines))

    if urgent_tasks:
        lines = [h(t.title) for t in urgent_tasks]
    else:
        lines = ["Shoshilinch vazifalar yo'q. 🎉"]
    sections.append(_section("🔥 Muhim vazifalar", lines))

    if user.team_id:
        team_tasks = await get_team_tasks(user.team_id, exclude_user_id=user.id)
        active_team_tasks = [t for t in team_tasks if t.status.value != "DONE"]

        by_user: dict[int, list] = {}
        for task in active_team_tasks:
            by_user.setdefault(task.assigned_to, []).append(task)

        if by_user:
            lines = []
            for u_tasks in by_user.values():
                assignee = u_tasks[0].assignee
                assignee_name = h(assignee.full_name or assignee.username) if assignee else "?"
                lines.append(f"{assignee_name} {h(u_tasks[0].title)}")
        else:
            lines = ["Jamoada hozircha faol tasklar yo'q."]
        sections.append(_section("👥 Jamoa", lines))

    task_summary_parts = [
        f"- {t.title} (deadline: {t.deadline.strftime('%d.%m %H:%M') if t.deadline else 'yoq'})"
        for t in active_tasks
    ]
    task_summary = "\n".join(task_summary_parts) if task_summary_parts else "Faol vazifalar yo'q."

    try:
        recommendation = await get_digest_recommendation(task_summary)
    except Exception:
        if urgent_tasks:
            recommendation = f"Bugun \"{urgent_tasks[0].title}\"ni birinchi navbatda bajarish tavsiya etiladi."
        else:
            recommendation = "Bugun uchun shoshilinch vazifalar yo'q — rejalashtirish uchun yaxshi kun."

    sections.append(_section("💡 AI tavsiya", [recommendation]))
    sections.append("💬\n\n" + get_daily_quote())

    body = f"\n\n{SEPARATOR}\n\n".join(sections)
    return f"{header}\n\n{SEPARATOR}\n\n{body}"


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
