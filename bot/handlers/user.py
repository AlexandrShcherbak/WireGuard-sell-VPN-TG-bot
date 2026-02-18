from aiogram import F, Router
from aiogram.types import CallbackQuery, FSInputFile, Message

from bot.keyboards.user import buy_confirm_kb, main_menu_kb
from bot.utils.helpers import fmt_dt
from config.config import settings
from database.crud import create_subscription, get_or_create_user, get_user_active_subscription
from database.db import SessionLocal
from wireguard.generator import build_client_config, save_config
from wireguard.manager import WireGuardEasyManager

router = Router()
wg_manager = WireGuardEasyManager(settings.wireguard_api_url, settings.wireguard_api_token)


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


@router.callback_query(F.data == 'menu')
async def open_menu(call: CallbackQuery) -> None:
    await call.message.edit_text('Главное меню:', reply_markup=main_menu_kb())
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
        'Переведите оплату и нажмите кнопку ниже для подтверждения.'
        f'\nID заказа: <code>{subscription.id}</code>'
    )
    await call.message.edit_text(text, reply_markup=buy_confirm_kb())
    await call.answer()


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
async def paid_handler(call: CallbackQuery) -> None:
    # Для MVP считаем платеж подтвержденным вручную.
    client_name = f'user-{call.from_user.id}'
    client = await wg_manager.create_client(client_name)
    conf = build_client_config(
        client,
        server_public_key=settings.wireguard_server_public_key,
        endpoint=settings.wireguard_server_endpoint,
    )
    file_path = save_config(f'storage/configs/{client_name}.conf', conf)

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
        from database.crud import activate_subscription
        await activate_subscription(
            session=session,
            subscription=subscription,
            wg_client_id=client.id,
            wg_client_name=client.name,
            config_path=file_path,
        )

    await call.message.answer_document(FSInputFile(file_path), caption='Оплата подтверждена. Ваш WireGuard конфиг:')
    await call.message.answer('Подписка активирована ✅', reply_markup=main_menu_kb())
    await call.answer()
