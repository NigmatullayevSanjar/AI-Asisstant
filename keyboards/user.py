from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from db.models import Task


def user_main_menu() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="📋 Mening tasklarim")
    builder.button(text="📨 Daily Digest")
    builder.button(text="👤 Profil")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


def task_action_kb(task: Task) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if task.status.value == "NEW":
        builder.button(text="▶️ Start", callback_data=f"taskstart:{task.id}")
    if task.status.value == "IN_PROGRESS":
        builder.button(text="✅ Done", callback_data=f"taskdone:{task.id}")
    builder.adjust(1)
    return builder.as_markup()
