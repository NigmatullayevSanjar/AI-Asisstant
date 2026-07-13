from datetime import datetime

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from db.models import TaskStatus
from db.requests import (
    assign_task,
    create_task,
    delete_task,
    edit_task,
    get_all_tasks,
    get_all_users,
    get_user_by_tg_id,
)
from keyboards.admin import (
    admin_main_menu,
    cancel_kb,
    confirm_delete_kb,
    edit_task_fields_kb,
    tasks_inline_kb,
    users_inline_kb,
)
from middlewares.admin import IsAdmin
from states.states import AssignTask, CreateTask, DeleteTask, EditTask
from utils.text import h

router = Router(name="admin-tasks")
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())

DEADLINE_FORMAT = "%Y-%m-%d %H:%M"


# ---------------------------------------------------------------------------
# Create task
# ---------------------------------------------------------------------------


@router.message(F.text == "📝 Task yaratish")
async def start_create_task(message: Message, state: FSMContext):
    await state.set_state(CreateTask.title)
    await message.answer("Task nomini kiriting:", reply_markup=cancel_kb())


@router.message(CreateTask.title)
async def process_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(CreateTask.description)
    await message.answer("Task tavsifini kiriting (agar tavsif bo'lmasa, '-' deb yozing):")


@router.message(CreateTask.description)
async def process_description(message: Message, state: FSMContext):
    description = None if message.text.strip() == "-" else message.text
    await state.update_data(description=description)
    await state.set_state(CreateTask.deadline)
    await message.answer(
        f"Deadline sanasini kiriting ({DEADLINE_FORMAT.replace('%', '')} formatida, masalan "
        "2026-07-20 18:00) yoki '-' agar kerak bo'lmasa:"
    )


@router.message(CreateTask.deadline)
async def process_deadline(message: Message, state: FSMContext):
    deadline = None
    if message.text.strip() != "-":
        try:
            deadline = datetime.strptime(message.text.strip(), DEADLINE_FORMAT)
        except ValueError:
            await message.answer(
                "Sana formati noto'g'ri. Masalan: 2026-07-20 18:00\nQaytadan kiriting yoki '-' yozing:"
            )
            return
    await state.update_data(deadline=deadline)

    users = await get_all_users()
    if not users:
        await message.answer("Hozircha foydalanuvchilar yo'q. Avval user yarating.")
        await state.clear()
        return

    await state.set_state(CreateTask.assignee)
    await message.answer("Taskni kimga biriktiramiz?", reply_markup=users_inline_kb(users, prefix="assignee"))


@router.callback_query(CreateTask.assignee, F.data.startswith("assignee:"))
async def process_assignee(callback: CallbackQuery, state: FSMContext):
    user_id = int(callback.data.split(":")[1])
    data = await state.get_data()

    creator = await get_user_by_tg_id(callback.from_user.id)
    task = await create_task(
        title=data["title"],
        description=data.get("description"),
        created_by=creator.id if creator else None,
        assigned_to=user_id,
        deadline=data.get("deadline"),
    )
    await state.clear()

    await callback.message.edit_text(f"✅ Task yaratildi: #{task.id} {h(task.title)}")
    await callback.message.answer("Admin menyu:", reply_markup=admin_main_menu())
    await callback.answer()


# ---------------------------------------------------------------------------
# Assign task
# ---------------------------------------------------------------------------


@router.message(F.text == "📌 Assign Task")
async def start_assign_task(message: Message, state: FSMContext):
    tasks = await get_all_tasks()
    if not tasks:
        await message.answer("Hozircha tasklar yo'q.")
        return
    await state.set_state(AssignTask.task_id)
    await message.answer("Qaysi taskni biriktiramiz?", reply_markup=tasks_inline_kb(tasks, prefix="assigntask"))


@router.callback_query(AssignTask.task_id, F.data.startswith("assigntask:"))
async def choose_task_for_assign(callback: CallbackQuery, state: FSMContext):
    task_id = int(callback.data.split(":")[1])
    await state.update_data(task_id=task_id)

    users = await get_all_users()
    if not users:
        await callback.message.edit_text("Hozircha foydalanuvchilar yo'q.")
        await state.clear()
        await callback.answer()
        return

    await state.set_state(AssignTask.user_id)
    await callback.message.edit_text("Foydalanuvchini tanlang:", reply_markup=users_inline_kb(users, prefix="assignuser"))
    await callback.answer()


