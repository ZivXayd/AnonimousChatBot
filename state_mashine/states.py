from aiogram.dispatcher.filters.state import State, StatesGroup

class ChatStates(StatesGroup):
    stop_chat_state = State()
    play_chat_state = State()