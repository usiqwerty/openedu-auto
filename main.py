import logging
import os

import config
from automation.autosolver import OpenEduAutoSolver
from ui.actions import solve_with_llm, solve_with_file, save_answers
from errors import Unauthorized, GenericOpenEduError, ReloginReceived
from solvers.mistral_solver import MistralSolver
from tests.fakes import DummyDescriber

logging.getLogger().setLevel(logging.DEBUG)


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
        solver = MistralSolver()
        describer = DummyDescriber()
        app = OpenEduAutoSolver(solver, describer)
        url = input("Ссылка: ")
        app.solve_by_url(url)
        return True


def require_login(empty_app: OpenEduAutoSolver):
    if not empty_app.app.has_login_data:
        print("Нужно ввести данные формы, чтобы авторизоваться")
        username = input("Имя пользователя: ").strip()
        password = input("Пароль: ").strip()
        status = empty_app.app.login(username, password)
        if status.get("auth"):
            empty_app.app.save()
        else:
            raise Unauthorized("Could not log in")


def main():
    app = OpenEduAutoSolver(None, None)
    try:
        require_login(app)
    except Unauthorized:
        print("Не удалось войти")
        exit(1)
    while True:
        try:
            if menu_iteration(app):
                continue
        except GenericOpenEduError as e:
            print(e)
            return
        except Unauthorized as e:
            print(e)
            return
        except ReloginReceived:
            print("Сервер сбросил авторизацию")
            with app.cache_context:
                app.app.logout()
            print("Введите пароль заново")
            return
        break


if __name__ == "__main__":
    main()
