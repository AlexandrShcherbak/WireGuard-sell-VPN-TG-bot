from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from sqlalchemy import func, select

from bot.keyboards.admin import admin_menu_kb
from config.config import settings
from database.db import SessionLocal
from database.models.subscription import Subscription
from database.models.user import User

router = Router(name='admin_router')


def _is_admin(user_id: int) -> bool:
    return user_id in settings.admin_ids


@router.message(F.text == '/admin')
async def admin_start(message: Message) -> None:
    if not _is_admin(message.from_user.id):
        await message.answer('Недостаточно прав.')
        return
    await message.answer('Админ-панель', reply_markup=admin_menu_kb())


@router.callback_query(F.data == 'admin_stats')
async def admin_stats(call: CallbackQuery) -> None:
    if not _is_admin(call.from_user.id):
        await call.answer('Нет доступа', show_alert=True)
        return

    async with SessionLocal() as session:
        users_count = await session.scalar(select(func.count(User.id)))
        active_subs = await session.scalar(select(func.count(Subscription.id)).where(Subscription.status == 'active'))

    await call.message.edit_text(
        f'Пользователей: <b>{users_count or 0}</b>\nАктивных подписок: <b>{active_subs or 0}</b>',
        reply_markup=admin_menu_kb(),
    )
    await call.answer()
