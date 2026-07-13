# Task Management Bot

aiogram 3.x + PostgreSQL (SQLAlchemy async) asosida qurilgan Telegram bot.
Admin va oddiy foydalanuvchilar uchun task boshqaruv tizimi.

## Imkoniyatlar

**Admin:**
- 👤 User yaratish
- 👥 Team yaratish
- 📝 Task yaratish
- 📌 Assign Task
- ✏️ Edit Task
- 🗑 Delete Task
- 📊 Statistics
- 📨 Daily Digest yuborish (barcha foydalanuvchilarga qo'lda)

**User:**
- 📋 Mening tasklarim
- ▶️ Start (IN_PROGRESS ga o'tkazish)
- ✅ Done (DONE ga o'tkazish)
- 📨 Daily Digest (o'zining kunlik hisoboti)
- 👤 Profil

Bundan tashqari har kuni soat **09:00** da (Asia/Tashkent) barcha foydalanuvchilarga
avtomatik digest yuboriladi (`utils/scheduler.py`).

## O'rnatish

1. PostgreSQL bazasini yarating:
   ```sql
   CREATE DATABASE taskbot;
   ```

2. Repozitoriyani/fayllarni serveringizga joylashtiring va kutubxonalarni o'rnating:
   ```bash
   pip install -r requirements.txt
   ```

3. `.env.example` faylidan nusxa olib `.env` yarating va to'ldiring:
   ```bash
   cp .env.example .env
   ```
   - `BOT_TOKEN` — @BotFather orqali olingan token
   - `ADMIN_IDS` — admin bo'ladigan foydalanuvchilarning Telegram ID lari (vergul bilan)
   - `DB_URL` — PostgreSQL ulanish manzili

4. Botni ishga tushiring:
   ```bash
   python main.py
   ```

   Jadval (tables) birinchi ishga tushishda avtomatik yaratiladi (`init_db()`).
   Production uchun Alembic migratsiyalaridan foydalanish tavsiya etiladi.

## Loyiha tuzilishi

```
bot/
├── handlers/
│   ├── admin/          # Faqat ADMIN_IDS yoki is_admin=True userlar uchun
│   │   ├── start.py     # /menu, bekor qilish
│   │   ├── users.py     # User/Team yaratish
│   │   ├── tasks.py     # Task CRUD + assign
│   │   ├── statistics.py
│   │   └── digest.py    # Qo'lda digest yuborish + build_digest_text()
│   ├── user/
│   │   ├── start.py
│   │   ├── tasks.py     # Mening tasklarim, Start/Done
│   │   ├── profile.py
│   │   └── digest.py
│   └── common/
│       └── register.py  # /start — ro'yxatdan o'tish
│
├── keyboards/
│   ├── admin.py
│   └── user.py
│
├── middlewares/
│   └── admin.py          # AdminMiddleware + IsAdmin filter
│
├── db/
│   ├── models.py          # User, Team, Task (SQLAlchemy)
│   ├── database.py        # Engine/session
│   └── requests.py        # CRUD funksiyalar
│
├── states/
│   └── states.py           # FSM states (CreateUser, CreateTask va h.k.)
│
├── utils/
│   └── scheduler.py         # APScheduler — avtomatik kunlik digest
│
├── config.py
├── main.py
├── requirements.txt
└── .env
```

## Kim admin bo'ladi?

Ikki yo'l bilan:
1. `.env` dagi `ADMIN_IDS` ro'yxatida bo'lish (statik, config orqali)
2. Bazadagi `users.is_admin = True` (dinamik — kelajakda admin panel orqali
   boshqa userlarni ham admin qilish mumkin)

`AdminMiddleware` har bir update uchun ikkalasini ham tekshirib, `is_admin`
flagini handlerlarga uzatadi.
