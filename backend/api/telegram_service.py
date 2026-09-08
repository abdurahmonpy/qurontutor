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

def send_telegram_message(chat_id, text, photo=None, photo_name=None, button_text=None, button_url=None):
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

    clean_text = text or ""

    try:
        if photo:
            endpoint = f"{base_url}/sendPhoto"
            data = {
                "chat_id": chat_id,
                "caption": clean_text,
                "parse_mode": "HTML"
            }
            if reply_markup:
                data["reply_markup"] = json.dumps(reply_markup)

            files = None
            if isinstance(photo, (bytes, bytearray)):
                files = {"photo": (photo_name or "image.jpg", photo)}
            elif hasattr(photo, 'read'):
                try:
                    photo.seek(0)
                except Exception:
                    pass
                files = {"photo": (photo_name or getattr(photo, 'name', 'image.jpg'), photo.read())}
            elif isinstance(photo, str) and os.path.exists(photo):
                files = {"photo": (photo_name or os.path.basename(photo), open(photo, "rb"))}

            if files:
                resp = requests.post(endpoint, data=data, files=files, timeout=15)
            else:
                resp = requests.post(f"{base_url}/sendMessage", json={
                    "chat_id": chat_id,
                    "text": clean_text,
                    "parse_mode": "HTML",
                    **({"reply_markup": reply_markup} if reply_markup else {})
                }, timeout=10)
        else:
            endpoint = f"{base_url}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": clean_text,
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


def broadcast_to_users(user_qs, text, photo=None, photo_name=None, button_text=None, button_url=None, delay=0.05):
    """
    Sends a message to an iterable/QuerySet of TelegramUser objects.
    Returns: (sent_count, failed_count, errors)
    """
    sent_count = 0
    failed_count = 0
    errors = []

    # Pre-read photo into bytes once so it can be re-sent safely to all recipients
    photo_bytes = None
    if isinstance(photo, (bytes, bytearray)):
        photo_bytes = photo
    elif photo and hasattr(photo, 'read'):
        try:
            photo.seek(0)
            photo_bytes = photo.read()
            if not photo_name:
                photo_name = getattr(photo, 'name', 'image.jpg')
        except Exception as err:
            logger.warning(f"Could not read photo for broadcast: {err}")
            photo_bytes = None
    elif isinstance(photo, str) and os.path.exists(photo):
        try:
            with open(photo, 'rb') as f:
                photo_bytes = f.read()
            if not photo_name:
                photo_name = os.path.basename(photo)
        except Exception as err:
            logger.warning(f"Could not read photo file {photo}: {err}")
            photo_bytes = None

    for user in user_qs:
        if not user.telegram_id:
            continue

        # Personalize text with user's name if placeholder exists
        user_name = user.first_name or "Qoriy"
        clean_text = text or ""
        personalized_text = clean_text.replace("{name}", user_name).replace("{first_name}", user_name)

        success, detail = send_telegram_message(
            chat_id=user.telegram_id,
            text=personalized_text,
            photo=photo_bytes,
            photo_name=photo_name,
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
