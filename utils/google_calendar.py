"""Google Calendar sync.

Har bir task uchun deadline belgilansa (yoki o'zgartirilsa), shu deadline'ga mos
Google Calendar eventi avtomatik yaratiladi/yangilanadi. Task o'chirilsa yoki
deadline olib tashlansa, event ham o'chiriladi.

Ishlashi uchun (bitta umumiy "jamoa kalendari" orqali, har bir user o'z Google
akkauntini ulashi shart emas):

1. https://console.cloud.google.com da yangi loyiha oching, "Google Calendar API"ni yoqing.
2. "Service Account" yarating -> unga JSON kalit yuklab oling.
3. Google Calendar'da (yoki yangi kalendar yaratib) uni service account emailiga
   ("...@...iam.gserviceaccount.com", JSON faylning ichida "client_email") ulashing:
   Settings -> Share with specific people -> "Make changes to events".
4. Kalendar ID'sini (Settings -> Integrate calendar -> Calendar ID) .env dagi
   GOOGLE_CALENDAR_ID ga yozing.
5. Kalitni ikki xil usulda berish mumkin:
   a) Lokal/VPS: JSON faylni serverga joylab, yo'lini GOOGLE_SERVICE_ACCOUNT_FILE ga yozing.
      (Masalan: GOOGLE_SERVICE_ACCOUNT_FILE=service_account.json)
   b) Railway/Render kabi platformalarda (fayl deploy qilinmaydi, git'ga ham tushmaydi):
      JSON faylning BUTUN mazmunini nusxalab, GOOGLE_SERVICE_ACCOUNT_JSON environment
      variable'ga joylashtiring. Bu bo'lsa, u ustuvor ishlatiladi.

Agar ikkalasi ham bo'sh bo'lsa, kalendar sinxronizatsiyasi shunchaki o'chiq turadi
va bot xatosiz ishlayveradi.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta

from config import config

logger = logging.getLogger(__name__)

TIMEZONE = "Asia/Tashkent"
DEFAULT_EVENT_MINUTES = 30

_service = None
_enabled = bool(
    config.google_calendar_id
    and (config.google_service_account_json or config.google_service_account_file)
)
_init_failed = False


def is_enabled() -> bool:
    return _enabled and not _init_failed


def _get_service():
    global _service, _init_failed
    if _service is not None:
        return _service
    if not _enabled or _init_failed:
        return None

    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build

        scopes = ["https://www.googleapis.com/auth/calendar"]

        if config.google_service_account_json:
            info = json.loads(config.google_service_account_json)
            credentials = service_account.Credentials.from_service_account_info(
                info, scopes=scopes
            )
        else:
            credentials = service_account.Credentials.from_service_account_file(
                config.google_service_account_file, scopes=scopes
            )

        _service = build("calendar", "v3", credentials=credentials, cache_discovery=False)
        return _service
    except Exception as e:
        _init_failed = True
        logger.warning(
            "Google Calendar ulanmadi (GOOGLE_SERVICE_ACCOUNT_FILE / GOOGLE_CALENDAR_ID "
            "tekshiring): %s",
            e,
        )
        return None


def _event_body(title: str, description: str | None, deadline: datetime, assignee_name: str | None) -> dict:
    end = deadline + timedelta(minutes=DEFAULT_EVENT_MINUTES)
    summary = f"📝 {title}" + (f" — {assignee_name}" if assignee_name else "")
    return {
        "summary": summary,
        "description": description or "",
        "start": {"dateTime": deadline.isoformat(), "timeZone": TIMEZONE},
        "end": {"dateTime": end.isoformat(), "timeZone": TIMEZONE},
    }


def _upsert_task_event_sync(
    title: str,
    description: str | None,
    deadline: datetime,
    assignee_name: str | None,
    existing_event_id: str | None,
) -> str | None:
    service = _get_service()
    if not service:
        return existing_event_id

    body = _event_body(title, description, deadline, assignee_name)

    try:
        if existing_event_id:
            event = (
                service.events()
                .update(calendarId=config.google_calendar_id, eventId=existing_event_id, body=body)
                .execute()
            )
        else:
            event = (
                service.events()
                .insert(calendarId=config.google_calendar_id, body=body)
                .execute()
            )
        return event["id"]
    except Exception as e:
        logger.warning("Calendar eventini yozib bo'lmadi: %s", e)
        return existing_event_id


def _delete_task_event_sync(event_id: str | None) -> None:
    service = _get_service()
    if not service or not event_id:
        return
    try:
        service.events().delete(calendarId=config.google_calendar_id, eventId=event_id).execute()
    except Exception as e:
        logger.warning("Calendar eventini o'chirib bo'lmadi: %s", e)


async def sync_task_event(
    title: str,
    description: str | None,
    deadline: datetime | None,
    assignee_name: str | None,
    existing_event_id: str | None,
) -> str | None:
    """Deadline bo'lsa event yaratadi/yangilaydi, bo'lmasa mavjud eventni o'chiradi.
    Har doim yangi calendar_event_id (yoki None) qaytaradi — buni Task.calendar_event_id
    ga saqlab qo'yish kerak."""
    if not is_enabled():
        return existing_event_id

    if deadline is None:
        if existing_event_id:
            await asyncio.to_thread(_delete_task_event_sync, existing_event_id)
        return None

    return await asyncio.to_thread(
        _upsert_task_event_sync, title, description, deadline, assignee_name, existing_event_id
    )


async def delete_task_event(event_id: str | None) -> None:
    if not is_enabled() or not event_id:
        return
    await asyncio.to_thread(_delete_task_event_sync, event_id)
