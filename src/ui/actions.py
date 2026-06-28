import logging

from src.automation.ans_saver import AnswersSaver
from src.automation.autosolver import OpenEduAutoSolver
from src.config import set_config
from src.images.openrouter.qwen_describer import QwenImageDescriber
from src.solvers.localsolver import LocalSolver
from tests.fakes import DummyDescriber
from src.ui.cli_tools import get_course_id, solve, get_solution_filepath
from src.ui.solver_utils import pick_solver_from_config


def solve_with_llm(empty_app: OpenEduAutoSolver, go_on=False):
    try:
        course_id = get_course_id(empty_app)
    except ValueError:
        print("Не удалось распознать ссылку")
        return
    course = empty_app.app.get_course_info(course_id)
    set_config("last-course", str(course_id))

    solver = pick_solver_from_config()

    describer = QwenImageDescriber()
    solve(solver, describer, course, go_on=go_on)


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
    saver.pull_answers(course_id)
