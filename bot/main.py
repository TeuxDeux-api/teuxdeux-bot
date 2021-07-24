import pathlib

from aiogram.dispatcher import storage
from bot.states import States
import os

import dotenv
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.files import PickleStorage

from bot.logger import logger_init
from .handlers import new_task_handler, start_handler, text_handler, todo_callback_handler, todo_submenu_callback_handler

# Load dotenv
dotenv.load_dotenv()

# Configure logging.
# 4-levels for logging: INFO, DEBUG, WARNING, ERROR
logger_init("INFO")


async def main():
    """Main function"""

    # Initialize bot and dispatcher
    bot = Bot(token=os.getenv("API_TOKEN"))
    try:
        dp = Dispatcher(bot, storage=PickleStorage("db"))
        # start_handler register
        dp.register_message_handler(
            start_handler, commands={"start"}, state="*")
        # # text_handler register
        dp.register_message_handler(
            text_handler, content_types="text")
        # register new_task_handler
        dp.register_message_handler(
            new_task_handler, state=States.new_task)
        # todo menu inline buttons handler
        dp.register_callback_query_handler(
            todo_callback_handler, state=States.my_tasks)
        # todo submenu callback handler
        dp.register_callback_query_handler(
            todo_submenu_callback_handler, state=States.todo_submenu)
        await dp.start_polling()
    finally:
        await bot.close()
