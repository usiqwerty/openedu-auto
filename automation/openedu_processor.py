import logging
from abc import abstractmethod, ABC

from bs4 import BeautifulSoup

from cache import CacheContext
from errors import UnsupportedProblemType, NoSolutionFoundError
from images.image_describer import ImageDescriber
from openedu.ids import SequentialBlockID, BlockID
from openedu.oed_parser import VerticalBlock
from openedu.openedu import OpenEdu
from openedu.questions.question import Question

from solvers.abstract_solver import AbstractSolver


class OpenEduProcessor(ABC):
    """Abstract automated OpenEdu processor"""
    mark_completion: bool = True
    require_incomplete: bool
    solver: AbstractSolver
    describer: ImageDescriber
    app: OpenEdu
    cache_context: CacheContext

    def __init__(self, solver: AbstractSolver, describer: ImageDescriber):
        self.solver = solver
        self.cache_context = CacheContext([lambda: self.app.save()])
        self.describer = describer
        self.app = OpenEdu(self.describer)

    def should_process(self, block_id: str):
        return not (self.require_incomplete and self.app.is_block_solved(block_id))

    def process_course(self, course_id: str):
        with self.cache_context:
            course = self.app.get_course_info(course_id)
            for ch in course.chapters:
                print(f"Chapter: {ch.name}")
                for seq in ch.sequentials:
                    seq_id = SequentialBlockID.parse(seq)

                    if not self.should_process(seq_id.block_id):
                        continue

                    for vertical in self.app.get_sequential_block(course_id, seq_id.block_id):
                        print(vertical.title)
                        blk = self.app.get_vertical_block(vertical.id)
                        # TODO: too many places where completion might be marked
                        #  should be only should_process()
                        if (not self.should_process(blk.id)) and not blk.complete:
                            continue
                        self.process_vertical(blk.id, vertical, course_id)
                    if self.mark_completion:
                        self.app.mark_block_as_completed(seq_id.block_id)

    def process_vertical(self, blkid: str, block: VerticalBlock, course_id: str):
        logging.debug(blkid)
        logging.debug(f"Block '{block.title}' (complete={block.complete}) of type '{block.type}'")
        r = self.app.get_vertical_page_html(blkid)
        soup = BeautifulSoup(r, 'html.parser')
        if self.should_process(blkid):
            for xblock_vert in soup.select("div.xblock div.vert"):
                block_id_str = xblock_vert['data-id']

                rich_block_id = BlockID.parse(block_id_str)
                if rich_block_id.type in {"html", "xvideoblock"} and self.mark_completion:
                    self.app.publish_completion(course_id, block_id_str)
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
        if self.mark_completion:
            self.app.mark_block_as_completed(blkid)

    @abstractmethod
    def process_problem(self, course_id: str, problem: list[Question]):
        pass
