from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from tg_bot.keyboards.callbackdatas import team_callback, confirmation_callback

def generate_kb_team_choice(values):
    kb = InlineKeyboardMarkup(row_width=2)

    [kb.insert(InlineKeyboardButton(text=i, callback_data=team_callback.new(name=i.strip()))) for i in values]
    return kb


def admin_kb_confirm_registration(data):

    kb = InlineKeyboardMarkup(row_width=2, inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Подтвердить',
                callback_data=confirmation_callback.new(result='confirm', bd_data=data)
            ),
            InlineKeyboardButton(
                text='Отказать',
                callback_data=confirmation_callback.new(result='reject', bd_data=data)
            ),

        ]
    ])
    return kb



