import asyncio
from datetime import timedelta, datetime
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from aiogram import Bot, Dispatcher, executor
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from logging import basicConfig, getLogger, INFO
from dotenv import load_dotenv
from os import environ

from models import Base, User
from utils import update_user_tracking_info
from keyboards import menu

# logger
basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=INFO)
logger = getLogger(__name__)

# db initialisation
engine = create_engine('sqlite:///sqlite.db', echo=True, future=True)
Base.metadata.create_all(engine)

# tg bot initialisation
load_dotenv()
bot = Bot(environ.get('BOT_TOKEN'), parse_mode='HTML')
dp = Dispatcher(bot, storage=MemoryStorage())


@dp.message_handler(state='*', commands=['cancel'])
@dp.message_handler(lambda message: message.text.lower() == 'cancel', state='*')
async def cancel_handler(message: Message, state: FSMContext, raw_state: str | None = None):
    """Allow user to cancel any action"""

    if raw_state is None:
        return

    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    await message.reply('Canceled.', reply_markup=ReplyKeyboardRemove())


@dp.message_handler(Command('menu'))
async def send_menu(message: Message):
    """Menu, shows all bot functionality"""

    logger.info(f'sent menu to {message.from_user.username}')

    await message.answer("Please choose an action", reply_markup=menu)


def test_sql_db_update():
    start = (datetime.today() - timedelta(days=120))
    end = datetime.today()
    with Session(engine) as session:
        # Make if enry is already in db -> skip that
        user = User(name='testuser')
        session.add(user)
        session.commit()
        user = session.query(User).get(1)
        update_user_tracking_info(session, start, end, user)


def main():
    pass


if __name__ == '__main__':
    # main()
    executor.start_polling(dp)
