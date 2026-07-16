from datetime import datetime

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from db.requests import create_task, edit_task, get_user_by_tg_id
from middlewares.admin import IsAdmin
from utils.date_parser import parse_datetime_from_text
from utils.google_calendar import is_enabled, sync_task_event
from utils.text import h

router = Router(name="quick-reminder")
router.message.filter(IsAdmin())


@router.message(F.text, ~F.text.startswith("/"))
async def quick_reminder(message: Message, state: FSMContext):
    # Agar user hozir biror FSM oqimida bo'lsa (task yaratish, tahrirlash va h.k.),
    # bu xabar o'sha oqimga tegishli — bu yerda aralashmaymiz.
    if await state.get_state() is not None:
        return

    dt, title = parse_datetime_from_text(message.text, datetime.now())
    if not dt:
        return

    user = await get_user_by_tg_id(message.from_user.id)
    if not user:
        return

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

    calendar_note = "\n📅 Google Calendar'ga qo'shildi." if event_id else ""
    if not is_enabled():
        calendar_note = "\n⚠️ Google Calendar ulanmagan — faqat task sifatida saqlandi."

    await message.answer(
        f"✅ Eslatma saqlandi:\n"
        f"📌 {h(task.title)}\n"
        f"🕒 {dt.strftime('%d.%m.%Y %H:%M')}"
        f"{calendar_note}"
    )
