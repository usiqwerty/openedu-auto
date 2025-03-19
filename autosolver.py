import logging
import traceback

from cached_requests import CacheContext
from errors import WrongAnswer, UnsupportedProblemType
from images.image_describer import ImageDescriber
from openedu.ids import SequentialBlockID
from openedu.oed_parser import VerticalBlock
from openedu.openeduapp import OpenEduApp, extract_quest_id
from openedu.questions.freematch import FreeMatchQuestion
from openedu.questions.question import Question
from openedu.utils import parse_page_url
from solvers.abstract_solver import AbstractSolver


class OpenEduAutoSolver:
    solver: AbstractSolver
    describer: ImageDescriber
    app: OpenEduApp
    cache_context: CacheContext

    def __init__(self, solver: AbstractSolver, describer: ImageDescriber):
        self.solver = solver
        self.describer = describer
        self.app = OpenEduApp(self.describer)
        self.cache_context = CacheContext([lambda: self.app.api.auth.save(), lambda: self.app.api.api_storage.save()])

    def solve_by_url(self, url: str):
        course_id, seq, ver = parse_page_url(url)
        logging.debug(f"Course: {course_id}")
        logging.debug(f"Starting at block {seq}")

        with self.cache_context:
            self.app.api.auth.refresh()
            # self.app.api.get("https://courses.openedu.ru/csrf/api/v1/token") #update token
            for vert in self.app.get_sequential_block(course_id, seq.block_id):
                print(vert)
                self.solve_vertical(self.app, vert.id, vert, course_id)

            # for blkid, block in self.app.incomplete_blocks():
            #     self.solve_block(self.app, blkid, block, course_id)

    def solve_course(self, course_id: str):
        with self.cache_context:
            course = self.app.get_course_info(course_id)
            self.app.api.auth.refresh()
            for ch in course.chapters:
                for seq in ch.sequentials:
                    seq_id = SequentialBlockID.parse(seq)

                    if self.app.is_block_solved(seq_id.block_id):
                        continue

                    for vertical in self.app.get_sequential_block(course_id, seq_id.block_id):
                        blk = self.app.get_vertical_block(vertical.id)
                        if self.app.is_block_solved(blk.id):
                            continue
                        if blk and not blk.complete:
                            self.solve_vertical(self.app, blk.id, vertical, course_id)
                        else:
                            logging.info("Requested block was already completed")
                    self.app.api.api_storage.mark_block_as_completed(seq_id.block_id)

    def solve_vertical(self, app: OpenEduApp, blkid: str, block: VerticalBlock, course_id: str):
        logging.debug(blkid)
        logging.debug(f"Block '{block.title}' (complete={block.complete}) of type '{block.type}'")
        if block.type == 'other':
            # return
            # print(blkid, block)
            # api.tick_page(blkid)
            # time.sleep(5)
            app.api.publish_completion(course_id, blkid)
        elif block.type == "problem":
            try:
                for problem in app.get_problems_for_vertical(blkid):
                    self.solve_problem(app, course_id, problem)
            except UnsupportedProblemType as e:
                logging.error(f"Unsupported problem type: {e}")
                self.app.skip_forever(blkid)
        self.app.api.api_storage.mark_block_as_completed(blkid)

    def solve_problem(self, app: OpenEduApp, course_id: str, problem: list[Question]):
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
        if app.is_block_solved(quest_id):
            return

        print(f"{answers=}")
        new_block_id = f"block-v1:{course_id}+type@problem+block@{quest_id}"
        got, total = app.api.problem_check(course_id, new_block_id, answers)
        logging.info(f"Solved ({got}/{total})")
        self.app.api.api_storage.mark_block_as_completed(quest_id)
        if got < total:
            raise WrongAnswer
