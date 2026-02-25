from dataclasses import dataclass
from typing import Protocol


@dataclass(slots=True)
class PaymentStatus:
    invoice_id: str
    state: str


class PaymentProvider(Protocol):
    async def create_invoice(self, user_id: int, amount_rub: int) -> str:
        ...

    async def get_status(self, invoice_id: str) -> PaymentStatus:
        ...


class StubPaymentProvider:
    """Временная заглушка для будущей интеграции с платежным API."""

    async def create_invoice(self, user_id: int, amount_rub: int) -> str:
        return f"stub-invoice-{user_id}-{amount_rub}"

    async def get_status(self, invoice_id: str) -> PaymentStatus:
        return PaymentStatus(invoice_id=invoice_id, state="pending")
