import logging
import os

import config
from ans_saver import AnswersSaver
from autosolver import OpenEduAutoSolver
from cli_tools import get_course_id, solve, get_solution_filepath
from config import set_config
from errors import Unauthorized
from images.openrouter.qwen_describer import QwenImageDescriber
from solvers.localsolver import LocalSolver
from solvers.mistral_solver import MistralSolver
from solvers.openrouter.gemini_solver import GeminiSolver
from tests.fakes import DummyDescriber

logging.getLogger().setLevel(logging.DEBUG)


def solve_with_llm(empty_app: OpenEduAutoSolver):
    try:
        course_id = get_course_id(empty_app)
    except ValueError:
        print("Не удалось распознать ссылку")
        return
    course = empty_app.app.get_course_info(course_id)
    set_config("last-course", str(course_id))

    solver = GeminiSolver()
    describer = QwenImageDescriber()
    solve(solver, describer, course)


def solve_with_file(empty_app: OpenEduAutoSolver):
    try:
        course_id = get_course_id(empty_app)
    except ValueError:
        print("Не удалось распознать ссылку")
        return
    course = empty_app.app.get_course_info(course_id)
    set_config("last-course", str(course_id))

    filepath = get_solution_filepath(course_id)
    logging.debug(f"Solution file: {filepath}")
    if filepath is None:
        print("Не удалось найти файл с решением для этого курса")
        return

    solver = LocalSolver(filepath)
    describer = DummyDescriber()
    solve(solver, describer, course)


def save_answers(empty_app: OpenEduAutoSolver):
    try:
        course_id = get_course_id(empty_app)
    except ValueError:
        print("Не удалось распознать ссылку")
        return

    saver = AnswersSaver()
    saver.pull_answers(str(course_id))


def main():
    empty_app = OpenEduAutoSolver(None, None)
    try:
        require_login(empty_app)
    except Unauthorized:
        print("Не удалось войти")
        exit(1)
    while True:
        print("1. Решить через нейросеть")
        print("2. Решить из файла")
        print("3. Сохранить решение в файл")
        print("4. Сбросить куки")
        print("5. Сбросить кеш")
        print("6. По ссылке")
        cmd = input("Ввод: ")
        if cmd == "1":
            solve_with_llm(empty_app)
            continue
        elif cmd == '2':
            solve_with_file(empty_app)
            continue
        elif cmd == '3':
            save_answers(empty_app)
            continue
        elif cmd == '4':
            with empty_app.cache_context:
                empty_app.app.api.auth.drop()
        elif cmd == '5':
            if os.path.exists(config.cache_fn):
                os.remove(config.cache_fn)
        elif cmd == '6':
            solver = MistralSolver()
            describer = DummyDescriber()
            app = OpenEduAutoSolver(solver, describer)
            url = input("Ссылка: ")
            app.solve_by_url(url)
        else:
            continue
        break


def require_login(empty_app: OpenEduAutoSolver):
    if not empty_app.app.api.session.cookies:
        print("Нужно ввести данные формы, чтобы авторизоваться")
        username = input("Имя пользователя: ").strip()
        password = input("Пароль: ").strip()
        status = empty_app.app.login(username, password)
        if status.get("auth"):
            empty_app.app.api.auth.save()
        else:
            raise Unauthorized("Could not log in")


if __name__ == "__main__":
    main()
