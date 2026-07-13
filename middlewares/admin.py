from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject
from aiogram.types import User as TgUser

from config import config
from db.requests import get_user_by_tg_id


class AdminMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        tg_user: TgUser | None = data.get("event_from_user")
        if tg_user:
            db_user = await get_user_by_tg_id(tg_user.id)
            data["db_user"] = db_user
            data["is_admin"] = bool(tg_user.id in config.admin_ids or (db_user and db_user.is_admin))
        else:
            data["db_user"] = None
            data["is_admin"] = False
        return await handler(event, data)


class IsAdmin(BaseFilter):
    async def __call__(self, event: TelegramObject, is_admin: bool) -> bool:
        return is_admin
