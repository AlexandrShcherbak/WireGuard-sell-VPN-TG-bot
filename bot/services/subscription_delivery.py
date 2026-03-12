from aiogram import Bot
from aiogram.types import FSInputFile

from bot.keyboards.user import main_menu_kb
from config.config import settings
from database.crud import activate_subscription
from database.db import SessionLocal
from database.models.subscription import Subscription
from wireguard.generator import build_client_config, generate_qr, save_config
from wireguard.manager import WireGuardEasyManager

wg_manager = WireGuardEasyManager(settings.wireguard_api_url, settings.wireguard_api_token)


async def activate_and_deliver_subscription(bot: Bot, user_telegram_id: int, subscription: Subscription) -> None:
    client_name = f'user-{user_telegram_id}-sub-{subscription.id}'
    client = await wg_manager.create_client(client_name)
    conf = build_client_config(
        client,
        server_public_key=settings.wireguard_server_public_key,
        endpoint=settings.wireguard_server_endpoint,
    )

    conf_path = save_config(f'storage/configs/{client_name}.conf', conf)
    qr_path = generate_qr(f'storage/qr/{client_name}.png', conf)

    async with SessionLocal() as session:
        managed_subscription = await session.get(Subscription, subscription.id)
        if not managed_subscription:
            return

        await activate_subscription(
            session=session,
            subscription=managed_subscription,
            wg_client_id=client.id,
            wg_client_name=client.name,
            config_path=conf_path,
        )

    await bot.send_document(user_telegram_id, FSInputFile(conf_path), caption='Оплата подтверждена. Ваш WireGuard конфиг:')
    await bot.send_photo(user_telegram_id, FSInputFile(qr_path), caption='QR-код для быстрого подключения')
    await bot.send_message(user_telegram_id, 'Подписка активирована ✅', reply_markup=main_menu_kb())
