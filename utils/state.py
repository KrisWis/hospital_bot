from aiogram.fsm.state import State, StatesGroup


class APanelState(StatesGroup):
    wait_user = State()
    wait_message = State()
    wait_message_name = State()
    wait_message_url = State()
    wait_fio = State()
    wait_phone = State()
    wait_date_start = State()


class UserState(StatesGroup):
    wait_sighting = State()
    wait_optg = State()
    wait_kt = State()
    wait_trg = State()
    wait_blood = State()
    wait_implantation = State()
    wait_procedur = State()
