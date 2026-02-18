from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def admin_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='📊 Статистика', callback_data='admin_stats')],
            [InlineKeyboardButton(text='🔄 Проверить платежи', callback_data='admin_payments')],
        ]
    )
