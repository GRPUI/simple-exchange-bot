import os

import dotenv

dotenv.load_dotenv(
    dotenv_path=".env",
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("POSTGRES_PORT")
DB_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
LEAD_CHAT = os.getenv("LEAD_CHAT")
