import asyncio
from datetime import datetime
from aiogram.types import reply_keyboard, update

import loguru
from aiogram import types
from aiogram.dispatcher.storage import FSMContext

from client.queries import delete_task, get_all_tasks, new_task, update_task
from bot.buttons import main_btn, todo_menu, todo_sub_menu
from bot.states import States


async def start_handler(message: types.Message):
    """
    This handler will be called when user sends `/start` command
    """
    await message.answer("Hi!", reply_markup=main_btn())


async def text_handler(message: types.Message):
    """Text message handler"""

    if message.text == "➕ New task":
        await States.new_task.set()
        await message.answer("Ok send me a task text")
    elif message.text == "My Tasks":
        await States.my_tasks.set()
        text = "Ваши задачи на сегодня:\n\n"
        todos = get_all_tasks()
        for i, todo in enumerate(todos["todos"], 1):
            if todo["done"]:
                text += f"{i}. <u>{todo['text']}</u>\n"
            else:
                text += f"{i}. {todo['text']}\n"
        await message.answer(text, parse_mode="html", reply_markup=todo_menu(todos["todos"]))


async def new_task_handler(message: types.Message):
    task = {
        "text": message.text,
        "current_date": str(datetime.strftime(datetime.now(), "%Y-%m-%d")),
        "done": False,
        "list_id": None
    }
    new_task(task)

    await message.answer("Task saved")


async def todo_callback_handler(query: types.CallbackQuery, state: FSMContext):
    try:
        todos = get_all_tasks()
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
        print()
        id, type = query.data.split(" ")
        if type == "done":
            data = {
                "done": 1
            }
            update_task(int(id), data)
            await States.my_tasks.set()
            await query.message.edit_text("Task is done")
        elif type == "delete":
            delete_task(int(id))
            await States.my_tasks.set()
            await query.message.edit_text("Task deleted")
        elif type == "update":
            pass

    except Exception as e:
        loguru.logger.error(e)
