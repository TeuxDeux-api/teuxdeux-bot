from aiogram.dispatcher.filters.state import State, StatesGroup


class States(StatesGroup):

    # Auth menu
    auth_menu = State()

    # Main states
    new_task = State()
    my_tasks = State()

    # ToDo menu
    todo_submenu = State()
    update_task = State()
