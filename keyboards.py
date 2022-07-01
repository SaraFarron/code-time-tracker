from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup,
)


def add_inline_buttons(buttons: dict[str: str], keyboard: InlineKeyboardMarkup) -> InlineKeyboardMarkup:
    """Return inline keyboard with buttons added"""

    for button_name, button_callback in buttons.items():
        keyboard.add(InlineKeyboardButton(button_name, callback_data=button_callback))

    return keyboard


def add_reply_buttons(buttons: list[str,], keyboard: ReplyKeyboardMarkup) -> ReplyKeyboardMarkup:
    """Return inline keyboard with buttons added"""

    for button_name in buttons:
        keyboard.add(button_name)

    return keyboard


menu_buttons = {
    'All time stats': 'retrieve_all',
    'Last week stats': 'last_week',
    'Update Wakatime API key': 'update_key',
}

menu = InlineKeyboardMarkup()
menu = add_inline_buttons(menu_buttons, menu)
