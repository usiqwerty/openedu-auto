import logging
from abc import abstractmethod

from bs4 import BeautifulSoup

from cache import CacheContext
from errors import UnsupportedProblemType, NoSolutionFoundError
from images.image_describer import ImageDescriber
from openedu.ids import SequentialBlockID, BlockID
from openedu.oed_parser import VerticalBlock
from openedu.openeduapp import OpenEduApp
from openedu.questions.question import Question

from solvers.abstract_solver import AbstractSolver


class OpenEduProcessor:
    require_incomplete: bool

    def __init__(self, solver: AbstractSolver, describer: ImageDescriber):
        self.solver = solver
        self.cache_context = CacheContext([lambda: self.app.api.auth.save(), lambda: self.app.api.api_storage.save()])
        self.describer = describer
        self.app = OpenEduApp(self.describer)

    def is_block_solved(self, block_id: str):
        return self.require_incomplete and self.app.is_block_solved(block_id)

    def process_course(self, course_id: str):
        with self.cache_context:
            course = self.app.get_course_info(course_id)
            self.app.api.auth.refresh()
            for ch in course.chapters:
                print(f"Chapter: {ch.name}")
                for seq in ch.sequentials:
                    seq_id = SequentialBlockID.parse(seq)

                    if self.is_block_solved(seq_id.block_id):
                        continue

                    for vertical in self.app.get_sequential_block(course_id, seq_id.block_id):
                        print(vertical.title)
                        blk = self.app.get_vertical_block(vertical.id)
                        if self.is_block_solved(blk.id) and not blk.complete:
                            continue
                        self.process_vertical(blk.id, vertical, course_id)

                    self.app.api.api_storage.mark_block_as_completed(seq_id.block_id)

    def process_vertical(self, blkid: str, block: VerticalBlock, course_id: str):
        logging.debug(blkid)
        logging.debug(f"Block '{block.title}' (complete={block.complete}) of type '{block.type}'")

        r = self.app.api.get_vertical_html(blkid)
        soup = BeautifulSoup(r, 'html.parser')
        if not self.is_block_solved(blkid):
            for xblock_vert in soup.select("div.xblock div.vert"):
                block_id_str = xblock_vert['data-id']

                rich_block_id = BlockID.parse(block_id_str)
                if rich_block_id.type in {"html", "xvideoblock"}:
                    self.app.api.publish_completion(course_id, block_id_str)
        # if block.type == 'other' and not block.graded:
        #     # return
        #     # print(blkid, block)
        #     # api.tick_page(blkid)
        #     # time.sleep(5)
        #
        #     app.api.publish_completion(course_id, block_id_str)
            if 1 or block.type == "problem" or (block.type == 'other' and block.graded):
                try:
                    for problem in self.app.get_problems_for_vertical(blkid):
                        self.process_problem(course_id, problem)
                except UnsupportedProblemType as e:
                    logging.error(f"Unsupported problem type: {e}")
                    self.app.skip_forever(blkid)
                except NoSolutionFoundError as e:
                    logging.error(f"No solution found: {e}")
                    return # do not mark as complete, so we can come back later
        self.app.api.api_storage.mark_block_as_completed(blkid)

    @abstractmethod
    def process_problem(self, course_id: str, problem: list[Question]):
        pass
