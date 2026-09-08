"""
aiogram 3 Telegram Bot for Quran Recitation Checker
Handles /start, user registration and launches the Telegram Mini App.
"""
import asyncio
import logging
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer

from .config import BOT_TOKEN, WEBAPP_URL, API_BASE_URL, PROXY_URL, TELEGRAM_API_SERVER

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dp = Dispatcher()

async def register_user_in_backend(user: types.User):
    """Sends user data to Django API."""
    async with aiohttp.ClientSession() as session:
        payload = {
            "telegram_id": user.id,
            "username": user.username,
            "first_name": user.first_name or "",
            "last_name": user.last_name or ""
        }
        try:
            async with session.post(f"{API_BASE_URL}/user/register/", json=payload, timeout=5) as resp:
                if resp.status == 200:
                    logger.info(f"Registered user {user.id} in backend")
        except Exception as e:
            logger.warning(f"Could not register user in backend: {e}")

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    user = message.from_user
    if user:
        await register_user_in_backend(user)

    # Clean URL with telegram_id query param
    app_url = f"{WEBAPP_URL}?tg_id={user.id}" if user else WEBAPP_URL

    # Check if URL has HTTPS (Telegram requires HTTPS for native Mini App WebAppInfo)
    is_https = WEBAPP_URL.startswith("https://")
    
    greeting_text = (
        f"Assalomu alaykum va rahmatullohi va barokatuh, muhtaram <b>{user.first_name if user else ''}</b>!\n\n"
        "✨ <b>Qur'on Tilovat Tekshiruvchi (Iqra)</b> tizimiga xush kelibsiz.\n\n"
        "Ushbu bot orqali siz:\n"
        "• Sura va oyatlarni tanlab qiroat qilasiz;\n"
        "• O'z ovozingizni yozib yuborasiz;\n"
        "• Rasmiy mashhur qorilar qiroatini eshitib o'rganasiz.\n\n"
    )

    if is_https:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📖 Qur'on Tilovatini Boshlash",
                    web_app=WebAppInfo(url=app_url)
                )
            ],
            [
                InlineKeyboardButton(text="📊 Mening Yutuqlarim", callback_data="show_progress"),
                InlineKeyboardButton(text="ℹ️ Qoidalar & Qo'llanma", callback_data="show_help")
            ]
        ])
        greeting_text += "Boshlash uchun quyidagi tugmani bosing:"
    else:
        greeting_text += (
            f"🌐 <b>Ilovani ochish uchun quyidagi havolaga kiring:</b>\n"
            f"👉 <b>{app_url}</b>\n\n"
            "<i>(Eslatma: Telegram ichida to'g'ridan-to'g'ri Mini App tugmasi orqali ochish uchun .env faylidagi WEBAPP_URL ga HTTPS havola (masalan, ngrok) ulanadi).</i>"
        )
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📊 Mening Yutuqlarim", callback_data="show_progress"),
                InlineKeyboardButton(text="ℹ️ Qoidalar & Qo'llanma", callback_data="show_help")
            ]
        ])

    await message.answer(greeting_text, reply_markup=keyboard, parse_mode="HTML")

@dp.message(Command("progress"))
@dp.callback_query(lambda c: c.data == "show_progress")
async def show_progress(event: types.Message | types.CallbackQuery):
    user_id = event.from_user.id
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{API_BASE_URL}/user/progress/?telegram_id={user_id}", timeout=5) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    text = (
                        "📊 <b>Sizning qiroat natijalaringiz:</b>\n\n"
                        f"• O'zlashtirilgan oyatlar: <b>{data.get('completed_ayahs', 0)}</b> ta\n"
                        f"• Jami qilingan urinishlar: <b>{data.get('total_attempts', 0)}</b> marta\n"
                        f"• O'rtacha aniqlik ko'rsatkichi: <b>{data.get('average_score', 0)}%</b>\n"
                        f"• Oxirgi o'qilgan sura: <b>{data.get('current_surah', 1)}-sura</b>"
                    )
                else:
                    text = "Hozircha natijalar mavjud emas. Mini App orqali birinchi tilovatingizni topshiring!"
        except Exception:
            text = "Natijalarni yuklashda xatolik yuz berdi. Iltimos keyinroq urinib ko'ring."

    if isinstance(event, types.CallbackQuery):
        await event.message.answer(text, parse_mode="HTML")
        await event.answer()
    else:
        await event.answer(text, parse_mode="HTML")

@dp.callback_query(lambda c: c.data == "show_help")
async def show_help(callback: types.CallbackQuery):
    text = (
        "💡 <b>Tilovatni tekshirish tartibi:</b>\n\n"
        "1. «Qur'on Tilovatini Boshlash» tugmasini bosing;\n"
        "2. Kerakli sura va oyatni tanlang;\n"
        "3. «Eshitish» tugmasi orqali qorining qiroatiga quloq soling;\n"
        "4. Mikrofon tugmasini bosib, oyatni dona-dona va tajvid bilan o'qing;\n"
        "5. Tizim har bir so'zni tekshiradi:\n"
        "   🟢 <b>Yashil</b> — To'g'ri o'qilgan so'z;\n"
        "   🟡 <b>Sariq</b> — So'z to'g'ri, lekin tajvid qoidasiga (madd, g'unna va h.k.) rioya qilinmagan;\n"
        "   🔴 <b>Qizil</b> — Tushirib qoldirilgan yoki boshqa so'z bilan adashtirilgan.\n"
        "6. 70% dan yuqori ball olsangiz, keyingi oyatga o'tasiz!"
    )
    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()

async def main():
    if BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE" or not BOT_TOKEN:
        logger.warning("BOT_TOKEN is not configured. Add your token to .env to run the Telegram Bot.")
        return

    session = None
    if PROXY_URL:
        logger.info(f"Using proxy: {PROXY_URL}")
        session = AiohttpSession(proxy=PROXY_URL)
    elif TELEGRAM_API_SERVER:
        logger.info(f"Using custom Telegram API server: {TELEGRAM_API_SERVER}")
        session = AiohttpSession(api=TelegramAPIServer.from_base(TELEGRAM_API_SERVER))

    bot = Bot(token=BOT_TOKEN, session=session)
    logger.info("Starting Telegram Bot...")

    try:
        # Reset any leftover webhook and drop old updates
        await bot.delete_webhook(drop_pending_updates=True)
    except Exception as e:
        logger.warning(f"Could not delete webhook: {e}")

    # Retry loop with backoff for polling in case previous container instance is terminating
    max_retries = 10
    retry_delay = 3
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Connecting bot polling (attempt {attempt}/{max_retries})...")
            await dp.start_polling(bot, drop_pending_updates=True)
            break
        except Exception as e:
            err_name = type(e).__name__
            if "Conflict" in str(e) or "Conflict" in err_name:
                logger.warning(
                    f"Telegram conflict detected: previous bot instance is shutting down. "
                    f"Retrying in {retry_delay}s (attempt {attempt}/{max_retries})..."
                )
                await asyncio.sleep(retry_delay)
                retry_delay = min(retry_delay * 1.5, 10)
            else:
                logger.error(f"Fatal error in bot polling: {e}")
                raise e

if __name__ == "__main__":
    asyncio.run(main())
