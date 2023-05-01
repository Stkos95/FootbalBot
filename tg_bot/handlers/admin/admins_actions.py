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
from tg_bot.handlers.admin.add_player import enter_player_name


async def admin_start(message: types.Message, state: FSMContext):
    await message.answer('Ты администратор всея бота!!')

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='Добавить игрока в команду', callback_data=admin_callback_data.new(action='add_player') )
        ],
        [
            InlineKeyboardButton(text='Создать картинку с трансфером', callback_data=admin_callback_data.new(action='transfer_picture'))
        ]
    ])
    await message.answer('Ты администратор!\nВыбери действие:', reply_markup=kb)

async def get_list_tournaments_for_admin(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    chosen_action = callback_data.get('action')
    await state.update_data(action=chosen_action)

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


async def final_choice(call: types.CallbackQuery, state: FSMContext):

    team_id = int(call.data)
    players = get_squad(team_id)
    answer = get_squad_answer(players)
    await call.message.answer(answer)
    async with state.proxy() as data:
        data['team_id'] = team_id
    action = await state.get_data('action')
    match action.get('action'):
        case 'add_player':
            await enter_player_name(call, state)
        # case 'transfer_picture':
            # Вызов хэндлера для создания карточки.





def admin_choice_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(get_list_tournaments_for_admin, admin_callback_data.filter(action='add_player'))
    dp.register_callback_query_handler(get_list_rounds, state='admin_list_tournaments')
    dp.register_callback_query_handler(get_list_teams, state='admin_list_rounds')
    dp.register_callback_query_handler(final_choice, state='admin_list_teams')
