"""Erkin matndan sana + vaqt + sarlavhani ajratib oladi.

Masalan: "16 iyul 18:00 trenirovka" -> (2026-07-16 18:00, "trenirovka")
Yoki: "ertaga soat 9 da uchrashuv" -> (ertangi kun 09:00, "uchrashuv")

Agar matnda tushunarli sana YOKI vaqt topilmasa, (None, matn) qaytaradi —
bu holda chaqiruvchi kod bu matnni oddiy xabar/AI so'rovi deb qabul qilishi kerak.
"""

import re
from datetime import date, datetime, timedelta

MONTHS = {
    "yanvar": 1,
    "fevral": 2,
    "mart": 3,
    "aprel": 4,
    "may": 5,
    "iyun": 6,
    "iyul": 7,
    "avgust": 8,
    "sentyabr": 9,
    "sentabr": 9,
    "oktyabr": 10,
    "noyabr": 11,
    "dekabr": 12,
}


def parse_datetime_from_text(text: str, now: datetime) -> tuple[datetime | None, str]:
    lowered = text.lower()
    date_part: date | None = None
    date_span: tuple[int, int] | None = None

    m = re.search(r"\bbugun\b", lowered)
    if m:
        date_part = now.date()
        date_span = m.span()
    else:
        m = re.search(r"\bertaga\b", lowered)
        if m:
            date_part = (now + timedelta(days=1)).date()
            date_span = m.span()
        else:
            m = re.search(r"\bindinga\b", lowered)
            if m:
                date_part = (now + timedelta(days=2)).date()
                date_span = m.span()

    if date_part is None:
        month_pattern = "|".join(MONTHS.keys())
        m = re.search(rf"\b(\d{{1,2}})[\s\-]+({month_pattern})\w*\b", lowered)
        if m:
            day = int(m.group(1))
            month = MONTHS[m.group(2)]
            year = now.year
            try:
                candidate = date(year, month, day)
                if candidate < now.date():
                    candidate = date(year + 1, month, day)
                date_part = candidate
                date_span = m.span()
            except ValueError:
                date_part = None

    if date_part is None:
        m = re.search(r"\b(\d{1,2})[./](\d{1,2})(?:[./](\d{2,4}))?\b", text)
        if m:
            day = int(m.group(1))
            month = int(m.group(2))
            year = int(m.group(3)) if m.group(3) else now.year
            if year < 100:
                year += 2000
            try:
                date_part = date(year, month, day)
                date_span = m.span()
            except ValueError:
                date_part = None

    if date_part is None:
        return None, text

    search_text = lowered
    if date_span:
        start, end = date_span
        search_text = lowered[:start] + (" " * (end - start)) + lowered[end:]

    time_match = re.search(r"soat\s*(\d{1,2})(?:[:.](\d{2}))?", search_text)
    if not time_match:
        time_match = re.search(r"\b(\d{1,2}):(\d{2})\b", search_text)
    if not time_match:
        time_match = re.search(r"\b(\d{1,2})\.(\d{2})\b", search_text)

    if not time_match:
        return None, text

    hour = int(time_match.group(1))
    minute = int(time_match.group(2)) if time_match.group(2) else 0
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        return None, text

    dt = datetime(date_part.year, date_part.month, date_part.day, hour, minute)

    spans = sorted([date_span, time_match.span()], key=lambda s: s[0])
    title = text
    for start, end in reversed(spans):
        title = title[:start] + title[end:]
    title = re.sub(r"\bsoat\b", "", title, flags=re.IGNORECASE)
    title = re.sub(r"\bda\b", "", title, flags=re.IGNORECASE)
    title = re.sub(r"\s+", " ", title).strip(" -,.\u2013\u2014")

    if not title:
        title = "Eslatma"

    return dt, title
