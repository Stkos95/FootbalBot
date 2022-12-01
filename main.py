from aiogram import Bot, Dispatcher
import asyncio

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from tg_bot.filter.admin_filter import AdminCheck
from config import load_config
from tg_bot.handlers.echo import register
from tg_bot.handlers.authorisation import register_greet
from tg_bot.handlers.admins_confirm import registration_result
from tg_bot.handlers.team.my_team import work_with_my_team
from tg_bot.handlers.income_outcome_templates.templates_messages import registration_answer_template
from tg_bot.handlers.admin.check_doubles import reg_doubles
<<<<<<< HEAD
from tg_bot.handlers.admin.add_player import players_request
=======
>>>>>>> ab8b64b (before devide registration to /registration command)

def register_handlers(dp):
    register(dp)
    register_greet(dp)
    registration_answer_template(dp)
    registration_result(dp)
    work_with_my_team(dp)
    reg_doubles(dp)
<<<<<<< HEAD
    players_request(dp)

def register_all_filters(dp):
    dp.filters_factory.bind(AdminCheck)
=======

>>>>>>> ab8b64b (before devide registration to /registration command)

config = load_config()




async def main():

    bot = Bot(token=config.token,parse_mode='HTML')
    memory = MemoryStorage()
    dp = Dispatcher(bot, storage=memory)
    register_all_filters(dp)
    register_handlers(dp)

    bot['config'] = config

    try:
        await dp.start_polling()
    finally:
        await bot.session.close()





# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    asyncio.run(main())
