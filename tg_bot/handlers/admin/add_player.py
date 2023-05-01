from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from tg_bot.misc.database.db import  Session
from tg_bot.keyboards.callbackdatas import admin_callback_data
from tg_bot.misc.database.models import Tournaments, TeamTournaments, Teams
from tg_bot.misc.funcs.get_lists_func import get_tournaments, get_squad, get_squad_answer
from tg_bot.misc.image_processing.get_list_teams import process_players
from tg_bot.misc.joinfootball_requests import GetJoinfootball
from tg_bot.filter.admin_filter import AdminCheck
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy import select, distinct










async def enter_player_name(call: types.CallbackQuery, state: FSMContext,):
    await call.message.answer('Для поиска игрока в базе введи имя:')
    await state.set_state('request_fio')


async def check_player_fio_in_teams(message: types.Message, state: FSMContext):
    player_fio = message.text
    if any(map(lambda x: x.isdigit(), player_fio)):
        await message.answer('Некорректно указано имя игрока, введите еще раз:')
        return

    site_connection = GetJoinfootball()
    players_found = site_connection.get_player(player_fio)
    print(f'{players_found=}')
    if not players_found:
        await message.answer("Игрок не найден!\n Попробуйте еще раз. Перепроверьте правильность написания имени и попробуйте еще раз.\n"
                             "Если игрок найден не будет, то для того, чтобы зарегистрировать нового игрока, нажмите на кнопку 'Зарегистрировать игрока'(кнопки пока нет :(( )")

        return

    # text = 'Найдены игроки, выберите из списка:\n'
    text = 'Найдены игроки, Укажите номер найденного игрока:\n'
    kb = types.InlineKeyboardMarkup(row_width=2)
    res = {}
    await state.update_data(found_players=res)
    for  indx,player_id in enumerate(players_found):

        text += f'{indx + 1}) {players_found[player_id]["name"]}, {players_found[player_id]["birthday"]} г.р.\n'
        players_found[player_id].update(player_id=player_id)
        res.update({indx + 1: players_found[player_id]})
    #     kb.insert(types.InlineKeyboardButton(text=players_found[player_id]['name'], callback_data=player_id))
    # await message.answer(text, reply_markup=kb)
    await message.answer(text)
    await state.set_state('player_found')



# async def add_found_player(call: types.CallbackQuery, state: FSMContext):
#     print('hello')
#     # await call.answer()
#     async with state.proxy() as data:
#         team_id = data.get('team_id')
#         players = process_players(team_id)
#         print(players)
#         # print(call.data)
#         if int(call.data) in players:
#             await call.message.answer('Игрок уже в команде!')
#             await state.finish()
#         else:
#             await call.message.answer('Игрок добавлен в команду!')


async def add_found_player(message: types.Message, state: FSMContext):
    try:
        player_number = int(message.text)
    except ValueError:
        await message.answer('Некорректно указан номер, возможно вы ввели не число, а слово, попробуйте еще раз.')
        return

    async with state.proxy() as data:
        team_id = data.get('team_id')
        players = process_players(team_id)
        found_players = data.get('found_players')
        print(found_players)
        print(players)

    try:
        if int(found_players[player_number]['player_id']) in players:
            await message.answer('Игрок уже в команде!')
            await state.finish()
        else:

            await message.answer('Игрок добавлен в команду!')

    except KeyError:
        await message.answer('Нет игрока под таким номером, проверьте номер внимательнее и попробуйте еще раз.')




def players_request(dp: Dispatcher):
    dp.register_callback_query_handler(enter_player_name, text='add_player')
    # dp.register_callback_query_handler(enter_player_name, state='admin_list_teams')
    dp.register_message_handler(check_player_fio_in_teams, state='request_fio')
    dp.register_message_handler(add_found_player, state='player_found')


