from sqlalchemy import select
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from tg_bot.misc import joinFootball
from tg_bot.keyboards.callbackdatas import confirmation_callback
from tg_bot.misc.database.db import  get_engine_connection
from tg_bot.misc.database.models import Admins, Tournaments, Teams, Confirmation

Session = get_engine_connection()
# joinFootball.prepare_teams()

async def registration_get_result_confirm(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    row_id = callback_data.get('bd_data')
    await call.answer()
    await call.message.answer('Вы подтвердили!!')
    await call.message.delete_reply_markup()
    with Session() as session:
        statement = select(Confirmation).where(Confirmation.id == int(row_id))
        result = session.execute(statement).scalars().first()
        print(result.user_id)
        session.add(Admins(user_id=result.user_id, team_id=result.team_id))
        session.commit()
        await call.bot.send_message(result.user_id,'Вашу заявку подтвердили, можете продолжить пользоваться ботом!')



async def registration_get_result_reject(call:types.CallbackQuery, state:FSMContext, callback_data: dict):
    row_id = callback_data.get('bd_data')
    await call.answer()
    with Session() as session:
        statement = select(Confirmation).where(Confirmation.id == int(row_id))
        result = session.execute(statement).scalars().first()
    await call.message.answer(f'Вы Отказали {result.user_full_name}!!')
    await call.message.delete_reply_markup()














def registration_result(dp: Dispatcher):
    dp.register_callback_query_handler(registration_get_result_confirm, confirmation_callback.filter(result='confirm'))
    dp.register_callback_query_handler(registration_get_result_reject, confirmation_callback.filter(result='reject'))