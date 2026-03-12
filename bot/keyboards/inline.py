from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='💳 Купить подписку', callback_data='buy')],
            [InlineKeyboardButton(text='🎁 Пробный период', callback_data='trial')],
            [InlineKeyboardButton(text='📄 Моя подписка', callback_data='my_sub')],
            [InlineKeyboardButton(text='📘 Как подключить', callback_data='howto')],
            [InlineKeyboardButton(text='🆘 Написать в поддержку', callback_data='support')],
        ]
    )


def get_subscription_keyboard(subscription_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='₿ Оплатить через Crypto Bot', callback_data=f'pay_crypto:{subscription_id}')],
            [InlineKeyboardButton(text='₽ Оплатить через донаты', callback_data=f'pay_donation:{subscription_id}')],
            [InlineKeyboardButton(text='⬅️ В меню', callback_data='menu')],
        ]
    )


def get_payment_methods_keyboard(subscription_id: int) -> InlineKeyboardMarkup:
    return get_subscription_keyboard(subscription_id)


def check_payment_kb(payment_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='🔄 Проверить оплату', callback_data=f'check_payment:{payment_id}')],
            [InlineKeyboardButton(text='⬅️ В меню', callback_data='menu')],
        ]
    )


def buy_methods_kb(subscription_id: int) -> InlineKeyboardMarkup:
    return get_payment_methods_keyboard(subscription_id)


def main_menu_kb() -> InlineKeyboardMarkup:
    return get_main_keyboard()
