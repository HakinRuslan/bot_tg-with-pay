from aiogram.fsm.state import StatesGroup, State
from aiogram.filters.callback_data import CallbackData


class Pagination(CallbackData, prefix="pag"):
    page: int

class Addtypeoftariff(StatesGroup):
    type_tarif_name = State()
    how_much_days = State()
    confirm_add = State()

class Addtariff(StatesGroup):
    name = State()
    description = State()
    price = State()
    type_of_tarrifs_id = State()
    confirm_add = State()