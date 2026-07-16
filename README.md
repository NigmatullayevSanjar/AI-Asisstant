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

## 📨 Daily Digest (yangilangan)

Endi digestda statistika/raqamlar yo'q. O'rniga har bir user o'ziga quyidagilarni ko'radi:
- 🎯 **Bugungi rejalar** — deadline'i bugun bo'lgan tasklar
- 📋 **Sizning faol tasklaringiz** — barcha NEW/IN_PROGRESS tasklar
- 👥 **Jamoangiz nima ish qilyapti** — o'z teamidagi boshqa a'zolarning faol tasklari

(Ob-havo qismi ilgarigidek qoldi.) Kod: `handlers/admin/digest.py -> build_digest_text(user)`.

## 📅 Google Calendar integratsiyasi

Admin biror taskka deadline qo'ysa (task yaratishda yoki keyin tahrirlashda),
shu deadline avtomatik umumiy Google Calendar'ga event sifatida yoziladi.
Task DONE bo'lsa yoki o'chirilsa — event ham kalendardan o'chadi.

Bu bitta umumiy "jamoa kalendari" orqali ishlaydi (Google Service Account),
ya'ni har bir xodim o'zining shaxsiy Google akkauntini ulashi shart emas —
faqat bitta kalendar bo'ladi va hammaning tasklari o'sha yerda ko'rinadi.

**Sozlash (bir martalik):**
1. https://console.cloud.google.com — yangi loyiha oching, **Google Calendar API**ni yoqing.
2. **IAM & Admin -> Service Accounts** bo'limidan yangi service account yarating,
   uning uchun JSON kalit yuklab oling (masalan `service_account.json` deb saqlang,
   `bot/` papkasi ichiga qo'ying — bu fayl `.gitignore`da, hech qachon git'ga tushmaydi).
3. Google Calendar'da (yangi kalendar ochsangiz ham bo'ladi) **Settings and sharing ->
   Share with specific people** bo'limidan o'sha service accountning emailini
   (JSON fayl ichidagi `client_email`, masalan `...@...iam.gserviceaccount.com`)
   qo'shing va huquq sifatida **"Make changes to events"** bering.
4. Shu kalendarning **Calendar ID**sini (Settings -> Integrate calendar) oling.
5. `.env` fayliga qo'shing:
   ```
   GOOGLE_CALENDAR_ID=sizning_kalendar_id@group.calendar.google.com
   GOOGLE_SERVICE_ACCOUNT_FILE=service_account.json
   ```
6. Agar bot allaqachon ishlab turgan (eski) bazaga ulanayotgan bo'lsangiz, deploy
   qilishdan oldin bir marta migratsiyani ishga tushiring (yangi `calendar_event_id`
   ustunini `tasks` jadvaliga qo'shish uchun):
   ```
   cd bot
   python -m scripts.migrate_add_calendar_column
   ```

Agar `GOOGLE_CALENDAR_ID` yoki `GOOGLE_SERVICE_ACCOUNT_FILE` bo'sh qoldirilsa,
kalendar sinxronizatsiyasi shunchaki o'chiq turadi — bot xatosiz, oddiy rejimda
ishlashda davom etadi (`utils/google_calendar.py`).
