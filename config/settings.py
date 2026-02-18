from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    bot_token: str = Field(..., alias='BOT_TOKEN')
    admin_ids: list[int] = Field(default_factory=list, alias='ADMIN_IDS')

    database_url: str = Field(default='sqlite+aiosqlite:///./vpn_bot.db', alias='DATABASE_URL')

    wireguard_api_url: str = Field(..., alias='WIREGUARD_API_URL')
    wireguard_api_token: str = Field(..., alias='WIREGUARD_API_TOKEN')
    wireguard_server_public_key: str = Field(..., alias='WIREGUARD_SERVER_PUBLIC_KEY')
    wireguard_server_endpoint: str = Field(..., alias='WIREGUARD_SERVER_ENDPOINT')

    payment_provider: str = Field(default='manual', alias='PAYMENT_PROVIDER')
    payment_token: str | None = Field(default=None, alias='PAYMENT_TOKEN')

    trial_days: int = Field(default=1, alias='TRIAL_DAYS')
    default_plan_days: int = Field(default=30, alias='DEFAULT_PLAN_DAYS')
    default_plan_price_rub: int = Field(default=299, alias='DEFAULT_PLAN_PRICE_RUB')


@lru_cache
def get_settings() -> Settings:
    return Settings()
