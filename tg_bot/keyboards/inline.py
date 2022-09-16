from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from tg_bot.keyboards.callbackdatas import team_callback

def generate_kb_team_choice(values):
    kb = InlineKeyboardMarkup(row_width=2)

    [kb.insert(InlineKeyboardButton(text=i, callback_data=team_callback.new(name=i.strip()))) for i in values]
    return kb



