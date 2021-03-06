import sys
import datetime

import loguru
from aiogram import types
from aiogram.dispatcher.storage import FSMContext

from client.queries import (auth_user_query, db, delete_task, get_all_tasks, delete_task,
                            get_current_tasks, get_task_by_id, new_task, update_task)
from bot.buttons import main_btn, todo_menu, todo_sub_menu
from bot.states import States
from bot import utils


async def start_handler(message: types.Message, state: FSMContext):
    """
    This handler will be called when user sends `/start` command
    """

    if db.hexists(message.from_user.id, 'auth_token'):

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
        await utils.auto_auth(message.from_user.id)
        await States.my_tasks.set()
        today = str(datetime.date.today())
        text = "Ваши задачи на сегодня:\n\n"
        todos = get_all_tasks(message.from_user.id)

        todos_for_buttons = []

        for i, todo in enumerate(todos["todos"], 1):
            if today in todo["current_date"]:
                if todo["done"]:
                    text += f"{i}. <u>{todo['text']}</u>\n"
                else:
                    text += f"{i}. {todo['text']}\n"
                todos_for_buttons.append(todo)
        await message.answer(text, parse_mode="html", reply_markup=todo_menu(todos_for_buttons))


async def new_task_handler(message: types.Message, state: FSMContext):
    try:
        task = {
            "text": message.text,
            "current_date": str(datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d")),
            "done": False,
            "list_id": None
        }
        text = new_task(message.from_user.id, task)
        await message.answer(text[1])
        await state.finish()
        loguru.logger.success(text)
    except Exception as e:
        loguru.logger.error(str(sys.exc_info()))


buttons_date = datetime.date.today()


async def todo_callback_handler(query: types.CallbackQuery, state: FSMContext):
    global buttons_date

    try:
        if query.data == "next":
            buttons_date = buttons_date + datetime.timedelta(days=1)
            todos = utils.get_current_tasks(
                query.from_user.id, str(buttons_date))

            if not todos:
                await States.my_tasks.set()
                await query.answer(
                    f"Нет задач на {buttons_date}",
                    show_alert=True)
                buttons_date = buttons_date - datetime.timedelta(days=1)
                return

            text = f"Ваши задачи на {buttons_date}:\n\n"

            for i, todo in enumerate(todos, 1):
                if todo["done"]:
                    text += f"{i}. <u>{todo['text']}</u>\n"
                else:
                    text += f"{i}. {todo['text']}\n"
            await States.my_tasks.set()
            await query.message.edit_text(text, parse_mode="html", reply_markup=todo_menu(todos))
            return
        elif query.data == "prev":
            buttons_date = buttons_date - datetime.timedelta(days=1)
            todos = utils.get_current_tasks(
                query.from_user.id, str(buttons_date))
            if buttons_date == datetime.date.today():
                text = "Ваши задачи на сегодня:\n\n"
            else:
                text = f"Ваши задачи на {buttons_date}:\n\n"

            for i, todo in enumerate(todos, 1):
                if todo["done"]:
                    text += f"{i}. <u>{todo['text']}</u>\n"
                else:
                    text += f"{i}. {todo['text']}\n"
            await States.my_tasks.set()
            await query.message.edit_text(text, parse_mode="html", reply_markup=todo_menu(todos))
            return

        todo = get_task_by_id(query.from_user.id, query.data)["todo"]
        text = ""
        if todo["done"]:
            text += f"<ins>{todo['text']}</ins>"
        else:
            text += todo['text']
        await States.todo_submenu.set()
        await query.message.edit_text(text, parse_mode="HTML", reply_markup=todo_sub_menu(todo))

        buttons_date = datetime.date.today()

    except Exception as e:
        loguru.logger.error(e)


task_id = []


async def todo_submenu_callback_handler(query: types.CallbackQuery, state: FSMContext):
    try:
        id, type = query.data.split(" ")

        # Back to tasks menu
        text = "\n\n"
        todos = get_current_tasks(query.from_user.id)

        for i, todo in enumerate(todos, 1):
            if todo["done"]:
                text += f"{i}. <u>{todo['text']}</u>\n"
            else:
                text += f"{i}. {todo['text']}\n"
        button = todo_menu(todos)
        text_lines = text.splitlines()
        # end

        if type == "done":
            data = {
                "done": 1
            }
            update_task(query.from_user.id, id, data)
            await States.my_tasks.set()
            text_lines[0] += "<b>Task is done</b>"

            await query.message.edit_text('\n'.join(text_lines),
                                          parse_mode="HTML", reply_markup=button)
        elif type == "delete":
            delete_task(query.from_user.id, id)
            await States.my_tasks.set()
            text_lines[0] += "<b>Task deleted</b>"
            await query.message.edit_text('\n'.join(text_lines),
                                          parse_mode="HTML", reply_markup=button)
        elif type == "update":
            task_id.append(int(id))
            await States.update_task.set()
            await query.message.edit_text("Ok. Send me the new text")
        elif type == "postpone":
            data = {
                "current_date": str(datetime.date.today() + datetime.timedelta(days=1)),
                "position": 0
            }
            response = update_task(query.from_user.id, id, data)
            if 200 in response:
                await States.my_tasks.set()
                text_lines[0] += "<b>Task postponed to tomorrow</b>"
                await query.message.edit_text('\n'.join(text_lines),
                                              parse_mode="HTML", reply_markup=button)
            else:
                await state.finish()
                await query.message.edit_text(response)
    except Exception as e:
        loguru.logger.error(sys.exc_info())


async def task_update_handler(message: types.Message, state: FSMContext):
    try:
        data = {
            "text": message.text
        }
        print(update_task(message.from_user.id, task_id=task_id[0], opts=data))
        await state.finish()
        await message.answer("Ok", reply_markup=main_btn())
        task_id.clear()
    except Exception as e:
        loguru.logger.debug(e)
