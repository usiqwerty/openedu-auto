import logging

from automation.ans_saver import AnswersSaver
from automation.autosolver import OpenEduAutoSolver
from config import set_config
from images.openrouter.qwen_describer import QwenImageDescriber
from solvers.consensus import ConsensusSolver
from solvers.localsolver import LocalSolver
from solvers.openai_solver import GenericOpenAISolver
from tests.fakes import DummyDescriber
from ui.cli_tools import get_course_id, solve, get_solution_filepath


def solve_with_llm(empty_app: OpenEduAutoSolver):
    try:
        course_id = get_course_id(empty_app)
    except ValueError:
        print("Не удалось распознать ссылку")
        return
    course = empty_app.app.get_course_info(course_id)
    set_config("last-course", str(course_id))

    solver = ConsensusSolver([
        GenericOpenAISolver(),
        GenericOpenAISolver(model='gpt-4.1-nano'),
        GenericOpenAISolver(model='gemini-2.5-flash'),
        GenericOpenAISolver(model='qwen3-235b-a22b-2507'),
    ])
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
