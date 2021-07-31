import sys
from datetime import datetime

import loguru
from aiogram import types
from aiogram.dispatcher.storage import FSMContext
from aiogram.types import reply_keyboard, update
from client.queries import (auth_user_query, db, delete_task, get_all_tasks, delete_task,
                            get_current_tasks, new_task, update_task)

from bot.buttons import main_btn, todo_menu, todo_sub_menu
from bot.states import States


async def start_handler(message: types.Message, state: FSMContext):
    """
    This handler will be called when user sends `/start` command
    """

    if db.llen(message.from_user.id) > 0:

        await state.finish()
        await message.answer("Hello", reply_markup=main_btn())
    else:
        await message.answer("Welcome to <b>TeuxDeux</b> bot!\nSend me your email and password from teuxdeux.com for authorization.\nFor example:\nfoo@gmail.com Qwerty1234", parse_mode="html")
        await States.auth_menu.set()


async def authenticate_user(message: types.Message, state: FSMContext):
    """
    Authenticate the user by email and password from teuxdeux.com
    """
    try:
        username, password = message.text.split(" ")

        auth_user_query(message.from_user.id, username, password)
        await message.answer("Ok", reply_markup=main_btn())
        await state.finish()
    except Exception as e:
        loguru.logger.debug(e)


async def text_handler(message: types.Message):
    """Text message handler"""

    if message.text == "➕ New task":
        await States.new_task.set()
        await message.answer("Ok send me a task text")
    elif message.text == "My Tasks":
        await States.my_tasks.set()
        text = "Ваши задачи на сегодня:\n\n"
        todos = get_current_tasks(message.from_user.id)

        for i, todo in enumerate(todos, 1):
            if todo["done"]:
                text += f"{i}. <u>{todo['text']}</u>\n"
            else:
                text += f"{i}. {todo['text']}\n"
        await message.answer(text, parse_mode="html", reply_markup=todo_menu(todos))


async def new_task_handler(message: types.Message, state: FSMContext):
    try:
        task = {
            "text": message.text,
            "current_date": str(datetime.strftime(datetime.now(), "%Y-%m-%d")),
            "done": False,
            "list_id": None
        }
        text = new_task(message.from_user.id, task)
        await message.answer(text[1])
        await state.finish()
        loguru.logger.success(text)
    except Exception as e:
        loguru.logger.error(str(sys.exc_info()))


async def todo_callback_handler(query: types.CallbackQuery, state: FSMContext):
    try:
        todos = get_all_tasks(query.from_user.id)
        text = ""
        for i, todo in enumerate(todos["todos"], 1):
            if str(query.data) in str(todo["id"]):
                if todo["done"]:
                    text += f"<ins>{todo['text']}</ins>"
                else:
                    text += todo['text']
                button = todo_sub_menu(todo)
        await States.todo_submenu.set()
        await query.message.edit_text(text, parse_mode="HTML", reply_markup=button)

    except Exception as e:
        loguru.logger.error(e)


async def todo_submenu_callback_handler(query: types.CallbackQuery, state: FSMContext):
    try:
        id, type = query.data.split(" ")
        if type == "done":
            data = {
                "done": 1
            }
            update_task(int(id), data)
            await state.finish()
            await query.message.edit_text("Task is done")
        elif type == "delete":
            delete_task(query.from_user.id, int(id))
            await state.finish()
            await query.message.edit_text("Task deleted")
        elif type == "update":
            pass

    except Exception as e:
        loguru.logger.error(e)
