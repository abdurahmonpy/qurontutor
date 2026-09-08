import os
import json
import time
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

def get_bot_token():
    token = getattr(settings, 'BOT_TOKEN', None) or os.getenv("BOT_TOKEN")
    if not token or token == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        return None
    return token

def send_telegram_message(chat_id, text, photo=None, button_text=None, button_url=None):
    """
    Sends a message (text or photo with caption and optional inline button)
    to a Telegram chat_id using the official Telegram Bot HTTP API.
    Returns: (success: bool, detail: str)
    """
    token = get_bot_token()
    if not token:
        return False, "BOT_TOKEN sozlanmagan"

    base_url = f"https://api.telegram.org/bot{token}"

    reply_markup = None
    if button_text and button_url:
        reply_markup = {
            "inline_keyboard": [
                [{"text": button_text, "url": button_url}]
            ]
        }

    try:
        if photo:
            endpoint = f"{base_url}/sendPhoto"
            data = {
                "chat_id": chat_id,
                "caption": text,
                "parse_mode": "HTML"
            }
            if reply_markup:
                data["reply_markup"] = json.dumps(reply_markup)

            # photo can be a file-like object or a path
            if hasattr(photo, 'read'):
                photo.seek(0)
                files = {"photo": (getattr(photo, 'name', 'image.jpg'), photo.read())}
            elif isinstance(photo, str) and os.path.exists(photo):
                files = {"photo": open(photo, "rb")}
            else:
                files = None

            if files:
                resp = requests.post(endpoint, data=data, files=files, timeout=12)
            else:
                resp = requests.post(f"{base_url}/sendMessage", json={
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": "HTML",
                    **({"reply_markup": reply_markup} if reply_markup else {})
                }, timeout=10)
        else:
            endpoint = f"{base_url}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML"
            }
            if reply_markup:
                payload["reply_markup"] = reply_markup
            resp = requests.post(endpoint, json=payload, timeout=10)

        data = resp.json()
        if data.get("ok"):
            return True, "OK"
        
        description = data.get("description", "Xatolik yuz berdi")
        logger.warning(f"Telegram API xatosi ({chat_id}): {description}")
        return False, description

    except Exception as e:
        logger.error(f"Telegram yuborishda ulanish xatosi ({chat_id}): {e}")
        return False, str(e)


def broadcast_to_users(user_qs, text, photo=None, button_text=None, button_url=None, delay=0.05):
    """
    Sends a message to an iterable/QuerySet of TelegramUser objects.
    Returns: (sent_count, failed_count, errors)
    """
    sent_count = 0
    failed_count = 0
    errors = []

    for user in user_qs:
        if not user.telegram_id:
            continue

        # Personalize text with user's name if placeholder exists
        user_name = user.first_name or "Qoriy"
        personalized_text = text.replace("{name}", user_name).replace("{first_name}", user_name)

        success, detail = send_telegram_message(
            chat_id=user.telegram_id,
            text=personalized_text,
            photo=photo,
            button_text=button_text,
            button_url=button_url
        )

        if success:
            sent_count += 1
        else:
            failed_count += 1
            if detail not in errors:
                errors.append(detail)

        # Small delay to adhere to Telegram rate limits (30 msg/sec)
        if delay > 0:
            time.sleep(delay)

    return sent_count, failed_count, errors
