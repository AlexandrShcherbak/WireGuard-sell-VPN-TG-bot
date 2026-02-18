from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config.config import settings

bot = Bot(token=settings.bot_token, parse_mode='HTML')
dp = Dispatcher(storage=MemoryStorage())
