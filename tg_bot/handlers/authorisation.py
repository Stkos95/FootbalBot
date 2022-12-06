import random
from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from sqlalchemy import select, and_
from tg_bot.misc.database.db import  get_engine_connection
from tg_bot.misc.database.models import Tournaments, Teams, Confirmation, Users
from aiogram.dispatcher import FSMContext
from tg_bot.keyboards.inline import admin_kb_confirm_registration

Session = get_engine_connection()
MAX_COUNT_ADMINS = 3 # Не используется


async def registration_message(message: types.Message, state: FSMContext):
    await message.answer("вы выбрали регистрацию!")
    user_id = message.from_user.id
    with Session() as session:
        statement1 = select(Tournaments.tournament_id, Tournaments.name)
        tournaments = session.execute(statement1).all()
        kb = InlineKeyboardMarkup()
        [kb.insert(InlineKeyboardButton(text=i[1], callback_data=i[0])) for i in tournaments]
        await message.answer('Вы не авторизованы, нужно вас зарегистрировать. Выберите лигу, где играет ваша команда?',
                             reply_markup=kb)
        await state.set_state('not_registered_1')
        await state.update_data(user_id=user_id)



async def greeting_funct(message: types.Message, state: FSMContext):
    await message.answer('Привет')
    user_id = message.from_user.id
    with Session() as session:

        statement = select(Users).where(Users.user_id == user_id)
        admin = session.execute(statement).scalars().all()

        if not admin:
            kb = ReplyKeyboardMarkup(keyboard=[
                [
                    KeyboardButton(text='Регистрация'),
                    KeyboardButton(text='Отмена'),
                ]
            ],resize_keyboard=True)
            await message.answer('Вы не зарегистрированы.\nДля регистрации нажмите на кнопку Зарегистрироваться',
                                 reply_markup=kb)

        else:
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
        await call.message.answer('Выберите вашу команду:', reply_markup=kb)

    await state.set_state('not_registered_team')
    await state.update_data(teams=teams)




# Добавлять ли ограничение по количеству админов?
async def registration_team_chocen(call: types.CallbackQuery, state: FSMContext):
    team_id = int(call.data)
    print(team_id)
    async with state.proxy() as data:
        data['team_id'] = team_id
        data['team_name'] = [i[1] for i in data.get('teams') if i[0] == team_id][0]

    with Session() as session:
        statement = select(Users)
        person = session.execute(statement).scalars().first()
    if person:
        await registration_name_input(call.message, state, person)
        await state.finish()
    else:
        await call.message.answer('Введите свое ФИО:')
        await state.set_state('not_registered_fio')


async def registration_name_input(message: types.Message, state: FSMContext, person=None):
    # Возможно добавить проверку на корректность имени.
    if person:
        user_full_name = person.user_full_name
    else:
        user_full_name = message.text
    username = message.from_user.username
    async with state.proxy() as data:
        user_id = data.get('user_id')
        team_name = data.get('team_name')
        team_id = data.get('team_id')

    with Session() as session:
        temporary_confirmation = Confirmation(user_id=user_id, team_id=team_id, user_full_name=user_full_name, username=username)
        session.add(temporary_confirmation)
        session.commit()
        row_id = temporary_confirmation.id

        team_admins = session.execute(select(Users).join(Teams).where(and_(Users.team_id == team_id, Users.permisions == 1))).all()

        print(team_admins)
        try:
            session.add(Users(user_id=user_id, user_full_name=user_full_name, username=username, team_id=team_id, permisions=1))
        except:
            pass
        session.commit()

    await message.answer('Ваша заявка на администрирование командой отправлена на подтверждение, ожидайте.',)
    await state.finish()


    # Отправляю сообщение себе/администратору
    config = message.bot.get('config')
    await message.bot.send_message(chat_id=config.admin, text=f'Была отправлена заявка на управление командой {team_name} от {user_full_name} (@{username})!',
                                   reply_markup=admin_kb_confirm_registration(row_id))
    await state.finish()



def register_greet(dp: Dispatcher):

    dp.register_message_handler(registration_message, text='Регистрация')
    dp.register_callback_query_handler(registration_callback, text='add_team')


    dp.register_message_handler(greeting_funct, commands=['registration'])
    dp.register_callback_query_handler(registration_start, state='not_registered_1')
    dp.register_callback_query_handler(registration_team_chocen, state='not_registered_team')
    dp.register_message_handler(registration_name_input, state='not_registered_fio')

