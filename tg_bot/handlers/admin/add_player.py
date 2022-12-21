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





async def admin_start(message: types.Message, state: FSMContext):

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='Добавить игрока в команду', callback_data=admin_callback_data.new(action='add_player') )
        ],
        [
            InlineKeyboardButton(text='Создать картинку с трансфером', callback_data=admin_callback_data.new(action='transfer_picture'))
        ]
    ])
    await message.answer('Ты администратор!\nВыбери действие:', reply_markup=kb)

async def get_list_tournaments_for_admin(call: types.CallbackQuery, state: FSMContext):
    with Session() as session:
        tournaments = get_tournaments(session)
        kb = InlineKeyboardMarkup()
        [kb.insert(InlineKeyboardButton(text=i[1], callback_data=i[0])) for i in tournaments]
        kb.insert(InlineKeyboardButton(text='Отмена❌', callback_data='cancel'))
        # await message.answer('Выберите лигу, где играет ваша команда:',
        #                      reply_markup=kb)
        await call.message.answer('Турнир, где играет ваша команда:',
                             reply_markup=kb)
        await state.set_state('admin_list_tournaments')


async def get_list_rounds(call: types.CallbackQuery, state: FSMContext):
    tournament_id = int(call.data)
    await call.answer()
    with Session() as session:
        statement = select(Tournaments.round_id, Tournaments.name_round).where(Tournaments.tournament_id == tournament_id)
        rounds = session.execute(statement).all()
        kb = InlineKeyboardMarkup()
        [kb.insert(InlineKeyboardButton(text=i[1], callback_data=i[0])) for i in rounds]
        await call.message.answer('Лига, где играет ваша команда:',
                             reply_markup=kb)
        await state.set_state('admin_list_rounds')

async def get_list_teams(call: types.CallbackQuery, state: FSMContext):
    round_id = int(call.data)
    await call.answer()
    with Session() as session:
        statement = select(TeamTournaments).join(Teams).where(TeamTournaments.round_id == round_id)
        teams = session.execute(statement).scalars().all()
        print(teams)
        kb = InlineKeyboardMarkup()
        [kb.insert(InlineKeyboardButton(text=i.team.team_name, callback_data=i.team_id)) for i in teams]
        kb.insert(InlineKeyboardButton(text='Отмена❌', callback_data='cancel'))
        await call.message.answer('Выберите вашу команду:', reply_markup=kb)

    await state.set_state('admin_list_teams')
    await state.update_data(teams=teams)





async def enter_player_name(call: types.CallbackQuery, state: FSMContext,):
    team_id = int(call.data)
    players = get_squad(team_id)
    answer = get_squad_answer(players)
    await call.message.answer(answer)
    async with state.proxy() as data:
        data['team_id'] = team_id
    await call.message.answer('Для поиска игрока в базе введи имя:')
    await state.set_state('request_fio')


async def check_player_fio_in_teams(message: types.Message, state: FSMContext):
    player_fio = message.text
    if any(map(lambda x: x.isdigit(), player_fio)):
        await message.answer('Некорректно указано имя игрока, введите еще раз:')
        return

    site_connection = GetJoinfootball()
    players_found = site_connection.get_player(player_fio)
    if not players_found:
        await message.answer("Игрок не найден!\n Попробуйте еще раз. Перепроверьте правильность написания имени и попробуйте еще раз.\n"
                             "Если игрок найден не будет, то для того, чтобы зарегистрировать нового игрока, нажмите на кнопку 'Зарегистрировать игрока'")

        return

    text = 'Найдены игроки, выберите из списка:\n'
    kb = types.InlineKeyboardMarkup(row_width=2)
    for  indx,player_id in enumerate(players_found):
        text += f'{indx + 1}) {players_found[player_id]["name"]}, {players_found[player_id]["birthday"]} г.р.\n'
        kb.insert(types.InlineKeyboardButton(text=players_found[player_id]['name'], callback_data=player_id))
    await message.answer(text, reply_markup=kb)
    await state.set_state('player_found')

async def add_found_player(call: types.CallbackQuery, state: FSMContext):
    print('hello')
    await call.answer()
    async with state.proxy() as data:
        team_id = data.get('team_id')
        players = process_players(team_id)
        print(players)
        print(call.data)
        if int(call.data) in players:
            await call.message.answer('Игрок уже в команде!')
            await state.finish()
        await call.message.answer('Игрок добавлен в команду!')



def players_request(dp: Dispatcher):
    dp.register_callback_query_handler(enter_player_name, text='add_player')
    dp.register_callback_query_handler(enter_player_name, state='admin_list_teams')
    dp.register_message_handler(check_player_fio_in_teams, state='request_fio')
    dp.register_callback_query_handler(add_found_player, state='player_found')
    dp.register_callback_query_handler(get_list_tournaments_for_admin, admin_callback_data.filter(action='add_player'))
    dp.register_callback_query_handler(get_list_rounds, state='admin_list_tournaments')
    dp.register_callback_query_handler(get_list_teams, state='admin_list_rounds')

