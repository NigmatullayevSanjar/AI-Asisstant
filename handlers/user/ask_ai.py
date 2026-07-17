from datetime import datetime

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from ai.openrouter import ask_ai
from db.requests import create_task, edit_task, get_tasks_by_user, get_user_by_tg_id
from utils.date_parser import parse_datetime_from_text
from utils.google_calendar import is_enabled, sync_task_event
from utils.text import h

router = Router()

STATUS = {
    "NEW": "Yangi",
    "IN_PROGRESS": "Jarayonda",
    "DONE": "Bajarilgan",
}


@router.message(Command("ai"))
async def ai_command(message: Message):
    await message.answer(
        "🤖 Endi /ai yozish shart emas.\n\n"
        "Menga oddiy xabar yuboring, men javob beraman."
    )


async def _try_quick_reminder(message: Message, is_admin: bool) -> bool:
    """Agar xabarda sana+vaqt bo'lsa (va yuboruvchi admin bo'lsa), uni task
    sifatida saqlab, Google Calendar'ga qo'shadi. Muvaffaqiyatli bo'lsa True
    qaytaradi (bu holda AI logikasi ishlamaydi)."""
    if not is_admin:
        return False

    dt, title = parse_datetime_from_text(message.text.strip(), datetime.now())
    if not dt:
        return False

    user = await get_user_by_tg_id(message.from_user.id)
    if not user:
        return False

    task = await create_task(
        title=title,
        description=None,
        created_by=user.id,
        assigned_to=user.id,
        deadline=dt,
    )

    assignee_name = user.full_name or user.username
    event_id = await sync_task_event(
        title=task.title,
        description=task.description,
        deadline=task.deadline,
        assignee_name=assignee_name,
        existing_event_id=None,
    )
    if event_id:
        await edit_task(task.id, calendar_event_id=event_id)

    if event_id:
        calendar_note = "\n📅 Google Calendar'ga qo'shildi."
    elif not is_enabled():
        calendar_note = "\n⚠️ Google Calendar ulanmagan — faqat task sifatida saqlandi."
    else:
        calendar_note = "\n⚠️ Calendar'ga qo'shishda xatolik bo'ldi — faqat task sifatida saqlandi."

    await message.answer(
        f"✅ Eslatma saqlandi:\n"
        f"📌 {h(task.title)}\n"
        f"🕒 {dt.strftime('%d.%m.%Y %H:%M')}"
        f"{calendar_note}"
    )
    return True


@router.message(F.text & ~F.text.startswith("/"))
async def ai_handler(message: Message, is_admin: bool):
    text = message.text.strip()

    if not text:
        return

    if await _try_quick_reminder(message, is_admin):
        return

    wait = await message.answer("🤖 O'ylayapman...")

    user = await get_user_by_tg_id(message.from_user.id)

    task_text = ""

    if user:
        tasks = await get_tasks_by_user(user.id)

        if tasks:
            for task in tasks:
                deadline = (
                    task.deadline.strftime("%Y-%m-%d %H:%M")
                    if task.deadline
                    else "Belgilanmagan"
                )

                task_text += f"""
Task: {task.title}
Description: {task.description or "-"}
Status: {STATUS.get(task.status.value, task.status.value)}
Deadline: {deadline}

"""
        else:
            task_text = "User has no tasks."
    else:
        task_text = "User not found."

    prompt = f"""
You are an Executive AI Assistant.

Current user tasks:

{task_text}

User message:

{text}

Answer in Uzbek.

If tasks exist:
- analyze them
- sort them by priority
- warn about deadlines
- recommend what to do first

If there are no tasks:
help plan today's work.
"""

    answer = await ask_ai(prompt)

    await wait.edit_text(answer)
