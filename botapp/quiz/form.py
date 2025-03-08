from aiogram.fsm.state import StatesGroup, State

class Useradd(StatesGroup):
    fio = State()
    date_birth = State()
    showstariff = State()
    paytariff = State()
    confirm_purch = State()