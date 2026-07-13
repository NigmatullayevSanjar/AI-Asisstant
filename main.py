import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import config
from db.database import init_db
from handlers.admin import digest as admin_digest
from handlers.admin import start as admin_start
from handlers.admin import statistics as admin_statistics
from handlers.admin import tasks as admin_tasks
from handlers.admin import users as admin_users
from handlers.common import register
from handlers.user import digest as user_digest
from handlers.user import profile as user_profile
from handlers.user import start as user_start
from handlers.user import tasks as user_tasks
from middlewares.admin import AdminMiddleware
from utils.scheduler import setup_scheduler
from handlers.user import ask_ai

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


async def main() -> None:
    bot = Bot(token=config.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    dp.message.outer_middleware(AdminMiddleware())
    dp.callback_query.outer_middleware(AdminMiddleware())
    dp.include_router(register.router)
    
    
    dp.include_router(admin_start.router)
    dp.include_router(admin_users.router)
    dp.include_router(admin_tasks.router)
    dp.include_router(admin_statistics.router)
    dp.include_router(admin_digest.router)

    dp.include_router(user_start.router)
    dp.include_router(user_tasks.router)
    dp.include_router(user_profile.router)
    dp.include_router(user_digest.router)
    dp.include_router(ask_ai.router)

    await init_db()
    setup_scheduler(bot)

    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Bot ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
