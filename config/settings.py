import os
from functools import lru_cache
from pathlib import Path

from pydantic.v1 import BaseSettings, Field, root_validator

ROOT_DIR = Path(__file__).resolve().parent.parent
ENV_FILES = (ROOT_DIR / '.env', ROOT_DIR / 'env')


def _load_env_files() -> None:
    """Load KEY=VALUE pairs from local env files without python-dotenv."""
    for env_file in ENV_FILES:
        if not env_file.exists():
            continue

        for raw_line in env_file.read_text(encoding='utf-8').splitlines():
            line = raw_line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue

            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()

            if value and ((value[0] == value[-1]) and value[0] in {'"', "'"}):
                value = value[1:-1]

            os.environ.setdefault(key, value)


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

    support_contact: str = Field(default='@support', env='SUPPORT_CONTACT')

    @root_validator(pre=True)
    def populate_admin_ids_from_single_admin_id(cls, values: dict) -> dict:
        """Support ADMIN_ID for convenience when ADMIN_IDS is not defined."""
        if values.get('ADMIN_IDS'):
            return values

        single_admin_id = values.get('ADMIN_ID')
        if single_admin_id in (None, ''):
            return values

        values['ADMIN_IDS'] = f'[{single_admin_id}]'
        return values

    class Config:
        extra = 'ignore'


@lru_cache
def get_settings() -> Settings:
    _load_env_files()
    return Settings()
