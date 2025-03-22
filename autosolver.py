import logging
import traceback

from cached_requests import CacheContext
from errors import WrongAnswer, UnsupportedProblemType
from images.image_describer import ImageDescriber
from openedu.openeduapp import OpenEduApp, extract_quest_id
from openedu.questions.freematch import FreeMatchQuestion
from openedu.questions.question import Question
from openedu.utils import parse_page_url
from openedu_processor import OpenEduProcessor
from solvers.abstract_solver import AbstractSolver


class OpenEduAutoSolver(OpenEduProcessor):
    solver: AbstractSolver
    describer: ImageDescriber
    app: OpenEduApp
    cache_context: CacheContext

    require_incomplete = True

    def process_problem(self, course_id: str, problem: list[Question]):
        answers = {}
        input_id = None
        for question in problem:
            if isinstance(question, FreeMatchQuestion):
                raise UnsupportedProblemType("freematch")
            try:
                input_id, input_value = self.solver.solve(question)
                answers[input_id] = input_value
            except KeyError as e:
                print("Error:", e)
                traceback.print_exc()
                exit(1)
        if input_id is None:
            return
        quest_id = extract_quest_id(input_id)
        new_block_id = f"block-v1:{course_id}+type@problem+block@{quest_id}"
        if self.app.is_block_solved(new_block_id):
            return
        print(f"{answers=}")

        got, total = self.app.api.problem_check(course_id, new_block_id, answers)
        logging.info(f"Solved ({got}/{total})")
        self.app.api.api_storage.mark_block_as_completed(new_block_id)
        if got < total:
            raise WrongAnswer(quest_id, answers)

    def solve_by_url(self, url: str):
        course_id, seq, ver = parse_page_url(url)
        logging.debug(f"Course: {course_id}")
        logging.debug(f"Starting at block {seq}")

        with self.cache_context:
            self.app.api.auth.refresh()
            for vert in self.app.get_sequential_block(course_id, seq.block_id):
                print(vert)
                self.process_vertical(vert.id, vert, course_id)
