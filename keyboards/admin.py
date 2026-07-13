from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def admin_main_menu() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="👤 User yaratish")
    builder.button(text="👥 Team yaratish")
    builder.button(text="📝 Task yaratish")
    builder.button(text="📌 Assign Task")
    builder.button(text="✏️ Edit Task")
    builder.button(text="🗑 Delete Task")
    builder.button(text="📊 Statistics")
    builder.button(text="📨 Daily Digest yuborish")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


def cancel_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="❌ Bekor qilish")
    return builder.as_markup(resize_keyboard=True)


def teams_inline_kb(teams) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for team in teams:
        builder.button(text=team.name, callback_data=f"team:{team.id}")
    builder.button(text="Bo'sh (team yo'q)", callback_data="team:none")
    builder.adjust(1)
    return builder.as_markup()


def users_inline_kb(users, prefix: str = "user") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for user in users:
        label = user.full_name or user.username or str(user.tg_id)
        builder.button(text=label, callback_data=f"{prefix}:{user.id}")
    builder.adjust(1)
    return builder.as_markup()


def tasks_inline_kb(tasks, prefix: str = "task") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for task in tasks:
        builder.button(text=f"#{task.id} {task.title}", callback_data=f"{prefix}:{task.id}")
    builder.adjust(1)
    return builder.as_markup()


def edit_task_fields_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Nomi", callback_data="editfield:title")
    builder.button(text="Tavsif", callback_data="editfield:description")
    builder.button(text="Deadline", callback_data="editfield:deadline")
    builder.button(text="Status", callback_data="editfield:status")
    builder.adjust(2)
    return builder.as_markup()


def confirm_delete_kb(task_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Ha, o'chirish", callback_data=f"confirmdelete:{task_id}")
    builder.button(text="❌ Bekor qilish", callback_data="canceldelete")
    builder.adjust(1)
    return builder.as_markup()