@router.callback_query(AssignTask.user_id, F.data.startswith("assignuser:"))
async def choose_user_for_assign(callback: CallbackQuery, state: FSMContext):
    user_id = int(callback.data.split(":")[1])
    data = await state.get_data()

    await assign_task(data["task_id"], user_id)
    await state.clear()

    await callback.message.edit_text("✅ Task muvaffaqiyatli biriktirildi.")
    await callback.message.answer("Admin menyu:", reply_markup=admin_main_menu())
    await callback.answer()


# ---------------------------------------------------------------------------
# Edit task
# ---------------------------------------------------------------------------


@router.message(F.text == "✏️ Edit Task")
async def start_edit_task(message: Message, state: FSMContext):
    tasks = await get_all_tasks()
    if not tasks:
        await message.answer("Hozircha tasklar yo'q.")
        return
    await state.set_state(EditTask.task_id)
    await message.answer("Qaysi taskni tahrirlaymiz?", reply_markup=tasks_inline_kb(tasks, prefix="edittask"))


@router.callback_query(EditTask.task_id, F.data.startswith("edittask:"))
async def choose_task_for_edit(callback: CallbackQuery, state: FSMContext):
    task_id = int(callback.data.split(":")[1])
    await state.update_data(task_id=task_id)
    await state.set_state(EditTask.field)
    await callback.message.edit_text("Qaysi maydonni o'zgartiramiz?", reply_markup=edit_task_fields_kb())
    await callback.answer()


@router.callback_query(EditTask.field, F.data.startswith("editfield:"))
async def choose_field_for_edit(callback: CallbackQuery, state: FSMContext):
    field = callback.data.split(":")[1]
    await state.update_data(field=field)
    await state.set_state(EditTask.value)

    prompts = {
        "title": "Yangi nomni kiriting:",
        "description": "Yangi tavsifni kiriting:",
        "deadline": f"Yangi deadlineni kiriting ({DEADLINE_FORMAT.replace('%', '')} formatida):",
        "status": "Yangi statusni kiriting (NEW / IN_PROGRESS / DONE):",
    }
    await callback.message.edit_text(prompts[field])
    await callback.answer()


@router.message(EditTask.value)
async def process_edit_value(message: Message, state: FSMContext):
    data = await state.get_data()
    field = data["field"]
    value: object = message.text.strip()

    if field == "deadline":
        try:
            value = datetime.strptime(value, DEADLINE_FORMAT)
        except ValueError:
            await message.answer("Sana formati noto'g'ri. Masalan: 2026-07-20 18:00")
            return
    elif field == "status":
        if value.upper() not in TaskStatus.__members__:
            await message.answer("Noto'g'ri status. NEW / IN_PROGRESS / DONE dan birini kiriting.")
            return
        value = TaskStatus[value.upper()]

    await edit_task(data["task_id"], **{field: value})
    await state.clear()
    await message.answer("✅ Task yangilandi.", reply_markup=admin_main_menu())


# ---------------------------------------------------------------------------
# Delete task
# ---------------------------------------------------------------------------


@router.message(F.text == "🗑 Delete Task")
async def start_delete_task(message: Message, state: FSMContext):
    tasks = await get_all_tasks()
    if not tasks:
        await message.answer("Hozircha tasklar yo'q.")
        return
    await state.set_state(DeleteTask.task_id)
    await message.answer("Qaysi taskni o'chiramiz?", reply_markup=tasks_inline_kb(tasks, prefix="deltask"))


@router.callback_query(DeleteTask.task_id, F.data.startswith("deltask:"))
async def choose_task_for_delete(callback: CallbackQuery, state: FSMContext):
    task_id = int(callback.data.split(":")[1])
    await state.update_data(task_id=task_id)
    await callback.message.edit_text(
        f"Task #{task_id} ni o'chirishga ishonchingiz komilmi?",
        reply_markup=confirm_delete_kb(task_id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("confirmdelete:"))
async def confirm_delete(callback: CallbackQuery, state: FSMContext):
    task_id = int(callback.data.split(":")[1])
    await delete_task(task_id)
    await state.clear()
    await callback.message.edit_text(f"✅ Task #{task_id} o'chirildi.")
    await callback.message.answer("Admin menyu:", reply_markup=admin_main_menu())
    await callback.answer()


@router.callback_query(F.data == "canceldelete")
async def cancel_delete(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Bekor qilindi.")
    await callback.answer()
