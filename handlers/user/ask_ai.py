from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from ai.openrouter import ask_ai
from db.requests import get_tasks_by_user, get_user_by_tg_id

router = Router()


STATUS = {
    "NEW": "Yangi",
    "IN_PROGRESS": "Jarayonda",
    "DONE": "Bajarilgan"
}


@router.message(Command("ai"))
async def ai_handler(message: Message):

    text = message.text.replace("/ai", "").strip()

    if not text:
        await message.answer(
            "Masalan:\n"
            "/ai Bugun nima qilishim kerak?"
        )
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
                    if task.deadline else
                    "Belgilanmagan"
                )

                task_text += f"""
Task: {task.title}
Description: {task.description or "-"}
Status: {STATUS[task.status.value]}
Deadline: {deadline}

"""
        else:
            task_text = "User has no tasks."
    else:
        task_text = "User not found."

    prompt = f"""
You are Executive AI Assistant.

Current user tasks:

{task_text}

User question:

{text}

Answer in Uzbek.

If tasks exist:
- analyze them
- sort by importance
- warn about deadlines
- recommend what to do first

If no tasks:
help plan today's work.
"""

    answer = await ask_ai(prompt)

    await wait.edit_text(answer)