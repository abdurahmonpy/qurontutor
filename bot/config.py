import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN_HERE")
WEBAPP_URL = os.getenv("WEBAPP_URL", "http://localhost:8000/")
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000/api")
PROXY_URL = os.getenv("PROXY_URL", "")
TELEGRAM_API_SERVER = os.getenv("TELEGRAM_API_SERVER", "")
