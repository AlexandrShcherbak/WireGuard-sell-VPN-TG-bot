from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='💳 Купить подписку', callback_data='buy')],
            [InlineKeyboardButton(text='🎁 Пробный период', callback_data='trial')],
            [InlineKeyboardButton(text='📄 Моя подписка', callback_data='my_sub')],
            [InlineKeyboardButton(text='📘 Как подключить', callback_data='howto')],
            [InlineKeyboardButton(text='🆘 Написать в поддержку', callback_data='support')],
        ]
    )


def buy_methods_kb(subscription_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='₿ Оплатить через Crypto Bot', callback_data=f'pay_crypto:{subscription_id}')],
            [InlineKeyboardButton(text='₽ Оплатить через донаты', callback_data=f'pay_donation:{subscription_id}')],
            [InlineKeyboardButton(text='⬅️ В меню', callback_data='menu')],
        ]
    )


def check_payment_kb(payment_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='🔄 Проверить оплату', callback_data=f'check_payment:{payment_id}')],
            [InlineKeyboardButton(text='⬅️ В меню', callback_data='menu')],
        ]
    )
