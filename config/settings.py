import os
from functools import lru_cache
from pathlib import Path

from pydantic.v1 import BaseSettings, Field, root_validator

ROOT_DIR = Path(__file__).resolve().parent.parent
ENV_FILES = (
    ROOT_DIR / '.env',
    ROOT_DIR / 'env',
    Path.cwd() / '.env',
    Path.cwd() / 'env',
)


def _load_env_files() -> None:
    """Load KEY=VALUE pairs from local env files without python-dotenv."""
    loaded_paths: set[Path] = set()
    for env_file in ENV_FILES:
        env_path = env_file.resolve()
        if env_path in loaded_paths:
            continue
        loaded_paths.add(env_path)

        if not env_file.exists():
            continue

        for raw_line in env_file.read_text(encoding='utf-8-sig').splitlines():
            line = raw_line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue

            if line.startswith('export '):
                line = line[len('export '):].strip()

            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()

            if ' #' in value and not value.startswith(('"', "'")):
                value = value.split(' #', 1)[0].rstrip()

            if value and ((value[0] == value[-1]) and value[0] in {'"', "'"}):
                value = value[1:-1]

            os.environ.setdefault(key, value)

    # Совместимость со старыми именами переменных.
    if 'ADMIN_IDS' not in os.environ and 'ADMIN_ID' in os.environ:
        os.environ['ADMIN_IDS'] = f"[{os.environ['ADMIN_ID']}]"

    if 'CRYPTOBOT_TOKEN' not in os.environ:
        legacy_token = os.environ.get('CRYPTOBOT_API_TOKEN') or os.environ.get('PAYMENT_TOKEN')
        if legacy_token:
            os.environ['CRYPTOBOT_TOKEN'] = legacy_token

    if 'DONATION_BASE_URL' not in os.environ and 'DONATIONALERTS_URL' in os.environ:
        os.environ['DONATION_BASE_URL'] = os.environ['DONATIONALERTS_URL']


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
    cryptobot_token: str | None = Field(default=None, env='CRYPTOBOT_TOKEN')
    donation_base_url: str | None = Field(default=None, env='DONATION_BASE_URL')

    support_contact: str = Field(default='@support', env='SUPPORT_CONTACT')

    # Вебхуки отключены в polling-режиме, поля оставлены для совместимости конфигов.
    sendler_webhook_enabled: bool = Field(default=False, env='SENDLER_WEBHOOK_ENABLED')
    sendler_webhook_host: str = Field(default='0.0.0.0', env='SENDLER_WEBHOOK_HOST')
    sendler_webhook_port: int = Field(default=8080, env='SENDLER_WEBHOOK_PORT')
    sendler_webhook_secret: str | None = Field(default=None, env='SENDLER_WEBHOOK_SECRET')

    trial_days: int = Field(default=1, env='TRIAL_DAYS')
    default_plan_days: int = Field(default=180, env='DEFAULT_PLAN_DAYS')
    default_plan_price_rub: int = Field(default=600, env='DEFAULT_PLAN_PRICE_RUB')

    @root_validator(pre=True)
    def populate_admin_ids_from_single_admin_id(cls, values: dict) -> dict:
        """Support ADMIN_ID for convenience when ADMIN_IDS is not defined."""
        if not values.get('ADMIN_IDS') and not values.get('admin_ids'):
            single_admin_id = values.get('ADMIN_ID') or values.get('admin_id')
            if single_admin_id not in (None, ''):
                values['ADMIN_IDS'] = f'[{single_admin_id}]'

        if not values.get('CRYPTOBOT_TOKEN') and not values.get('cryptobot_token'):
            values['CRYPTOBOT_TOKEN'] = (
                values.get('CRYPTOBOT_API_TOKEN')
                or values.get('cryptobot_api_token')
                or values.get('PAYMENT_TOKEN')
                or values.get('payment_token')
            )

        if not values.get('DONATION_BASE_URL') and not values.get('donation_base_url'):
            values['DONATION_BASE_URL'] = values.get('DONATIONALERTS_URL') or values.get('donationalerts_url')

        return values

    class Config:
        extra = 'ignore'


@lru_cache
def get_settings() -> Settings:
    _load_env_files()
    return Settings()
