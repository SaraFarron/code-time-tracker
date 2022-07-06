import asyncio
from datetime import timedelta, datetime
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from aiogram import Bot, Dispatcher, executor
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from logging import basicConfig, getLogger, INFO
from dotenv import load_dotenv
from os import environ

from keyboards import menu
from models import Base, User
from utils import (
    update_user_tracking_info, stats_message,
    update_user_credentials,
)

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

description = 'TODO'


class UpdateWakatimeKey(StatesGroup):
    send_key = State()
    check_key = State()


@dp.message_handler(Command('menu'))
async def send_menu(message: Message):
    logger.info(f'sent menu to {message.from_user.username}')
    await message.answer("Please choose an action", reply_markup=menu)


@dp.message_handler(Command('help'))
async def send_help(message: Message):
    logger.info(f'sent help to {message.from_user.username}')
    await message.answer(description)


@dp.message_handler(Command('start'))
async def create_new_user(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    with Session(engine) as session:
        user = User(
            telegram_id=user_id,
            name=username,
        )
        session.add(user)
        session.commit()

    logger.info('new user registered ' + username)
    await message.answer('TODO message with greetings')


@dp.callback_query_handler(text=['retrieve_all', 'last_week'])
async def show_tracking_stats(call: CallbackQuery):
    match call.data:
        case 'retrieve_all':
            logger.info('sent all stats to ' + call.from_user.username)
            text = stats_message(call.from_user.id, engine, 'Last 30 Days')
            if len(text) > 4096:
                await call.message.answer(text[:4096])
                await call.message.answer(text[4096:])
            else:
                await call.message.answer(text)
        case 'last_week':
            logger.info('sent last stats to ' + call.from_user.username)
            await call.message.answer(stats_message(call.from_user.id, engine, 'Last 7 Days'))
        case _: await call.answer()


@dp.callback_query_handler(text=['update_key'])
async def update_key(call: CallbackQuery):
    logger.info(call.from_user.username + ' updates api key')
    await UpdateWakatimeKey.send_key.set()
    await call.message.answer('Send me your new Wakatime key')
    await UpdateWakatimeKey.next()


@dp.message_handler(state=UpdateWakatimeKey.check_key)
async def update_result(message: Message, state: FSMContext):
    user_api_key = message.text
    await message.answer(
        update_user_credentials(user_api_key, message.from_user.id, engine)
    )
    await state.finish()


def main():
    pass


if __name__ == '__main__':
    # main()
    executor.start_polling(dp)
