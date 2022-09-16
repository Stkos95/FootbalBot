from aiogram.dispatcher.filters.state import State, StatesGroup


class ChoiceTeam(StatesGroup):
    tournament = State()
    team = State()
    confirmation = State()

class AddPlayer(StatesGroup):
    second_name = State()
    name = State()
    birthday = State()
    photo = State()
