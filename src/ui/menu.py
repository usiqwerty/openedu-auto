import os

from src import config
from src.auth_providers.urfu import login_urfu
from src.automation.autosolver import OpenEduAutoSolver
from errors import Unauthorized
from src.solvers.mistral_solver import MistralSolver
from tests.fakes import DummyDescriber
from src.ui.actions import solve_with_llm, solve_with_file, save_answers
from src.ui.cli_tools import parse_only_presudosolve
from src.ui.solver_utils import pick_solver_from_config


def menu_iteration(app: OpenEduAutoSolver):
    print("1. Решить через нейросеть")
    print("2. Решить из файла")
    print("3. Сохранить решение в файл")
    print("4. Сбросить куки")
    print("5. Сбросить кеш")
    print("6. По ссылке")
    cmd = input("Ввод: ")
    if cmd == "1":
        solve_with_llm(app)
        return True
    elif cmd == '2':
        solve_with_file(app)
        return True
    elif cmd == '3':
        save_answers(app)
        return True
    elif cmd == '4':
        with app.cache_context:
            app.app.logout()
        print("Перезапустите программу")
    elif cmd == '5':
        if os.path.exists(config.cache_fn):
            os.remove(config.cache_fn)
        print("Перезапустите программу")
    elif cmd == '6':
        solver = pick_solver_from_config()
        describer = DummyDescriber()
        app = OpenEduAutoSolver(solver, describer)
        url = input("Ссылка: ")
        app.solve_by_url(url)
        return True
    elif cmd == '-1':
        solver = MistralSolver()
        describer = DummyDescriber()
        parse_only_presudosolve(solver, describer)
    elif cmd == '-2':
        solve_with_llm(app, go_on=True)
        return True

def choose_login_method():
    method = None
    while method is None:
        print("Выберите метод авторизации")
        print("1. Парооль Openedu")
        print("2. Парооль Urfu")
        m = input("Выбор: ")
        if m in {"1", "2"}:
            method = int(m)

    return ["openedu", "urfu"][method-1]


def require_login(empty_app: OpenEduAutoSolver):
    if not empty_app.app.has_login_data:
        login_method = choose_login_method()
        print("Нужно ввести данные формы, чтобы авторизоваться")
        username = input("Имя пользователя: ").strip()
        password = input("Пароль: ").strip()

        if login_method == "openedu":
            status = empty_app.app.login(username, password)
        elif login_method == "urfu":
            login_urfu(empty_app.app._api.session, username, password)
            status = empty_app.app._api.status()

        if status.get("auth"):
            empty_app.app.save()
        else:
            raise Unauthorized("Could not log in")
