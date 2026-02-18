import time
from collections import defaultdict

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, rate_limit_seconds: float = 0.8) -> None:
        self.rate_limit_seconds = rate_limit_seconds
        self._last_called = defaultdict(float)

    async def __call__(self, handler, event: TelegramObject, data: dict):
        if isinstance(event, Message):
            now = time.time()
            key = event.from_user.id
            if now - self._last_called[key] < self.rate_limit_seconds:
                return
            self._last_called[key] = now
        return await handler(event, data)
