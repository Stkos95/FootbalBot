import random
from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy import select
from tg_bot.misc.database.db import  get_engine_connection
from tg_bot.misc.database.models import Admins, Tournaments, Teams, Confirmation, Users, TeamTournaments
from aiogram.dispatcher import FSMContext
from tg_bot.keyboards.inline import admin_kb_confirm_registration
from tg_bot.misc.funcs.get_lists_func import get_squad, get_squad_answer

from tg_bot.misc.image_processing.get_list_teams import process_players
from tg_bot.misc.doubles.join_api import get_not_requested_players
from tg_bot.misc.image_processing.get_list_teams import get_tournaments_for_concrete_team

from tg_bot.keyboards.callbackdatas import team_choice_callback, my_team_callback


Session = get_engine_connection()





async def my_team(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    team_id = callback_data.get('team_id')
    await call.message.answer('Выберите что вас интересует:', reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Состав', callback_data=my_team_callback.new(topic='squad', team_id=team_id)),
                InlineKeyboardButton(text='Турниры', callback_data=my_team_callback.new(topic='tournaments', team_id=team_id))
            ]
        ]
    ))



async def get_my_squad(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    team_id = callback_data.get('team_id')
    await call.answer()
    # await state.update_data(team_players=players)
    players = get_squad(team_id)
    answer = get_squad_answer(players)

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Добавить игрока', callback_data='add_player')
            ]
        ]
    )
    await call.message.answer(answer, reply_markup=kb)



async def get_my_tournaments(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await call.answer()
    team_id = int(callback_data.get('team_id'))
    with Session() as session:
        statement = select(TeamTournaments).where(TeamTournaments.team_id == team_id)
        tournamentsOfTeam = session.execute(statement).scalars().all()
        print(tournamentsOfTeam)


    # res = get_tournaments_for_concrete_team(team_id)
        kb = InlineKeyboardMarkup()
        # print(res)
        for tournament in tournamentsOfTeam:
            tournament_name = tournament.tournament.name_tournament + ' ' + tournament.tournament.name_round
            kb.insert(InlineKeyboardButton(text=tournament_name, callback_data=tournament.round_id))
        await call.message.answer('Команда учавствует в указанных турнирах:', reply_markup=kb)




def work_with_my_team(dp: Dispatcher):
    dp.register_callback_query_handler(my_team, team_choice_callback.filter())
    dp.register_callback_query_handler(get_my_squad, my_team_callback.filter(topic='squad'))
    dp.register_callback_query_handler(get_my_tournaments, my_team_callback.filter(topic='tournaments'))
