import sys
import json
from datetime import datetime
from aiogram.types import base

import bs4
import dotenv
import loguru
import requests
import pickle
from vedis import Vedis

db = Vedis("db", open_database=True)

dotenv.load_dotenv()


def _headers(user_id: int):
    try:
        if not user_id:
            raise None
        auth_token = db.hget(user_id, 'auth_token').decode()
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        return headers
    except Exception as e:
        loguru.logger.debug(str(e))


def _make_request(method_name, method='get', params=None, data=None, custom_url=None):
    if params:
        if "user_id" not in params:
            raise Exception("Not found user_id in params")
        user_id = params["user_id"]
        if not db.hexists(user_id, 'auth_token'):
            raise Exception("Not found workspace in vedis")
        workspace = db.hget(user_id, 'workspace').decode()
        headers = _headers(user_id)
    if not custom_url:
        base_url = f"https://teuxdeux.com/api/v3/workspaces/{workspace}/{method_name}"
    else:
        base_url = custom_url

    if method == 'post':
        if not data:
            raise Exception("Data not found for method post")
        r = requests.post(
            base_url, data=json.dumps(data), headers=headers)
        if r.status_code == 200:
            response = [r.status_code, "Task saved"]

        elif "errors" in r.json():
            response = [r.status_code, r.json()["errors"][0]["message"]]
        return response
    elif method == 'patch':
        if not data:
            raise Exception("Data not found for method patch")
        r = requests.post(
            base_url, data=data, headers=headers)
        if r.status_code == 200:
            response = [r.status_code, "Task updated"]

        elif "errors" in r.json():
            response = [r.status_code, r.json()["errors"][0]["message"]]
        return response
    elif method == 'delete':
        r = requests.delete(base_url, headers=headers)
        return r.status_code

    result = requests.get(base_url, headers=headers)

    if not result.status_code == 200:
        raise Exception(result.text)
    return result.json()


# def __init__(user_id: int) -> None:
    try:
        user_id = user_id

        if db.hexists(user_id, 'workspace') and db.hexists(user_id, 'auth_token'):
            workspace = db.hget(user_id, 'workspace').decode()
            auth_token = db.hget(user_id, 'auth_token').decode()
            headers = {
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json"
            }
            exists = True
        else:
            exists = False

    except Exception as e:
        loguru.logger.debug(str(e))


def new_task(user_id: int, task: dict) -> list[str]:

    params = {"user_id": user_id}

    r = _make_request(method_name='todos', method='post',
                      data=task, params=params, custom_url=None)

    return r
    """{text: "Hello Mir", current_date: "2021-07-24", done: false, list_id: null}"""


def update_task(user_id: int, task_id: int, opts: dict):
    try:
        if "done" in opts:
            method_url = f"/todos/{task_id}/state"
            method = 'post'
        else:
            method_url = f"/todos/{task_id}"
            method = 'patch'
        params = {"user_id": user_id}

        r = _make_request(method_name=method_url, method=method,
                          data=json.dumps(opts), params=params)

        loguru.logger.success(str(r))
        return r
    except Exception as e:
        loguru.logger.error(str(e))


def get_all_tasks(user_id: int) -> dict:
    try:
        params = {"user_id": user_id}

        workspace = db.hget(user_id, 'workspace').decode()

        custom_path = f"https://teuxdeux.com/api/v3/workspaces/{workspace}/todos"

        r = _make_request(method_name=None, method='get',
                          params=params, custom_url=custom_path)

        return r
    except Exception as e:
        loguru.logger.error(str(sys.exc_info()))


def get_current_tasks(user_id: int) -> list[dict]:
    """Get current day tasks on todo list
    TODO: Add a selection of the day
    URL examples: https://teuxdeux.com/api/v3/workspaces/36456786?since=2021-7-27&until=2021-08-10"""
    try:
        today = str(datetime.strftime(datetime.now(), "%Y-%m-%d"))
        params = {"user_id": user_id}

        workspace = db.hget(user_id, 'workspace').decode()

        custom_path = f"https://teuxdeux.com/api/v3/workspaces/{workspace}?since={today}"

        r = _make_request(
            method_name=None, method='get', params=params, custom_url=custom_path)

        return r["calendar_todos"]
    except Exception as e:
        loguru.logger.error(str(e))


def get_task_by_id(user_id: int, task_id: int) -> dict:
    try:
        params = {"user_id": user_id}

        r = _make_request(method_name=f'todos/{task_id}', method='get',
                          params=params)

        return r
    except Exception as e:
        loguru.logger.error(str(e))


def delete_task(user_id: int, task_id: int):
    try:
        params = {"user_id": user_id}

        r = _make_request(method_name=f'todos/{task_id}', method='delete',
                          params=params)

        loguru.logger.success(str(r))
    except Exception as e:
        loguru.logger.error(str(e))


def auth_user_query(user_id: int, username: str, password: str):
    try:
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

        # User's data list
        db.begin()
        # Get auth token from session cookies
        auth_token = s.cookies.get_dict()["_txdxtxdx_token"]
        # Save user auth token to db
        db.hsetnx(user_id, 'auth_token', auth_token)
        # Parser the workspace id
        pwid = bs4.BeautifulSoup(p._content, 'html.parser')
        # Find the script from html response by id
        el = pwid.find(
            'script', id="js__bootstrap-workspaces")
        # Decode json objects to dict
        json_object = json.loads(el.contents[0])
        # Save the worcspace id from json_object
        db.hsetnx(user_id, 'workspace', json_object[0]["id"])
        db.commit()

        # Print to console the success status code
        loguru.logger.success(str(p.status_code))
    except Exception as e:
        loguru.logger.error(str(e))
