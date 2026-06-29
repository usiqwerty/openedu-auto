import logging
from abc import abstractmethod, ABC

from bs4 import BeautifulSoup

from src.cache import CacheContext
from errors import UnsupportedProblemType, NoSolutionFoundError
from src.images.image_describer import ImageDescriber
from src.openedu.ids import BlockID, CourseID, VerticalBlockID
from src.openedu.oed_parser import VerticalBlock
from src.openedu.openedu import OpenEdu
from src.openedu.questions.question import Question
from src.solvers.abstract_solver import AbstractSolver


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

    def should_process(self, block_id: BlockID) -> bool:
        return not (self.require_incomplete and self.app.is_block_solved(block_id))

    def process_course(self, course_id: CourseID):
        with self.cache_context:
            course = self.app.get_course_info(course_id)
            for ch in course.chapters:
                print(f"Chapter: {ch.name}")
                for seq_id in ch.sequentials:
                    print("Sequential:", seq_id.block_id)
                    if not self.should_process(seq_id):
                        continue

                    for vertical in self.app.get_sequential_block(course_id, seq_id):
                        print("Vertical:", vertical.title)
                        if self.should_process(vertical.id):
                            self.process_vertical(vertical.id, vertical, course_id)
                    if self.mark_completion:
                        self.app.mark_block_as_completed(seq_id)

    def process_vertical(self, blkid: VerticalBlockID, block: VerticalBlock, course_id: CourseID, *,
                         process_solved=False):
        logging.debug(blkid)
        logging.debug(f"Block '{block.title}' (complete={block.complete}) of type '{block.type}'")
        html = self.app.get_vertical_page_html(blkid)
        soup = BeautifulSoup(html, 'html.parser')
        for xblock_vert in soup.select("div.xblock div.vert"):
            block_id_str = xblock_vert['data-id']
            block_id = BlockID.parse(block_id_str)

            # гении консистентности
            if block_id.type in {"html", "xvideoblock", "videoxblock"} and self.mark_completion:
                self.app.publish_completion(course_id, block_id)

        try:
            for problem in self.app.get_problems_for_vertical(blkid):
                self.process_problem(course_id, problem, process_solved=process_solved)
        except UnsupportedProblemType as e:
            logging.error(f"Unsupported problem type: {e}")
            self.app.skip_forever(blkid)
        except NoSolutionFoundError as e:
            logging.error(f"No solution found: {e}")
            return  # do not mark as complete, so we can come back later
        if self.mark_completion:
            self.app.mark_block_as_completed(blkid)

    @abstractmethod
    def process_problem(self, course_id: CourseID, problem: list[Question], *, process_solved):
        pass
