import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    bot_token: str
    admin_ids: list[int]
    db_url: str
    openrouter_key: str
    model: str
    google_calendar_id: str
    google_service_account_file: str
    google_service_account_json: str


def load_config() -> Config:
   
    if not os.getenv("BOT_TOKEN"):
        raise ValueError("BOT_TOKEN topilmadi")

    if not os.getenv("DB_URL"):
        raise ValueError("DB_URL topilmadi")

    admin_ids_raw = os.getenv("ADMIN_IDS", "")

    return Config(
        bot_token=os.getenv("BOT_TOKEN"),
        admin_ids=[int(x) for x in admin_ids_raw.split(",") if x.strip()],
        db_url=os.getenv("DB_URL"),
        openrouter_key=os.getenv("OPENROUTER_API_KEY", ""),
        model=os.getenv("MODEL", "openrouter/free"),
        google_calendar_id=os.getenv("GOOGLE_CALENDAR_ID", ""),
        google_service_account_file=os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", ""),
        google_service_account_json=os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", ""),
    )


config = load_config()