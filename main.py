from aiogram import Bot, Dispatcher
import asyncio

from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import load_config
from tg_bot.handlers.echo import register
from tg_bot.handlers.authorisation import register_greet
from tg_bot.handlers.admins_confirm import registration_result
from tg_bot.handlers.templates_messages import registration_answer_template
def register_handlers(dp):
    register(dp)
    register_greet(dp)
    registration_answer_template(dp)
    registration_result(dp)

config = load_config()




async def main():

    bot = Bot(token=config.token,parse_mode='HTML')
    memory = MemoryStorage()
    dp = Dispatcher(bot, storage=memory)
    register_handlers(dp)
    bot['config'] = config

    try:
        await dp.start_polling()
    finally:
        await bot.session.close()





# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    asyncio.run(main())
