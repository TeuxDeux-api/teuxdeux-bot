import asyncio
import datetime
from aiogram import types

import bs4
import requests

from client.queries import db, get_all_tasks
from bot import dp


async def auto_auth(user_id: int):
    last_auth = db.hget(user_id, 'last_auth_time').decode()
    today = datetime.date.today()
    if not last_auth == today:
        username, password = db.hget(user_id, 'username').decode(), db.hget(
            user_id, 'password').decode()
        login_url = "https://teuxdeux.com/login"

        payload = {
            'username': username,
            'password': password,
        }

        # Use 'with' to ensure the session context is closed after use.
        with requests.Session() as s:
            r = s.get(login_url)
            signin = bs4.BeautifulSoup(r._content, 'html.parser')
            payload['csrf_token'] = signin.find(
                'input', type="hidden")["value"]
            p = s.post(login_url, data=payload,
                       headers=dict(Referer=login_url))
        return
    return


def get_current_tasks(user_id: int, time) -> list:
    todos = get_all_tasks(user_id)
    text = f"Ваши задачи на {time}:\n\n"

    sorted_by_time_todos = []

    for todo in todos["todos"]:
        if time in todo["current_date"]:
            sorted_by_time_todos.append(todo)
    return sorted_by_time_todos
