from aiogram.dispatcher.filters.state import State, StatesGroup


class ChoiceTeam(StatesGroup):
    tournament = State()
    team = State()