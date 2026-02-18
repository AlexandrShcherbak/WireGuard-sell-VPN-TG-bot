import asyncio
import logging

from bot.bot_instance import bot, dp
from bot.handlers.admin import router as admin_router
from bot.handlers.payment import router as payment_router
from bot.handlers.user import router as user_router
from bot.middlewares import ThrottlingMiddleware
from database.db import init_db


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    await init_db()

    dp.message.middleware(ThrottlingMiddleware())
    dp.include_router(user_router)
    dp.include_router(payment_router)
    dp.include_router(admin_router)

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
