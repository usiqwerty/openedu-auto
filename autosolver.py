import logging
import re
import time
import traceback
import urllib

from cached_requests import CacheContext
from images.image_describer import ImageDescriber
from openedu.oed_parser import VerticalBlock
from openedu.openeduapp import OpenEduApp
from openedu.questions.question import Question
from openedu.utils import parse_page_url
from solvers.abstract_solver import AbstractSolver


class OpenEduAutoSolver:
    solver: AbstractSolver
    describer: ImageDescriber

    def __init__(self, solver: AbstractSolver, describer: ImageDescriber):
        self.solver = solver
        self.describer = describer

    def solve_course(self, url: str):
        course_id, seq, ver = parse_page_url(url)

        logging.debug(f"Course: {course_id}")
        logging.debug(f"Starting at block {seq}")
        url = (f"https://courses.openedu.ru/api/courseware/sequence/"
               f"block-v1:{course_id}+type@sequential"
               f"+block@{seq.block_id}")

        with CacheContext():
            app = OpenEduApp(course_id, self.describer)
            app.parse_and_save_sequential_block(url)

            for blkid, block in app.iterate_incomplete_blocks():
                self.solve_block(app, blkid, block, course_id)

    def solve_block(self, api: OpenEduApp, blkid: str, block: VerticalBlock, course_id: str):
        logging.debug(blkid)
        logging.debug(f"Block '{block.title}' (complete={block.complete}) of type '{block.type}'")
        if block.type == 'other':
            return
            # print(blkid, block)
            # api.tick_page(blkid)
            # time.sleep(5)
            # api.publish_completion(blkid)
        elif block.type == "problem":
            for problem in api.get_problems(blkid):
                self.solve_problem(api, course_id, problem)
            return

    def solve_problem(self, api: OpenEduApp, course_id: str, problem: list[Question]):
        answers = {}
        for question in problem:
            # print(question.query())
            try:
                input_id, input_value = self.solver.solve(question)
                answers[input_id] = input_value
            except KeyError as e:
                print("Error:", e)
                traceback.print_exc()
                exit(1)
        quest_id = api.extract_quest_id(input_id)
        print(f"{answers=}")
        new_block_id = f"block-v1:{course_id}+type@problem+block@{quest_id}"
        got, total = api.problem_check(new_block_id, answers)
        logging.info(f"Solved ({got}/{total})")
        if got < total:
            logging.critical("Wrong answer!")
            exit(1)
