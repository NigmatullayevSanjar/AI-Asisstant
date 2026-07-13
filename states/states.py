from aiogram.fsm.state import State, StatesGroup


class CreateUser(StatesGroup):
    tg_id = State()
    full_name = State()
    team = State()


class CreateTeam(StatesGroup):
    name = State()


class CreateTask(StatesGroup):
    title = State()
    description = State()
    deadline = State()
    assignee = State()


class AssignTask(StatesGroup):
    task_id = State()
    user_id = State()


class EditTask(StatesGroup):
    task_id = State()
    field = State()
    value = State()


class DeleteTask(StatesGroup):
    task_id = State()
