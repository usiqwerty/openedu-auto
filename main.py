import logging

from automation.autosolver import OpenEduAutoSolver
from errors import Unauthorized, GenericOpenEduError, ReloginReceived
from log import setup_logging
from ui.menu import menu_iteration, require_login

version_string = "openedu-auto v1.1"
setup_logging()
logging.debug(version_string)


def main():
    print(version_string)
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
