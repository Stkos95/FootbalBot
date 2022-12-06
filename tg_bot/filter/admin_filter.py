from aiogram.dispatcher.filters import BoundFilter


from config import Config

class AdminCheck(BoundFilter):
    key = 'is_admin'

    def __init__(self, is_admin=False):
        self.is_admin = is_admin



    async def check(self, obj):
        if self.is_admin:
            config: Config = obj.bot.get('config')
            user_id = obj.from_user.id
            return user_id == config.admin