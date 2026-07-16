"""Bir martalik migratsiya: mavjud 'tasks' jadvaliga calendar_event_id ustunini qo'shadi.

init_db() faqat yo'q jadvallarni yaratadi, mavjud jadvalga yangi ustun qo'shmaydi.
Shuning uchun bu skriptni deploy qilishdan oldin BIR MARTA qo'lda ishga tushiring:

    python -m scripts.migrate_add_calendar_column

(bot/ papkasi ichidan turib ishga tushiring, chunki config.py shu yerdan DB_URL ni oladi)
"""

import asyncio

from sqlalchemy import text

from db.database import engine


async def main() -> None:
    async with engine.begin() as conn:
        await conn.execute(
            text("ALTER TABLE tasks ADD COLUMN IF NOT EXISTS calendar_event_id VARCHAR(255)")
        )
    print("✅ calendar_event_id ustuni qo'shildi (yoki allaqachon bor edi).")


if __name__ == "__main__":
    asyncio.run(main())
