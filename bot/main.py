import logging
from contextlib import suppress

from aiohttp import web

from bot.bot_instance import bot, dp
from bot.handlers.admin import router as admin_router
from bot.handlers.payment import create_webhook_app, router as payment_router
from bot.handlers.user import router as user_router
from bot.middlewares import ThrottlingMiddleware
from config.config import settings
from database.db import init_db


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    await init_db()

    dp.message.middleware(ThrottlingMiddleware())
    dp.include_router(user_router)
    dp.include_router(payment_router)
    dp.include_router(admin_router)

    runner: web.AppRunner | None = None
    if settings.sendler_webhook_enabled:
        app = await create_webhook_app()
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host=settings.sendler_webhook_host, port=settings.sendler_webhook_port)
        await site.start()
        logging.info('Webhook server started on %s:%s', settings.sendler_webhook_host, settings.sendler_webhook_port)

    try:
        await dp.start_polling(bot)
    finally:
        if runner:
            with suppress(Exception):
                await runner.cleanup()
