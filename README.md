# Qur'on Tilovat Tekshiruvchi (Iqra) — Telegram Bot + Web App

Qur'on tilovatini sun'iy intellekt va tajvid qoidalari asosida tekshiruvchi zamonaviy Telegram Mini App va Bot platformasi.

---

## 🌟 Tizim Imkoniyatlari

1. **Telegram Mini App (Frontend):**
   - 1-114 Suralar va oyatlar tanlagichi.
   - Uthmanic xattotlikdagi arabcha matn (Amiri Quran shrifti).
   - O'zbekcha ma'no tarjimasi va fonetik transliteratsiyasi.
   - Rasmiy qorilar (Mishary Rashid Alafasy) qiroatini tinglash.
   - Ovoz yozish (MediaRecorder) va real-time audio soundwave vizualizatori.
   - **Rangli so'zma-so'z natija:**
     - 🟢 **Yashil:** To'g'ri o'qilgan so'z.
     - 🟡 **Sariq:** So'z to'g'ri, lekin tajvid kamchiligi bor (Madd, G'unna, Qalqala).
     - 🔴 **Qizil:** Tushirib qoldirilgan yoki adashtirilgan so'z.
   - O'zlashtirish foizi va keyingi oyatga avtomatik o'tish.

2. **Django REST Backend:**
   - Foydalanuvchilar, suralar, oyatlar, tilovat urinishlari va progress boshqaruvi.
   - `python manage.py import_quran` orqali Quran.com va Tanzil API'dan ma'lumotlarni tortish.

3. **FastAPI ASR & Tajweed Microservice:**
   - Tarteel Whisper (`tarteel-ai/whisper-base-ar-quran`) modeli.
   - Phonetic & Word-level Forced Alignment.
   - Qoidalarga asoslangan Tajvid tekshiruvi (Madd, G'unna, Qalqala, Iqlab, Idg'om).
   - GPU (CUDA) va CPU avtomatik aniqlanishi va ishlashi.

4. **aiogram 3 Telegram Bot:**
   - `/start` komandasi orqali foydalanuvchini ro'yxatga olib, Web App ochish tugmasini beradi.
   - `/progress` orqali shaxsiy statistika (o'qilgan oyatlar soni, o'rtacha ball).

---

## 🚀 Ishga Tushirish

### 1. Talablar
- Python 3.10+
- (Ixtiyoriy) PostgreSQL va GPU server

### 2. O'rnatish
```bash
pip install -r backend/requirements.txt
pip install -r asr_service/requirements.txt
pip install -r bot/requirements.txt
```

### 3. Ma'lumotlar bazasini tayyorlash va Suralarni yuklash
```bash
cd backend
python manage.py migrate
python manage.py import_quran --sample
```
*(Barcha 114 surani tortish uchun: `python manage.py import_quran --juz-amma`)*

### 4. Barcha xizmatlarni birgalikda ishga tushirish
Loyiha asosiy papkasida:
```bash
python run_dev.py
```

Ilova manzillari:
- **Telegram Web App:** [http://localhost:8000/](http://localhost:8000/)
- **Django REST API:** [http://localhost:8000/api/](http://localhost:8000/api/)
- **ASR Microservice Docs:** [http://127.0.0.1:8001/docs](http://127.0.0.1:8001/docs)

### 5. Telegram Botni ulash
`.env` faylini oching va `@BotFather`dan olingan bot tokenini yozing:
```env
BOT_TOKEN=123456789:ABCdef...
WEBAPP_URL=https://your-ngrok-or-domain.com/
```
Keyin botni ishga tushiring:
```bash
python -m bot.bot
```

---

## 🚂 Railway Serveriga Joylash (Deploy Guide)

Loyiha Railway platformasida to'liq avtomatlashtirilgan holda ishlashga moslashtirilgan (`start.sh`, `nixpacks.toml`, `railway.json`, `Dockerfile` va `Procfile` mavjud).

### 1-qadam: GitHub orqali Railway'ga ulash
1. [Railway.app](https://railway.app) ga kiring va hisobingizga kiring.
2. **"New Project"** -> **"Deploy from GitHub repo"** tugmasini bosing.
3. `abdurahmonpy/qurontutor` repozitoriyasini tanlang.

### 2-qadam: Ma'lumotlar bazasini qo'shish (PostgreSQL)
1. Loyiha panelida **"+ New"** -> **"Database"** -> **"Add PostgreSQL"** ni tanlang.
2. Railway avtomatik ravishda `DATABASE_URL` muhit o'zgaruvchisini ilovangizga ulab beradi.

### 3-qadam: Muhit o'zgaruvchilarini (Variables) kiritish
Ilovaning **"Variables"** bo'limiga kiring va quyidagilarni kiriting:
- `BOT_TOKEN` = `YOUR_BOT_TOKEN_HERE` (BotFather bergan token)
- `DEBUG` = `False`
- `DJANGO_SECRET_KEY` = `ixtiyoriy_uzun_maxfiy_kalit_yozing`
- `WEBAPP_URL` = `https://<sizning-railway-domeningiz>.up.railway.app/`
- `API_BASE_URL` = `https://<sizning-railway-domeningiz>.up.railway.app/api`

### 4-qadam: Ommaviy Domen yaratish (Networking)
1. Ilovaning **"Settings"** -> **"Networking"** bo'limiga o'ting.
2. **"Generate Domain"** tugmasini bosing (masalan: `qurontutor-production.up.railway.app`).
3. Olingan `https://...` manzilini yuqoridagi `WEBAPP_URL` o'zgaruvchisiga saqlang.

### 5-qadam: Avtomatik Ishga Tushish
Railway deploy jarayonida avtomatik tarzda:
- Barcha bog'liqliklarni (`requirements.txt`) o'rnatadi.
- Ma'lumotlar bazasi migratsiyalarini (`migrate`) bajaradi.
- Qur'on suralarini (`import_quran --sample`) bazaga yuklaydi.
- Statik fayllarni (`collectstatic`) jamlaydi.
- Telegram Botni orqa fonda (`bot.bot`) va Gunicorn veb-serverini ishga tushiradi.

