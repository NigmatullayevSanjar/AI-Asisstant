import random

QUOTES = [
    "Consistency beats motivation.",
    "Kichik qadamlar katta natijalarga olib keladi.",
    "Bugungi mehnat — ertangi natija.",
    "Harakat qilmagan hech narsaga erisha olmaydi.",
    "Discipline is choosing between what you want now and what you want most.",
    "Vaqtni boshqarish — hayotni boshqarish demakdir.",
    "Progress, not perfection.",
    "Har bir kichik ish katta maqsadga bir qadam yaqinlashtiradi.",
    "Bugun qilingan ish — ertangi erkinlik.",
    "Focus on being productive instead of busy.",
    "Muvaffaqiyat — kichik harakatlarning yig'indisi.",
    "Ishni ertaga qoldirma, bugun boshla.",
]


def get_daily_quote() -> str:
    return random.choice(QUOTES)
