import random
from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from sqlalchemy import select, and_
from tg_bot.misc.database.db import  get_engine_connection
from tg_bot.misc.database.models import Tournaments, Teams, Confirmation, Users
from aiogram.dispatcher import FSMContext
from tg_bot.keyboards.inline import admin_kb_confirm_registration
from dataclasses import dataclass
Session = get_engine_connection()
MAX_COUNT_ADMINS = 3 # Не используется


@dataclass()
class UserFromBase:
    user_full_name: str = None
    team_name: str = None
    user_id: str = None
    team_id: str = None
    username: str = None
    in_base: bool = False


async def cancel(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer('Отмена!')
    await call.message.edit_reply_markup(reply_markup=None)
    await state.finish()


async def registration_callback(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text('Вы выбрали регистрацию')
    user_id = call.from_user.id
    with Session() as session:
        statement1 = select(Tournaments.tournament_id, Tournaments.name)
        tournaments = session.execute(statement1).all()
        kb = InlineKeyboardMarkup()
        [kb.insert(InlineKeyboardButton(text=i[1], callback_data=i[0])) for i in tournaments]
        kb.insert(InlineKeyboardButton(text='Отмена❌', callback_data='cancel'))
        await call.message.answer('Выберите лигу, где играет ваша команда:',
                             reply_markup=kb)
        await state.set_state('not_registered_1')
        await state.update_data(user_id=user_id)
        await state.update_data(is_old=True)


async def greeting_funct(message: types.Message, state: FSMContext):
    await message.answer('Привет')
    user_id = message.from_user.id
    with Session() as session:
        statement = select(Users).where(Users.user_id == user_id)
        admin = session.execute(statement).scalars().all()
        user = UserFromBase(username=message.from_user.username, user_id=user_id)
        await state.update_data(admin=user)
        if not admin:
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text='Регистрация', callback_data='add_team'),
                    InlineKeyboardButton(text='Отмена', callback_data='cancel'),
                ]
            ])
            await message.answer('Вы не зарегистрированы.\nДля регистрации нажмите на кнопку Зарегистрироваться',
                                 reply_markup=kb)

        else:
            user.user_full_name=admin[0].user_full_name,
            user.in_base=True


            # await state.update_data(admin=user)
            answer = ', '.join(i.team.team_name for i in admin)
            kb_my_teams = InlineKeyboardMarkup()
            for team in admin:
                kb_my_teams.add(InlineKeyboardButton(text=team.team.team_name, callback_data=team.team_id))
            kb_my_teams.insert(InlineKeyboardButton(text='Добавить команду➕', callback_data='add_team'))
            await message.answer(f'Вы администратор команды "{answer}"\n'
                             f'Выберите действие:',
                             reply_markup=kb_my_teams)


async def registration_start(call: types.CallbackQuery, state: FSMContext):
    tournament_id = call.data
    print(tournament_id)
    await call.answer()
    with Session() as session:
        statement = select(Teams.team_id, Teams.team_name).where(Teams.tournament_id == tournament_id)
        teams = session.execute(statement).all()
        kb = InlineKeyboardMarkup()
        [kb.insert(InlineKeyboardButton(text=i[1], callback_data=i[0])) for i in teams]
        kb.insert(InlineKeyboardButton(text='Отмена❌', callback_data='cancel'))
        await call.message.answer('Выберите вашу команду:', reply_markup=kb)

    await state.set_state('not_registered_team')
    await state.update_data(teams=teams)



# Добавлять ли ограничение по количеству админов?
async def registration_team_chocen(call: types.CallbackQuery, state: FSMContext):
    team_id = int(call.data)
    async with state.proxy() as data:
        data['admin'].team_id = team_id
        data['admin'].team_name = [i[1] for i in data.get('teams') if i[0] == team_id][0]
        user = data['admin']

    if user.in_base:
        try:
            row_id = send_data_database_return_row_id(data['admin'])
            await send_message_to_admin(call.message, state, data['admin'], row_id)
        except:
            await call.message.answer(f'Вы уже являетесь администратором {user.team_name}')
        finally:
            await state.finish()
    else:
        await call.message.edit_text('Введите свое ФИО:')
        await state.set_state('not_registered_fio')

def send_data_database_return_row_id(user):

    temporary_confirmation = Confirmation(user_id=user.user_id, team_id=user.team_id, user_full_name=user.user_full_name,
                                          username=user.username)
    with Session() as session:
        session.add(temporary_confirmation)
        session.commit()
        row_id = temporary_confirmation.id
        session.add(
            Users(user_id=user.user_id, user_full_name=user.user_full_name, username=user.username, team_id=user.team_id, permisions=1))
        session.commit()
    return row_id

async def registration_name_input(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['admin'].user_full_name = message.text
    user = data['admin']
    row_id = send_data_database_return_row_id(user)
    await send_message_to_admin(message, state, user, row_id)
    await message.answer('Ваша заявка на администрирование командой отправлена на подтверждение, ожидайте.',)
    await state.finish()

    # Отправляю сообщение себе/администратору
async def send_message_to_admin(message, state, user, row_id):
    config = message.bot.get('config')

    await message.bot.send_message(chat_id=config.admin, text=f'Была отправлена заявка на управление командой {user.team_name} от {user.user_full_name} (@{user.username})!',
                                   reply_markup=admin_kb_confirm_registration(row_id))
    await state.finish()



def register_greet(dp: Dispatcher):
    dp.register_callback_query_handler(cancel, text='cancel', state='*')
    dp.register_callback_query_handler(registration_callback, text='add_team')
    dp.register_message_handler(greeting_funct, commands=['registration'])
    dp.register_callback_query_handler(registration_start, state='not_registered_1')
    dp.register_callback_query_handler(registration_team_chocen, state='not_registered_team')
    dp.register_message_handler(registration_name_input, state='not_registered_fio')

