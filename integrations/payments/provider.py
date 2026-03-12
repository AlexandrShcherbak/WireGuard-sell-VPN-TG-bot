import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import urlencode

import aiohttp

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class PaymentStatus:
    invoice_id: str
    state: str


@dataclass(slots=True)
class Invoice:
    invoice_id: str
    pay_url: str


class StubPaymentProvider:
    """Временная заглушка для будущей интеграции с платежным API."""

    async def create_invoice(self, user_id: int, amount_rub: int, payload: str | None = None) -> Invoice:
        invoice_id = f'stub-invoice-{user_id}-{amount_rub}'
        return Invoice(invoice_id=invoice_id, pay_url=f'https://example.com/pay/{invoice_id}')

    async def get_status(self, invoice_id: str) -> PaymentStatus:
        return PaymentStatus(invoice_id=invoice_id, state='pending')


class CryptoBotProvider:
    """Интеграция с @CryptoBot через Crypto Pay API."""

    def __init__(self, token: str) -> None:
        self.token = token
        self.base_url = 'https://pay.crypt.bot/api'

    @property
    def _headers(self) -> dict[str, str]:
        return {'Crypto-Pay-API-Token': self.token}

    async def create_invoice(self, user_id: int, amount_rub: int, payload: str | None = None) -> Invoice:
        data = {
            'currency_type': 'fiat',
            'fiat': 'RUB',
            'amount': str(amount_rub),
            'description': f'VPN subscription for user {user_id}',
            'allow_comments': False,
            'allow_anonymous': False,
        }
        if payload:
            data['payload'] = payload

        async with aiohttp.ClientSession(headers=self._headers) as session:
            async with session.post(f'{self.base_url}/createInvoice', json=data, timeout=20) as resp:
                resp.raise_for_status()
                data = await resp.json()

        if not data.get('ok'):
            raise RuntimeError(f"CryptoBot invoice creation failed: {data}")

        result = data['result']
        pay_url = result.get('bot_invoice_url') or result.get('pay_url')
        if not pay_url:
            raise RuntimeError(f"CryptoBot response missing payment URL: {data}")
        return Invoice(invoice_id=str(result['invoice_id']), pay_url=pay_url)

    async def get_status(self, invoice_id: str) -> PaymentStatus:
        async with aiohttp.ClientSession(headers=self._headers) as session:
            async with session.get(
                f'{self.base_url}/getInvoices',
                params={'invoice_ids': invoice_id},
                timeout=20,
            ) as resp:
                resp.raise_for_status()
                data = await resp.json()

        if not data.get('ok'):
            raise RuntimeError(f"CryptoBot getInvoices failed: {data}")

        items = data.get('result', {}).get('items', [])
        if not items:
            return PaymentStatus(invoice_id=invoice_id, state='not_found')

        return PaymentStatus(invoice_id=invoice_id, state=str(items[0].get('status', 'pending')))


class DonationAlertsProvider:
    """Формирует ссылку на донат-сервис с рублёвой оплатой."""

    def __init__(self, base_url: str, token: str | None = None) -> None:
        self.base_url = base_url.rstrip('/')
        self.token = token

    async def create_invoice(self, user_id: int, amount_rub: int, payload: str | None = None) -> Invoice:
        query: dict[str, str | int] = {'amount': amount_rub, 'currency': 'RUB', 'user': user_id}
        if payload:
            query['payload'] = payload
        if self.token:
            query['token'] = self.token

        timestamp = int(datetime.now(timezone.utc).timestamp())
        invoice_id = payload or f'donation-{user_id}-{amount_rub}-{timestamp}'
        query['invoice_id'] = invoice_id
        pay_url = f'{self.base_url}?{urlencode(query)}'
        return Invoice(invoice_id=invoice_id, pay_url=pay_url)

    async def get_status(self, invoice_id: str) -> PaymentStatus:
        # Для донат-сервисов подтверждение оплаты обычно приходит webhook'ом.
        return PaymentStatus(invoice_id=invoice_id, state='pending')


def get_payment_provider(settings: object) -> StubPaymentProvider | CryptoBotProvider | DonationAlertsProvider:
    provider_name = str(getattr(settings, 'payment_provider', 'manual')).lower()
    logger.info('Selecting payment provider: %s', provider_name)

    if provider_name == 'cryptobot':
        token = (
            getattr(settings, 'cryptobot_token', None)
            or getattr(settings, 'payment_token', None)
            or getattr(settings, 'cryptobot_api_token', None)
        )
        if not token:
            raise RuntimeError('CryptoBot provider selected but token is missing')
        return CryptoBotProvider(token)

    if provider_name in {'donationalerts', 'donation'}:
        token = getattr(settings, 'donationalerts_token', None) or getattr(settings, 'donation_token', None)
        base_url = (
            getattr(settings, 'donation_base_url', None)
            or getattr(settings, 'donationalerts_base_url', None)
            or 'https://www.donationalerts.com/r/countvpn'
        )
        return DonationAlertsProvider(base_url=base_url, token=token)

    return StubPaymentProvider()
