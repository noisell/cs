import os

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
SITE_URL = "https://cs-limited.ru"
ADMIN_URL = SITE_URL + "/admin/DRk3DsdZsdDaovn2LpfzFI8b"
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))