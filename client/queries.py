import json
import os
import loguru

import requests
import dotenv


dotenv.load_dotenv()

headers = {
    "Authorization": f"Bearer {os.getenv('AUTH_TOKEN')}",
    "Content-Type": "application/json"
}


def new_task(task: dict) -> list[str]:

    r = requests.post(
        "https://teuxdeux.com/api/v3/workspaces/584007/todos", data=json.dumps(task),
        headers=headers)

    print(r.json())
    if r.status_code == 200:
        response = [r.status_code, "Task saved"]

    elif "errors" in r.json():
        response = [r.status_code, r.json()["errors"][0]["message"]]

    return response
    """{text: "Hello Mir", current_date: "2021-07-24", done: false, list_id: null}"""


def update_task(task_id: int, opts: dict):
    try:
        if "done" in opts:
            r = requests.post(f"https://teuxdeux.com/api/v3/workspaces/584007/todos/{task_id}/state", data=json.dumps(opts),
                              headers=headers)
        else:
            r = requests.patch(f"https://teuxdeux.com/api/v3/workspaces/584007/todos/{task_id}", data=json.dumps(opts),
                               headers=headers)
        loguru.logger.success(str(r.status_code))
    except Exception as e:
        loguru.logger.error(str(e))


def get_all_tasks() -> dict:
    try:
        r = requests.get(
            "https://teuxdeux.com/api/v3/workspaces/584007/todos", headers=headers)
        loguru.logger.success(str(r.status_code))
        return r.json()
    except Exception as e:
        loguru.logger.error(str(e))


def delete_task(task_id: int) -> dict:
    try:
        r = requests.delete(
            f"https://teuxdeux.com/api/v3/workspaces/584007/todos/{task_id}", headers=headers)
        loguru.logger.success(str(r.status_code))
    except Exception as e:
        loguru.logger.error(str(e))
