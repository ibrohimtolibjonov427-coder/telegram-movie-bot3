# 🎬 Kino Bot — O'rnatish va Ishga Tushirish Qo'llanmasi

## 📁 Fayllar
- `bot.py` — Asosiy bot kodi
- `database.py` — SQLite baza
- `requirements.txt` — Kerakli kutubxonalar

---

## ⚙️ Sozlash

### 1. Bot Token olish
1. Telegram'da [@BotFather](https://t.me/BotFather) ga yozing
2. `/newbot` buyrug'ini yuboring
3. Bot nomini kiriting
4. Token oling (masalan: `7123456789:AAFxxxxxx`)

### 2. Admin ID olish
1. [@userinfobot](https://t.me/userinfobot) ga `/start` yuboring
2. Sizning Telegram ID raqamingiz ko'rinadi (masalan: `123456789`)

### 3. bot.py ni sozlash
`bot.py` faylida quyidagi qatorlarni o'zgartiring:
```python
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "123456789").split(",")))
```
`YOUR_BOT_TOKEN_HERE` — o'z tokeningiz
`123456789` — o'z Telegram ID raqamingiz

---

## 🚀 Lokal ishga tushirish

```bash
pip install -r requirements.txt
python bot.py
```

---

## ☁️ TEKIN SERVER (Deploy) Variantlari

### ✅ 1. Koyeb (Eng oson, tavsiya etiladi)
- Sayt: https://koyeb.com
- Tekin: ✅ (Free tier bor)
- Steps:
  1. GitHub'ga kodingizni yuklang
  2. Koyeb'da ro'yxatdan o'ting
  3. "Deploy from GitHub" tugmasini bosing
  4. Environment variables qo'shing:
     - `BOT_TOKEN` = tokeningiz
     - `ADMIN_IDS` = ID raqamingiz
  5. Deploy tugmasini bosing — tayyor!

### ✅ 2. Railway
- Sayt: https://railway.app
- Tekin: ✅ ($5 kredit oylik)
- Steps:
  1. GitHub'ga kodingizni yuklang
  2. Railway'da "New Project" → "Deploy from GitHub"
  3. Environment variables kiriting
  4. Deploy!

### ✅ 3. Render
- Sayt: https://render.com
- Tekin: ✅ (Web service free tier)
- Kamchilik: 15 daqiqada "sleep" bo'ladi (bot uchun Worker yarating)

### ✅ 4. PythonAnywhere
- Sayt: https://pythonanywhere.com
- Tekin: ✅ (Beginner account)
- Steps:
  1. Ro'yxatdan o'ting
  2. "Bash console" oching
  3. Fayllarni yuklang
  4. `pip install python-telegram-bot==20.7`
  5. "Always-on task" qo'shing: `python bot.py`

### ✅ 5. Google Cloud Run (Free tier)
- Sayt: https://cloud.google.com
- Tekin: ✅ (3 oy + aylik limit)

---

## 📋 Bot Ishlatish

### Foydalanuvchilar uchun:
- `/start` — Botni ishga tushirish
- Kino kodini yuboring (masalan `1001`) → Bot kinoni yuboradi

### Admin uchun:
- `/admin` — Admin panelni ochish
- **Kino qo'shish:** Admin panel → "➕ Kino qo'shish" → Kod kiriting → Nom kiriting → Tavsif kiriting → Fayl yuboring
- **Kinolar ro'yxati:** Admin panel → "📋 Kinolar ro'yxati"
- **Kino o'chirish:** Admin panel → "🗑 Kino o'chirish" → Kodni yuboring → Tasdiqlang

---

## 🔧 Bir nechta Admin qo'shish
```python
ADMIN_IDS = [123456789, 987654321, 111222333]
```
Yoki environment variable orqali:
```
ADMIN_IDS=123456789,987654321,111222333
```

---

## ❓ Muammolar

**Bot ishlamayapti:**
- Token to'g'riligini tekshiring
- `pip install -r requirements.txt` ni qayta ishga tushiring

**Admin panel ko'rinmayapti:**
- Admin ID to'g'riligini tekshiring
- `@userinfobot` orqali ID ni qayta tekshiring
