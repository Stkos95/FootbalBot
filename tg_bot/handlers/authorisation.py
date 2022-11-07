import random
from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy import select
from tg_bot.misc.database.db import  get_engine_connection
from tg_bot.misc.database.models import Admins, Tournaments, Teams, Confirmation, Users
from aiogram.dispatcher import FSMContext
from tg_bot.keyboards.inline import admin_kb_confirm_registration

Session = get_engine_connection()
MAX_COUNT_ADMINS = 3


async def greeting_funct(message: types.Message, state: FSMContext):

    await message.answer('Привет')
    # user_id = message.from_user.id
    user_id = random.randint(1,1000000) # Убрать после тестирования
    with Session() as session:

        statement = select(Admins).join(Admins.team).where(Admins.user_id == user_id)
        admin = session.execute(statement).scalars().first()

        if not admin:
            statement1 = select(Tournaments.tournament_id, Tournaments.name)
            tournaments = session.execute(statement1).all()
            kb = InlineKeyboardMarkup()
            [kb.insert(InlineKeyboardButton(text=i[1], callback_data=i[0])) for i in tournaments]
            await message.answer('Вы не авторизованы, нужно вас зарегистрировать. Выберите лигу, где играет ваша команда?',
                                 reply_markup=kb)
            await state.set_state('not_registered_1')
            await state.update_data(user_id=user_id)
        else:
            await message.answer(f'Вы администратор команды "{admin.team.team_name}"')
            await state.set_state('registered_1') # Дальнейшие действия указаны в 'request_players'



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

    await call.message.answer('Введите свое ФИО:')
    await state.set_state('not_registered_fio')






async def registration_name_input(message: types.Message, state: FSMContext):
    # Возможно добавить проверку на корректность имени.
    user_full_name = message.text
    username = message.from_user.username
    async with state.proxy() as data:
        # user_name = data.get('user_name')
        user_id = data.get('user_id')
        team_name = data.get('team_name')
        team_id = data.get('team_id')

    with Session() as session:
        temporary_confirmation = Confirmation(user_id=user_id, team_id=team_id, user_full_name=user_full_name, username=username)
        session.add(temporary_confirmation)
        session.commit()
        row_id = temporary_confirmation.id
        team_admins = session.execute(select(Users.user_full_name).join(Admins.full_name).where(Admins.team_id == team_id)).all()
        print(team_admins)
        try:
            session.add(Users(user_id=user_id, user_full_name=user_full_name, username=username))
        except:
            session.add(Users(user_id=random.randint(1,100000), user_full_name=user_full_name, username=username))
        session.commit()

    await message.answer('Ваша заявка на администрирование командой отправлена на подтверждение, ожидайте.',)

    # Отправляю сообщение себе/администратору

    config = message.bot.get('config')
    await message.bot.send_message(chat_id=config.admin, text=f'Была отправлена заявка на управление командой {team_name} от {user_full_name} (@{username})!',
                                   reply_markup=admin_kb_confirm_registration(row_id))
    await state.finish()







def register_greet(dp: Dispatcher):
    dp.register_message_handler(greeting_funct, commands=['hello'])
    dp.register_callback_query_handler(registration_start, state='not_registered_1')
    dp.register_callback_query_handler(registration_team_chocen, state='not_registered_team')
    dp.register_message_handler(registration_name_input, state='not_registered_fio')




"""/start - бот проверяет зарегистрирован ли позователь, дальше 2 варианта:
1. Пользователь не авторизован: бот спрашивает ФИО, просит ввести название команды, и находит соответствующую команду на 
сайте (или выгружает из базы, которая хранит команды из АПИ) 
и предоставляет выбор пользователю. Когда пользователь выбрал команду, бот отправляет Админу запрос на подтверждение 
(чтобы избежать ситуаций, когда любой желающий может стать представителем команды).
Когда подтвердили представителя команды, то ему приходит уведомление и он заносится в БД.
2. Пользователь авторизован: бот находит его в бд, определяет его команду и уже спрашивает что и кого он хочет заявить. 

"""