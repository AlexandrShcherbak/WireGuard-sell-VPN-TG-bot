import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from bot.keyboards.inline import buy_methods_kb, check_payment_kb, main_menu_kb
from bot.services.subscription_delivery import activate_and_deliver_subscription
from bot.utils.helpers import fmt_dt
from config.config import settings
from database.crud import (
    create_payment,
    create_subscription,
    get_latest_pending_subscription,
    get_or_create_user,
    get_payment,
    get_subscription,
    get_user_active_subscription,
    mark_payment_paid,
)
from database.db import SessionLocal
from integrations.payments import CryptoBotProvider, DonationAlertsProvider

router = Router()
logger = logging.getLogger(__name__)


def _build_howto_text() -> str:
    return (
        '📘 <b>Как подключить VPN за 1 минуту</b>\n\n'
        '1) Установите WireGuard:\n'
        '• Android: https://play.google.com/store/apps/details?id=com.wireguard.android\n'
        '• iOS: https://apps.apple.com/us/app/wireguard/id1441195209\n'
        '• Windows/macOS/Linux: https://www.wireguard.com/install/\n\n'
        '2) После оплаты получите .conf и QR-код в этом боте.\n'
        '3) В приложении WireGuard импортируйте конфиг (или отсканируйте QR).\n'
        '4) Включите туннель и проверьте IP: https://2ip.ru\n\n'
        f'Если нужна помощь — {settings.support_contact}'
    )


@router.message(F.text == '/start')
async def cmd_start(message: Message) -> None:
    async with SessionLocal() as session:
        await get_or_create_user(
            session=session,
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name,
        )
    await message.answer('Привет! Это VPN-бот. Выберите действие:', reply_markup=main_menu_kb())


@router.message(F.text == '/howto')
async def cmd_howto(message: Message) -> None:
    await message.answer(_build_howto_text(), disable_web_page_preview=True)


@router.callback_query(F.data == 'howto')
async def howto_callback(call: CallbackQuery) -> None:
    await call.message.edit_text(_build_howto_text(), disable_web_page_preview=True, reply_markup=main_menu_kb())
    await call.answer()


@router.callback_query(F.data == 'menu')
async def open_menu(call: CallbackQuery) -> None:
    await call.message.edit_text('Главное меню:', reply_markup=main_menu_kb())
    await call.answer()


@router.callback_query(F.data == 'support')
async def write_to_support(call: CallbackQuery) -> None:
    await call.message.edit_text(
        f'Написать в поддержку: {settings.support_contact}',
        reply_markup=main_menu_kb(),
    )
    await call.answer()


@router.callback_query(F.data == 'buy')
async def buy_sub(call: CallbackQuery) -> None:
    async with SessionLocal() as session:
        user = await get_or_create_user(
            session=session,
            telegram_id=call.from_user.id,
            username=call.from_user.username,
            full_name=call.from_user.full_name,
        )
        subscription = await create_subscription(
            session=session,
            user_id=user.id,
            plan_days=settings.default_plan_days,
            price_rub=settings.default_plan_price_rub,
        )

    text = (
        f'Подписка на {settings.default_plan_days} дней — {settings.default_plan_price_rub} ₽\n'
        'Выберите способ оплаты:\n'
        f'ID заказа: <code>{subscription.id}</code>'
    )
    await call.message.edit_text(text, reply_markup=buy_methods_kb(subscription.id))
    await call.answer()


@router.callback_query(F.data == 'back_to_subscription')
async def back_to_subscription(call: CallbackQuery) -> None:
    async with SessionLocal() as session:
        user = await get_or_create_user(
            session=session,
            telegram_id=call.from_user.id,
            username=call.from_user.username,
            full_name=call.from_user.full_name,
        )
        subscription = await get_latest_pending_subscription(session, user.id)

    if not subscription:
        await call.answer('Нет ожидающей оплаты подписки', show_alert=True)
        return

    await call.message.edit_text(
        f'Выберите способ оплаты для заказа <code>{subscription.id}</code>:',
        reply_markup=buy_methods_kb(subscription.id),
    )
    await call.answer()


@router.callback_query(F.data == 'trial')
async def trial_info(call: CallbackQuery) -> None:
    await call.answer('Пробный период подключается поддержкой. Напишите в чат поддержки.', show_alert=True)


@router.callback_query(F.data.startswith('pay_crypto:'))
async def create_crypto_payment(call: CallbackQuery) -> None:
    subscription_id = int(call.data.split(':')[1])
    async with SessionLocal() as session:
        subscription = await get_subscription(session, subscription_id)
        user = await get_or_create_user(
            session=session,
            telegram_id=call.from_user.id,
            username=call.from_user.username,
            full_name=call.from_user.full_name,
        )
        if not subscription or subscription.user_id != user.id:
            await call.answer('Заказ не найден', show_alert=True)
            return

        payment = await create_payment(
            session=session,
            user_id=user.id,
            amount_rub=subscription.price_rub,
            subscription_id=subscription.id,
            provider='cryptobot',
        )

    if not settings.cryptobot_token:
        await call.answer('CRYPTOBOT_TOKEN не настроен', show_alert=True)
        return

    provider = CryptoBotProvider(settings.cryptobot_token)
    try:
        invoice = await provider.create_invoice(
            user_id=call.from_user.id,
            amount_rub=subscription.price_rub,
            payload=f'subscription:{subscription.id}:payment:{payment.id}',
        )
    except Exception as exc:
        logger.exception('Failed to create CryptoBot invoice')
        await call.answer(f'Не удалось создать счёт: {exc}', show_alert=True)
        return

    async with SessionLocal() as session:
        db_payment = await get_payment(session, payment.id)
        if db_payment:
            db_payment.provider_payment_id = invoice.invoice_id
            await session.commit()

    await call.message.edit_text(
        f'Счёт создан ✅\nОплатите по ссылке: {invoice.pay_url}',
        reply_markup=check_payment_kb(payment.id),
    )
    await call.answer()


