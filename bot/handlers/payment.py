from aiogram import Router

from integrations.payments import StubPaymentProvider

router = Router(name='payment_router')
payment_provider = StubPaymentProvider()

# TODO: добавить webhook-роутер и заменить StubPaymentProvider на реального провайдера.
