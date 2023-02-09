
from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy import select, and_, distinct
from tg_bot.misc.database.db import  Session
from tg_bot.misc.database.models import Tournaments, Teams, Confirmation, Users, Admins, TeamTournaments
from aiogram.dispatcher import FSMContext
from tg_bot.keyboards.inline import admin_kb_confirm_registration
from tg_bot.keyboards.callbackdatas import team_choice_callback
from tg_bot.handlers.admin.add_player import admin_start, enter_player_name
from tg_bot.misc.funcs.get_lists_func import get_tournaments
from tg_bot.keyboards.callbackdatas import admin_callback_data


from dataclasses import dataclass

MAX_COUNT_ADMINS = 3 # Не используется
regular_tournaments = (1025285, 1026113)


# добавить хэндлер с вопросом, где узнать кем хочет стать пользователь игрок/админ и тд
@dataclass
class UserInfo:
    user_full_name: str = None
    user_id: str = None
    username: str = None
    in_base: bool = False

@dataclass
class AdminData:
    user: UserInfo
    team_id: int = None
    team_name: str = None

async def cancel(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer('Отмена!')
    await call.message.edit_reply_markup(reply_markup=None)
    await state.finish()

async def greeting_funct(message: types.Message, state: FSMContext):
    await message.answer('Привет')
    with Session() as session:
        statement_admin = select(Admins).where(Admins.user_id == message.from_user.id)
        admin = session.execute(statement_admin).scalars().all()
        # if admin[0].user.permision_id == 0:
        #     # from admin/add_player
        #     await admin_start(message, state)
        #     return
        # print(admin[0].user.permision_id)
        # await state.update_data(admin_data=admin)
        if not admin:
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text='Регистрация', callback_data='add_team'),
                    InlineKeyboardButton(text='Отмена', callback_data='cancel'),
                ]
            ])
            await message.answer('Вы не являетесь администратором команды.\nДля добавления команды, нажмите "Зарегистрироваться"',
                                 reply_markup=kb)

        else:
            await state.update_data(admin_data=admin)
            answer = ', '.join(i.team.team_name for i in admin)
            kb_my_teams = InlineKeyboardMarkup()
            for team in admin:
                kb_my_teams.add(InlineKeyboardButton(text=team.team.team_name, callback_data=team_choice_callback.new(team_id=team.team_id)))
            kb_my_teams.insert(InlineKeyboardButton(text='Добавить команду➕', callback_data='add_team'))
            await message.answer(f'Вы администратор команды "{answer}"\n'
                             f'Выберите действие:',
                             reply_markup=kb_my_teams)

def get_user_data(message):
    with Session() as session:
        statement_user = select(Users).where(Users.user_id == int(message.from_user.id))
        user_from_db = session.execute(statement_user).scalars().first()
        user = AdminData(
            user=UserInfo(
                user_id=message.from_user.id,
                username=message.from_user.username
            )
        )
        if user_from_db:
            user.user.in_base = True
            user.user.user_full_name = user_from_db.user_full_name
        return user


async def registration_callback(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text('Вы выбрали регистрацию')
    user = get_user_data(call)
    await state.update_data(admin=user)
    if not user.user.in_base:
        await call.message.answer('Введите свое ФИО:')
        await state.set_state('not_registered_fio')
    else:
        await get_list_tournaments(call.message, state)


async def registration_fio(message: types.Message,state: FSMContext):
    async with state.proxy() as data:
        data['admin'].user.user_full_name = message.text
        user = data.get('admin')
    send_user_db(user.user)
    await get_list_tournaments(message, state)


async def get_list_tournaments(message: types.Message, state: FSMContext):
    with Session() as session:
        tournaments = get_tournaments(session)
        kb = InlineKeyboardMarkup()
        [kb.insert(InlineKeyboardButton(text=i[1], callback_data=i[0])) for i in tournaments]
        kb.insert(InlineKeyboardButton(text='Отмена❌', callback_data='cancel'))
        # await message.answer('Выберите лигу, где играет ваша команда:',
        #                      reply_markup=kb)
        await message.answer('Турнир, где играет ваша команда:',
                             reply_markup=kb)
        await state.set_state('not_registered_rounds')


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
        await state.set_state('not_registered_1')




async def registration_start(call: types.CallbackQuery, state: FSMContext):
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

    await state.set_state('not_registered_team')
    await state.update_data(teams=teams)

# Добавлять ли ограничение по количеству админов?
async def registration_team_chocen(call: types.CallbackQuery, state: FSMContext):
    team_id = int(call.data)
    print(team_id)

    async with state.proxy() as data:
        # if data['admin_data'].user.permision_id == 0:
        #     await enter_player_name(call, state)
        admin = [i for i in data.get('admin_data') if i.team_id == team_id]
        data['admin'].team_id = team_id
        print(data['admin'])
        data['admin'].team_name = [i.team.team_name for i in data.get('teams') if i.team_id == team_id][0]
        user = data['admin']
    if admin:
        await call.message.answer(f'Вы уже являетесь администратором {user.team_name}')
        return

    row_id = send_confirm_database_return_row_id(user)
    await send_message_to_admin(call.message, state, data['admin'], row_id)
    await call.message.answer('Ваша заявка на администрирование командой отправлена на подтверждение, ожидайте.', )
    await state.finish()


def send_confirm_database_return_row_id(user: AdminData):
    temporary_confirmation = Confirmation(user_id=int(user.user.user_id), team_id=user.team_id,
                                          user_full_name=user.user.user_full_name,
                                          username=user.user.username)
    with Session() as session:
        session.add(temporary_confirmation)
        session.commit()
        row_id = temporary_confirmation.id
    return row_id

def send_user_db(user: UserInfo):
        with Session() as session:
            user_add = Users(user_id=int(user.user_id),
                  user_full_name=user.user_full_name,
                  username=user.username
                 )
            session.add(user_add)
            session.commit()


async def send_message_to_admin(message, state, user: AdminData, row_id):
    config = message.bot.get('config')

    await message.bot.send_message(chat_id=config.admin, text=f'Была отправлена заявка на управление командой {user.team_name} от {user.user.user_full_name} (@{user.user.username})!',
                                   reply_markup=admin_kb_confirm_registration(row_id))
    await state.finish()


def register_greet(dp: Dispatcher):

    dp.register_callback_query_handler(cancel, text='cancel', state='*')
    dp.register_callback_query_handler(get_list_rounds, state='not_registered_rounds')
    # dp.register_callback_query_handler(get_list_tournaments, admin_callback_data.filter())
    dp.register_message_handler(registration_fio , state='not_registered_fio')
    dp.register_callback_query_handler(registration_callback, text='add_team')
    dp.register_message_handler(greeting_funct, commands=['registration'])
    dp.register_callback_query_handler(registration_start, state='not_registered_1')
    dp.register_callback_query_handler(registration_team_chocen, state='not_registered_team')

