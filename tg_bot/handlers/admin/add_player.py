from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from tg_bot.misc.joinfootball_requests import GetJoinfootball
from tg_bot.filter.admin_filter import AdminCheck

async def enter_player_name(message: types.Message, state: FSMContext,):

    await message.answer('Для поиска игрока в базе введи имя:')
    await state.set_state('request_fio')


async def check_player_fio_in_teams(message: types.Message, state: FSMContext):
    player_fio = message.text
    if any(map(lambda x: x.isdigit(), player_fio)):
        await message.answer('Некорректно указано имя игрока, введите еще раз:')
        return

    site_connection = GetJoinfootball()
    players_found = site_connection.get_player(player_fio)
    print(players_found)
    if not players_found:
        await message.answer("Игрок не найден!\n Попробуйте еще раз. Перепроверьте правильность написания имени и попробуйте еще раз.\n"
                             "Если игрок найден не будет, то для того, чтобы зарегистрировать нового игрока, нажмите на кнопку 'Зарегистрировать игрока'")

        await state.set_state('find_player') # возможно изменить
        return

    text = 'Найдены игроки:\n'
    kb = types.InlineKeyboardMarkup(row_width=2)
    for  player_id in players_found:
        text += f'{player_id}) {players_found[player_id]}\n'
        kb.insert(types.InlineKeyboardButton(text=players_found[player_id], callback_data=player_id))
    await message.answer(text, reply_markup=kb)



def players_request(dp: Dispatcher):
    dp.register_message_handler(enter_player_name,is_admin=True, commands='request_player')
    dp.register_message_handler(check_player_fio_in_teams, state='request_fio')
