import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRIVATE_KEY_PATH = os.path.join(BASE_DIR, "auth", "certs", "private.pem")
PRIVATE_KEY_PASSWORD = os.getenv('PRIVATE_KEY_PASSWORD')
ACCESS_TOKEN_EXPIRES = os.getenv('ACCESS_TOKEN_EXPIRES')
REFRESH_TOKEN_EXPIRES = os.getenv('REFRESH_TOKEN_EXPIRES')
TOKEN_KEY = os.getenv('TOKEN_KEY')

BOT_TOKEN = os.getenv('BOT_TOKEN')
