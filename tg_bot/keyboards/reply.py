from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def generate_kb_list_of_tournaments(values):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    [kb.insert(KeyboardButton(str(i))) for i in values]

    return kb





