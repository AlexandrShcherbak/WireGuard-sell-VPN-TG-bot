from aiohttp import web
from aiogram import Router

from bot.bot_instance import bot
from bot.services.subscription_delivery import activate_and_deliver_subscription
from config.config import settings
from database.crud import get_payment, get_subscription, mark_payment_paid
from database.db import SessionLocal

router = Router(name='payment_router')


async def cryptobot_webhook(request: web.Request) -> web.Response:
    payload = await request.json()
    update = payload.get('update', {})
    if update.get('status') != 'paid':
        return web.json_response({'ok': True})

    invoice_id = str(update.get('invoice_id', ''))
    async with SessionLocal() as session:
        from sqlalchemy import select
        from database.models.payment import Payment

        payment = (
            await session.execute(
                select(Payment).where(Payment.provider == 'cryptobot', Payment.provider_payment_id == invoice_id)
            )
        ).scalar_one_or_none()

        if not payment or payment.status == 'paid':
            return web.json_response({'ok': True})

        subscription = await get_subscription(session, payment.subscription_id)
        user_id = payment.user.telegram_id
        await mark_payment_paid(session, payment.id, invoice_id)

    if subscription:
        await activate_and_deliver_subscription(bot, user_id, subscription)

    return web.json_response({'ok': True})


async def donation_webhook(request: web.Request) -> web.Response:
    if settings.sendler_webhook_secret:
        secret = request.headers.get('X-Webhook-Secret')
        if secret != settings.sendler_webhook_secret:
            return web.json_response({'ok': False, 'error': 'unauthorized'}, status=401)

    payload = await request.json()
    payment_id = int(payload.get('payment_id', 0))

    async with SessionLocal() as session:
        payment = await get_payment(session, payment_id)
        if not payment:
            return web.json_response({'ok': False, 'error': 'payment_not_found'}, status=404)

        if payment.status == 'paid':
            return web.json_response({'ok': True})

        subscription = await get_subscription(session, payment.subscription_id)
        await mark_payment_paid(session, payment.id, str(payload.get('transaction_id', payment_id)))
        user_id = payment.user.telegram_id

    if subscription:
        await activate_and_deliver_subscription(bot, user_id, subscription)

    return web.json_response({'ok': True})


async def sendler_webhook(request: web.Request) -> web.Response:
    if settings.sendler_webhook_secret:
        secret = request.headers.get('X-Sendler-Secret')
        if secret != settings.sendler_webhook_secret:
            return web.json_response({'ok': False, 'error': 'unauthorized'}, status=401)

    payload = await request.json()
    event = payload.get('event', 'unknown')
    contact = payload.get('contact', {})
    text = (
        '📥 <b>Sendler webhook</b>\n'
        f'Событие: <code>{event}</code>\n'
        f'Имя: {contact.get("name", "-")}\n'
        f'Телефон: {contact.get("phone", "-")}\n'
        f'Email: {contact.get("email", "-")}'
    )

    for admin_id in settings.admin_ids:
        await bot.send_message(admin_id, text)

    return web.json_response({'ok': True})


async def create_webhook_app() -> web.Application:
    app = web.Application()
    app.router.add_post('/webhooks/cryptobot', cryptobot_webhook)
    app.router.add_post('/webhooks/donation', donation_webhook)
    app.router.add_post('/webhooks/sendler', sendler_webhook)
    return app
