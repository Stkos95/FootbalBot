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
    text += '\n'.join([f'{i + 1}) {val}' for i, val in enumerate(team_dict)])
    await message.answer(text, reply_markup=generate_kb_team_choice(team_dict))
    print(generate_kb_team_choice)
    await ChoiceTeam.team.set()

async def processing_team(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await call.answer()
    team_name = callback_data.get('name')
    async with state.proxy() as data:
        data['session']



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
    dp.register_message_handler(get_tournaments_list, commands=['start'])
    dp.register_message_handler(get_team_name, state=ChoiceTeam.tournament)
    # dp.register_message_handler(check_photo, content_types= types.ContentTypes.DOCUMENT | types.ContentTypes.PHOTO)
    dp.register_callback_query_handler(processing_team, team_callback.filter(), state=ChoiceTeam.team )
