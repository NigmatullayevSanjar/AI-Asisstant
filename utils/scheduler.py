import logging

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from db.requests import get_all_users, get_tasks_by_user
from handlers.admin.digest import build_digest_text

logger = logging.getLogger(__name__)


async def send_digest_job(bot: Bot) -> None:
    users = await get_all_users()
    for user in users:
        tasks = await get_tasks_by_user(user.id)
        try:
            await bot.send_message(user.tg_id, build_digest_text(tasks))
        except Exception as e:
            logger.warning("Digestni %s ga yuborib bo'lmadi: %s", user.tg_id, e)


def setup_scheduler(bot: Bot) -> AsyncIOScheduler:
    """Sends every user their daily digest automatically at 09:00 (Asia/Tashkent)."""
    scheduler = AsyncIOScheduler(timezone="Asia/Tashkent")
    scheduler.add_job(send_digest_job, "cron", hour=9, minute=0, kwargs={"bot": bot})
    scheduler.start()
    return scheduler
