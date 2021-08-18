import datetime

from aiogram import types
from aiogram.types.reply_keyboard import ReplyKeyboardMarkup

# from client.models import NewTask


def main_btn() -> ReplyKeyboardMarkup:
    """Main button"""
    buttons = ["➕ New task",
               "My Tasks"]

    menu = types.ReplyKeyboardMarkup(
        resize_keyboard=True, row_width=2, one_time_keyboard=True)
    menu.add(*buttons)
    return menu


def todo_menu(todos: dict, tomorrow=True) -> types.InlineKeyboardMarkup:
    """Todo menu"""
    menu = types.InlineKeyboardMarkup(row_width=4)
    buttons = []
    for i, todo in enumerate(todos, 1):
        buttons.append(types.InlineKeyboardButton(
            i, callback_data=todo["id"]))
    menu.add(*buttons)
    today = str(datetime.date.today())
    if not todos[0]["current_date"] == today:
        menu.row(types.InlineKeyboardButton("« Prev.", callback_data="prev"),
                 types.InlineKeyboardButton("Next »", callback_data="next"))
        return menu
    if tomorrow:
        menu.add(types.InlineKeyboardButton("Next »", callback_data="next"))
    else:
        menu.add(types.InlineKeyboardButton("« Prev.", callback_data="prev"))

    return menu


def todo_sub_menu(todo: dict) -> types.InlineKeyboardMarkup:
    """Article menu"""
    menu = types.InlineKeyboardMarkup(row_width=2)
    texts = ["✅ Done", "🔄 Update", "📅 Postpone", "🗑 Delete"]
    buttons = []
    for text in texts:
        buttons.append(types.InlineKeyboardButton(
            text, callback_data=f"{todo['id']} {text[2:].lower()}"))
    menu.add(*buttons)

    return menu


def back_btn() -> types.ReplyKeyboardMarkup:
    return types.ReplyKeyboardMarkup(resize_keyboard=True).add("⬅️ Back")
