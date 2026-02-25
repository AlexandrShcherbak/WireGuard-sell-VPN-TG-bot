from functools import lru_cache
from pathlib import Path

from pydantic.v1 import BaseSettings, Field

ROOT_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT_DIR / '.env'


class Settings(BaseSettings):
    bot_token: str = Field(..., env='BOT_TOKEN')
    admin_ids: list[int] = Field(default_factory=list, env='ADMIN_IDS')

    database_url: str = Field(default='sqlite+aiosqlite:///./vpn_bot.db', env='DATABASE_URL')

    wireguard_api_url: str = Field(..., env='WIREGUARD_API_URL')
    wireguard_api_token: str = Field(..., env='WIREGUARD_API_TOKEN')
    wireguard_server_public_key: str = Field(..., env='WIREGUARD_SERVER_PUBLIC_KEY')
    wireguard_server_endpoint: str = Field(..., env='WIREGUARD_SERVER_ENDPOINT')

    payment_provider: str = Field(default='manual', env='PAYMENT_PROVIDER')
    payment_token: str | None = Field(default=None, env='PAYMENT_TOKEN')

    trial_days: int = Field(default=1, env='TRIAL_DAYS')
    default_plan_days: int = Field(default=30, env='DEFAULT_PLAN_DAYS')
    default_plan_price_rub: int = Field(default=299, env='DEFAULT_PLAN_PRICE_RUB')

    class Config:
        env_file = str(ENV_FILE)
        env_file_encoding = 'utf-8'
        extra = 'ignore'


@lru_cache
def get_settings() -> Settings:
    return Settings()
