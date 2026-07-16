import httpx
from config import config

URL = "https://openrouter.ai/api/v1/chat/completions"


SYSTEM_PROMPT = """
Siz Executive AI Assistantsiz.

Sizning vazifangiz:

- Xodimning vazifalarini tahlil qilish.
- Deadline va ustuvorlikni hisobga olish.
- Kunlik reja tuzish.
- Samaradorlik bo'yicha tavsiyalar berish.
- Dasturlash va biznes savollariga javob berish.

Qoidalar:

1. Faqat o'zbek tilida javob bering.
2. Tabiiy va ravon yozing.
3. Inglizcha yoki ruscha iboralarni aralashtirmang.
4. Hech qachon mavjud bo'lmagan ma'lumotni o'ylab topmang.
5. Agar vazifalar berilgan bo'lsa, avval ularni tahlil qiling.
6. Deadline yaqin bo'lsa ogohlantiring.
7. Muhim vazifalarni birinchi o'ringa qo'ying.
8. Javobni quyidagi formatda yozing:

📌 Tahlil

...

🎯 Tavsiya

...

⚡ Keyingi qadam

...

Jadval ishlatmang.
"""


async def ask_ai(prompt: str):

    headers = {
        "Authorization": f"Bearer {config.openrouter_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": config.model,
        "temperature": 0.3,
        "max_tokens": 1000,
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    async with httpx.AsyncClient(timeout=60) as client:

        response = await client.post(
            URL,
            headers=headers,
            json=payload
        )

        response.raise_for_status()

        data = response.json()

        return data["choices"][0]["message"]["content"]


DIGEST_SYSTEM_PROMPT = """
Siz qisqa va aniq tavsiya beruvchi yordamchisiz.

Sizga foydalanuvchining bugungi va yaqin kunlardagi vazifalari beriladi.
Faqat BITTA qisqa jumla bilan (10-15 so'zdan oshmasin) o'zbek tilida javob bering:
bugun eng birinchi qilinishi kerak bo'lgan vazifani ayting va sababini qisqa
tushuntiring. Formatlash, ro'yxat, emoji, sarlavha ishlatmang — faqat bitta
oddiy jumla yozing.
"""


async def get_digest_recommendation(task_summary: str) -> str:
    headers = {
        "Authorization": f"Bearer {config.openrouter_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": config.model,
        "temperature": 0.3,
        "max_tokens": 80,
        "messages": [
            {"role": "system", "content": DIGEST_SYSTEM_PROMPT},
            {"role": "user", "content": task_summary},
        ],
    }

    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()