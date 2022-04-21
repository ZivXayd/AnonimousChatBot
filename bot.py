import random

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import state_mashine.states
from lang.translator import Translator
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram import Bot, types
import sqlite3
import config

db = sqlite3.connect(
    database='database.db'
)
cur = db.cursor()
bot = Bot(
    token=config.token
)
dp = Dispatcher(
    bot=bot,
    storage=MemoryStorage()
)
dp.middleware.setup(LoggingMiddleware())
translator = Translator()


translate_keyboard = InlineKeyboardMarkup()
translate_keyboard.add(
    InlineKeyboardButton(
        text='перевод сообщения',
        callback_data='translate_message'
    )
)

try:
    cur.execute(
        f'CREATE TABLE users ('
        f'user_id UNIQUE,'
        f'user2 INT'
        f');'
    )
except sqlite3.OperationalError:
    print('# база данных инициализирована')


@dp.message_handler(
    commands=['start']
)
async def start_command_handler(msg: types.Message):
    cur.execute(
        f'INSERT OR IGNORE INTO users (user_id) VALUES ({msg.from_user.id})'
    )
    db.commit()
    await msg.answer(
        text='Привет. Это анонимный чат бот.\n'
             'Для начала диалога напиши /play\n\n'
             'Удачных разговоров ;)'
    )


@dp.message_handler(
    commands=['play']
)
async def play_command_handler(msg: types.Message, state: FSMContext):
    await state_mashine.states.ChatStates.play_chat_state.set()

    users = random.choice(
        cur.execute(
            f'SELECT user_id FROM users WHERE user_id!={msg.from_user.id}'
        ).fetchall()
    )[0]

    cur.execute(
        f'UPDATE users SET user2={users} WHERE user_id={msg.from_user.id}'
    )
    cur.execute(
        f'UPDATE users SET user2={msg.from_user.id} WHERE user_id={users}'
    )
    db.commit()

    await msg.answer(
        text='Собеседник найден!\n\n'
             'Чтобы закончить общение - напиши /stop'
    )
    await bot.send_message(
        text='Собеседник найден!\n\n'
             'Чтобы закончить общение - напиши /stop',
        chat_id=users
    )



@dp.message_handler(content_types=['photo'])
async def image_message_handler(msg: types.Message):
    user2 = cur.execute(
        f'SELECT user2 FROM users WHERE user_id={msg.from_user.id}'
    ).fetchone()[0]
    await bot.send_photo(
        photo=msg.photo[0].file_id,
        chat_id=user2
    )


@dp.message_handler()
async def send_message_handler(msg: types.Message, state: FSMContext):
    user2 = cur.execute(
        f'SELECT user2 FROM users WHERE user_id={msg.from_user.id}'
    ).fetchone()[0]
    await bot.send_message(
        text=msg.text,
        reply_markup=translate_keyboard,
        chat_id=user2
    )


@dp.callback_query_handler(lambda c: c)
async def translate_handler(cq: types.CallbackQuery):
    if cq.data == 'translate_message':
        await cq.message.edit_text(
            translator.translate(cq.message.text)
        )
    await cq.answer(
        text='сообщение переведено.'
    )

if __name__ == '__main__':
    executor.start_polling(
        dispatcher=dp
    )
