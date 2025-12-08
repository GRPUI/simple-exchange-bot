import os

import dotenv

dotenv.load_dotenv(
    dotenv_path=".env",
)

BOT_TOKEN = os.getenv("BOT_TOKEN", "7513118526:AAGkD4yu37VYsgmDdmth1CJ62OeBDaLzxcI")
DB_NAME = os.getenv("POSTGRES_DB", "shop_db")
DB_USER = os.getenv("POSTGRES_USER", "xue_lxng")
DB_PASSWORD = os.getenv(
    "POSTGRES_PASSWORD", "fyxNtn7A3BLjS84eefcidF7cPAq9ZtXrC0vIA6wAK2JfZKcIsK"
)
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5001")
DB_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
LEAD_CHAT = os.getenv("LEAD_CHAT", "-4837893437")
