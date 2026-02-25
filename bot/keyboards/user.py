from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='💳 Купить подписку', callback_data='buy')],
            [InlineKeyboardButton(text='🎁 Пробный период', callback_data='trial')],
            [InlineKeyboardButton(text='📄 Моя подписка', callback_data='my_sub')],
            [InlineKeyboardButton(text='🆘 Написать в поддержку', callback_data='support')],
        ]
    )


def buy_confirm_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='✅ Я оплатил', callback_data='paid')],
            [InlineKeyboardButton(text='⬅️ В меню', callback_data='menu')],
        ]
    )
