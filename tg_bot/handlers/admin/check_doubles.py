from aiogram import types, Dispatcher
from tg_bot.misc.doubles.join_api import check_doubles_players





async def check_doubles(message: types.Message):
    await message.answer('Подождите...⏳')
    players = check_doubles_players(1026113)
    if not players:
        await message.answer('Повторяющихся игроков не найдено!')
        return
    text = ''
    for indx, player in enumerate(players):
        text += f'\n{indx + 1}) '
        text += '\n'.join(map(str,player))
    await message.answer(text)


def reg_doubles(dp: Dispatcher):
    dp.register_message_handler(check_doubles, commands=['admin_check'])










