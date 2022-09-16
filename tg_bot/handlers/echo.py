import requests
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove
from tg_bot.misc import parsing_page
from tg_bot.keyboards.reply import generate_kb_list_of_tournaments
from tg_bot.keyboards.inline import generate_kb_team_choice
from tg_bot.FSM.states import ChoiceTeam
from io import BytesIO
from tg_bot.keyboards.callbackdatas import team_callback



async def get_tournaments_list(message: types.Message, state: FSMContext):
    session = requests.Session()
    list_of_tourn = parsing_page.get_list_of_tournaments(session)

    async with state.proxy() as data:
        data['tournaments'] = list_of_tourn
        data['session'] = session

    text = '\n'.join([f'{i}) {val.get("name")}' for i, val in list_of_tourn.items()])

    await message.answer(text, reply_markup=generate_kb_list_of_tournaments(list_of_tourn))
    await ChoiceTeam.first()

async def get_team_name(message: types.Message, state: FSMContext):
    number = int(message.text)
    async with state.proxy() as data:
        link = data['tournaments'].get(number).get('link')
        name = data['tournaments'].get(number).get('name')
        await message.answer(f'Вы выбрали турнир "{name}"', reply_markup=ReplyKeyboardRemove())
        text = 'Укажите номер, под которым указана ваша команда:\n'
        team_dict = parsing_page.get_list_of_teams(data['session'])
        data['teams'] = team_dict
    text += '\n'.join([f'{i + 1}) {val}' for i, val in enumerate(team_dict)])
    await message.answer(text, reply_markup=generate_kb_team_choice(team_dict))
    print(team_dict)
    await ChoiceTeam.team.set()

async def processing_team(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await call.answer()
    await state.update_data(team_name=callback_data.get('name'))
    team_name = callback_data.get('name')

    await call.message.answer(f'Вы выбрали команду {team_name}, Все верно?')
    await ChoiceTeam.confirmation.set()

async def refuse_chosen_team(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        team_dict = data['teams']
    await message.answer('Выберите команду повторно.', reply_markup=generate_kb_team_choice(team_dict))
    await ChoiceTeam.team.set()

async def confirm_chosen_team(message: types.Message, state: FSMContext):

    async with state.proxy() as data:
        team_name = data.get('team_name')
        team_id = data['teams'].get(team_name).split('=')[-1]  # в словаре ссылка формата http://lmfl.ru/cp/tournament/1017964/application/view?team_id=1203706
        team_link = f'http://lmfl.ru/cp/team/{team_id}/players'
        link_add_player = f'http://lmfl.ru/cp/player/profile/create?team_id={team_id}'
    print(team_link)







"""На предыдущем хэндлере выбирается команда, здесь сделать дозаявку игроков в выбранную команду...
сделать чтобы после выбора команды можно было дозаявить несколько игроков...
и чтобы бот отправлял админу инфу о том, что команда заявила игрока....
"""

# async def check_photo(message: types.Message):
#     match message.content_type:
#         case types.ContentType.PHOTO:
#             file_id = message.photo[-1].file_id
#             text = f'{message.content_type}: {file_id}'
#             with open('file_ids.txt', 'w') as file:
#                 file.write(text)
#
#             await message.answer_photo(photo=file_id)
#
#         case types.ContentType.DOCUMENT:
#             file_id = message.document.file_id
#             file_name = message.document.file_name
#
#             await message.answer_document(document=file_id, caption=file_name)

   # d = message.document.file_name

    # await message.answer_document(types.InputFile(save_to_io, filename='test.jpeg'))
    # print(save_to_io.getvalue())


    # await message.answer(f'file_id: {d}')




def register(dp: Dispatcher):
    dp.register_message_handler(refuse_chosen_team, (lambda message: message.text.strip().lower() == 'нет'), state=ChoiceTeam.confirmation)
    dp.register_message_handler(get_tournaments_list, commands=['start'])
    dp.register_message_handler(get_team_name, state=ChoiceTeam.tournament)
    # dp.register_message_handler(check_photo, content_types= types.ContentTypes.DOCUMENT | types.ContentTypes.PHOTO)
    dp.register_callback_query_handler(processing_team, team_callback.filter(), state=ChoiceTeam.team )
