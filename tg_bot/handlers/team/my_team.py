import random
from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy import select
from tg_bot.misc.database.db import  get_engine_connection
from tg_bot.misc.database.models import Admins, Tournaments, Teams, Confirmation, Users
from aiogram.dispatcher import FSMContext
from tg_bot.keyboards.inline import admin_kb_confirm_registration

from tg_bot.misc.image_processing.get_list_teams import process_players
from tg_bot.misc.doubles.join_api import get_not_requested_players


Session = get_engine_connection()





async def my_team(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer('Выберите что вас интересует:', reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Состав', callback_data='squad'),
                InlineKeyboardButton(text='Турниры', callback_data='tournaments')
            ]
        ]
    ))



async def get_my_squad(call: types.CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    await call.answer()
    with Session() as session:
        # statement = select(Admins).join(Admins.team).where(Admins.user_id == user_id)
        # admin = session.execute(statement).scalars().first()
        statement = select(Admins).where(Admins.user_id == user_id)
        admin = session.execute(statement).scalars().first()

        team_id = admin.team_id
        players = process_players(team_id)
        print(players)
    answer = 'Список игроков:\n'
    text = [f"{indx} - {player.get('name')}" for indx, player in enumerate(players.values())]
    answer += '\n'.join(text)
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Добавить игрока', callback_data='add_player')
            ]
        ]
    )
    await call.message.answer(answer, reply_markup=kb)



async def get_my_tournaments(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer('Пока работает для мини-футбола 2022/23')
    await call.answer()




def work_with_my_team(dp: Dispatcher):
    dp.register_callback_query_handler(my_team, text='my_team')
    dp.register_callback_query_handler(get_my_squad, text='squad')
