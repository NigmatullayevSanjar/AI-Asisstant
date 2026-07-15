from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from ai.openrouter import ask_ai
from db.requests import get_tasks_by_user, get_user_by_tg_id

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


@router.message(F.text & ~F.text.startswith("/"))
async def ai_handler(message: Message):
    text = message.text.strip()

    if not text:
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