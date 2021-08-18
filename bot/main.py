import time

import dotenv
from aiogram.dispatcher import storage
from aiogram.utils import executor

from bot.utils import auto_auth
from bot.logger import logger_init
from .handlers import authenticate_user, new_task_handler, start_handler, task_update_handler, text_handler, todo_callback_handler, todo_submenu_callback_handler
from client.queries import db
from bot.states import States
from . import bot, dp


# Configure logging.
# 4-levels for logging: INFO, DEBUG, WARNING, ERROR
logger_init("INFO")


async def main():
    """Main function"""

    # Initialize bot and dispatcher
    try:

        # start_handler register
        dp.register_message_handler(
            start_handler, commands={"start"}, state="*")
        # Authentication menu register
        dp.register_message_handler(
            authenticate_user, state=States.auth_menu
        )
        # text_handler register
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
        # task's text update handler
        dp.register_message_handler(
            task_update_handler, state=States.update_task)

        await dp.start_polling()
    finally:
        db.close()
        await storage.close()
        await bot.close()