@router.callback_query(F.data.startswith('pay_donation:'))
async def create_donation_payment(call: CallbackQuery) -> None:
    subscription_id = int(call.data.split(':')[1])
    if not settings.donation_base_url:
        await call.answer('DONATION_BASE_URL не настроен', show_alert=True)
        return

    async with SessionLocal() as session:
        subscription = await get_subscription(session, subscription_id)
        user = await get_or_create_user(
            session=session,
            telegram_id=call.from_user.id,
            username=call.from_user.username,
            full_name=call.from_user.full_name,
        )
        if not subscription or subscription.user_id != user.id:
            await call.answer('Заказ не найден', show_alert=True)
            return

        payment = await create_payment(
            session=session,
            user_id=user.id,
            amount_rub=subscription.price_rub,
            subscription_id=subscription.id,
            provider='donation',
        )

    provider = DonationAlertsProvider(base_url=settings.donation_base_url, token=settings.donationalerts_token)
    try:
        invoice = await provider.create_invoice(
            user_id=call.from_user.id,
            amount_rub=subscription.price_rub,
            payload=f'subscription:{subscription.id}:payment:{payment.id}',
        )
    except Exception as exc:
        logger.exception('Failed to create donation invoice')
        await call.answer(f'Не удалось сформировать ссылку на оплату: {exc}', show_alert=True)
        return

    async with SessionLocal() as session:
        db_payment = await get_payment(session, payment.id)
        if db_payment:
            db_payment.provider_payment_id = invoice.invoice_id
            await session.commit()

    await call.message.edit_text(
        f'Ссылка на рублёвую оплату:\n{invoice.pay_url}\n\nПосле оплаты нажмите «Проверить оплату».',
        reply_markup=check_payment_kb(payment.id),
    )
    await call.answer()


@router.callback_query(F.data.startswith('check_payment:'))
async def check_payment(call: CallbackQuery) -> None:
    payment_id = int(call.data.split(':')[1])

    async with SessionLocal() as session:
        payment = await get_payment(session, payment_id)
        if not payment:
            await call.answer('Платёж не найден', show_alert=True)
            return

        subscription = await get_subscription(session, payment.subscription_id)
        user = await get_or_create_user(
            session=session,
            telegram_id=call.from_user.id,
            username=call.from_user.username,
            full_name=call.from_user.full_name,
        )

        if payment.user_id != user.id or not subscription:
            await call.answer('Нет доступа к этому платежу', show_alert=True)
            return

        if payment.status == 'paid':
            await call.answer('Платёж уже подтверждён')
            return

        if payment.provider == 'cryptobot':
            if not settings.cryptobot_token:
                await call.answer('CRYPTOBOT_TOKEN не настроен', show_alert=True)
                return
            provider = CryptoBotProvider(settings.cryptobot_token)
            status = await provider.get_status(payment.provider_payment_id or '')
            is_paid = status.state == 'paid'
        else:
            # Для донат-сервисов подтверждение оплаты обычно приходит webhook'ом.
            is_paid = False

        if not is_paid:
            await call.answer('Оплата пока не найдена. Попробуйте позже.', show_alert=True)
            return

        await mark_payment_paid(session, payment.id, payment.provider_payment_id)

    await activate_and_deliver_subscription(call.bot, call.from_user.id, subscription)
    await call.answer('Оплата подтверждена!')


@router.callback_query(F.data == 'my_sub')
async def my_subscription(call: CallbackQuery) -> None:
    async with SessionLocal() as session:
        user = await get_or_create_user(
            session=session,
            telegram_id=call.from_user.id,
            username=call.from_user.username,
            full_name=call.from_user.full_name,
        )
        active_sub = await get_user_active_subscription(session, user.id)

    if not active_sub:
        await call.message.edit_text('У вас пока нет активной подписки.', reply_markup=main_menu_kb())
        await call.answer()
        return

    text = (
        'Текущая подписка:\n'
        f'Статус: <b>{active_sub.status}</b>\n'
        f'Начало: {fmt_dt(active_sub.starts_at)}\n'
        f'Окончание: {fmt_dt(active_sub.ends_at)}'
    )
    await call.message.edit_text(text, reply_markup=main_menu_kb())
    await call.answer()


@router.callback_query(F.data == 'paid')
async def paid_handler_deprecated(call: CallbackQuery) -> None:
    await call.answer('Используйте новый способ оплаты через кнопки.', show_alert=True)
