from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from db.models import TaskStatus
from db.requests import get_task_by_id, get_tasks_by_user, get_user_by_tg_id, update_task_status
from keyboards.user import task_action_kb
from utils.text import h

router = Router(name="user-tasks")

STATUS_LABELS = {
    "NEW": "🆕 Yangi",
    "IN_PROGRESS": "🔄 Jarayonda",
    "DONE": "✅ Bajarildi",
}


def _task_text(task) -> str:
    text = (
        f"📝 <b>#{task.id} {h(task.title)}</b>\n"
        f"{h(task.description)}\n\n"
        f"Status: {STATUS_LABELS[task.status.value]}"
    )
    if task.deadline:
        text += f"\n⏰ Deadline: {task.deadline.strftime('%Y-%m-%d %H:%M')}"
    return text


@router.message(F.text == "📋 Mening tasklarim")
async def my_tasks(message: Message):
    user = await get_user_by_tg_id(message.from_user.id)
    if not user:
        await message.answer("Siz hali ro'yxatdan o'tmagansiz. /start bosing.")
        return

    tasks = await get_tasks_by_user(user.id)
    if not tasks:
        await message.answer("Sizga biriktirilgan tasklar yo'q. 🎉")
        return

    for task in tasks:
        await message.answer(_task_text(task), reply_markup=task_action_kb(task))


@router.callback_query(F.data.startswith("taskstart:"))
async def task_start(callback: CallbackQuery):
    task_id = int(callback.data.split(":")[1])
    await update_task_status(task_id, TaskStatus.IN_PROGRESS)
    task = await get_task_by_id(task_id)
    await callback.message.edit_text(_task_text(task), reply_markup=task_action_kb(task))
    await callback.answer("Task boshlandi! 🔄")


@router.callback_query(F.data.startswith("taskdone:"))
async def task_done(callback: CallbackQuery):
    task_id = int(callback.data.split(":")[1])
    await update_task_status(task_id, TaskStatus.DONE)
    task = await get_task_by_id(task_id)
    await callback.message.edit_text(_task_text(task), reply_markup=task_action_kb(task))
    await callback.answer("Task yakunlandi! ✅")
