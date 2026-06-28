import logging

from images.image_describer import ImageDescriber
from openedu.api import OpenEduAPI
from openedu.ids import CourseID, BlockID, VerticalBlockID, ProblemBlockID
from openedu.local_api_storage import LocalApiStorage
from openedu.oed_parser import OpenEduParser, VerticalBlock
from openedu.questions.question import Question


class OpenEdu:
    """OpenEdu service"""
    parser: OpenEduParser
    _api: OpenEduAPI
    storage: LocalApiStorage

    def __init__(self, describer: ImageDescriber):
        self.storage = LocalApiStorage()
        self._api = OpenEduAPI(self.storage)
        self.parser = OpenEduParser(describer)

    @property
    def has_login_data(self):
        return len(self._api.session.cookies) > 0

    def get_sequential_block(self, course_id: CourseID, block_id: str):
        r = self._api.get_sequential_block(course_id, block_id)
        for blk in self.parser.parse_sequential_block_(r):
            if blk.id not in self.storage.blocks:
                self.storage.blocks[blk.id] = blk
                logging.debug(f"Block added: {blk.id}")
            yield blk

    def is_block_solved(self, block_id: ProblemBlockID | VerticalBlockID) -> bool:
        if block_id.type == "problem":
            return block_id in self.storage.solved
        else:
            # TODO: maybe we should separate solved problems from solved verticals
            #  if it's not necessary, then simplify all this stuff.
            #  Like, why would we need to store vertical block data? We only need
            #  it's solution status, right?
            if block_id in self.storage.solved:
                return True
            block = self.storage.blocks.get(block_id)
            if block is None:
                return False
            else:
                return block.complete

    def get_problems_for_vertical(self, blk: VerticalBlockID) -> list[list[Question]]:
        r = self._api.get_vertical_html(blk)
        return self.parser.parse_vertical_block_html(r)

    def login(self, username: str, password: str):
        self._api.auth.login(username, password)
        return self._api.status()

    def get_course_info(self, course_id: CourseID):
        if course_id not in self.storage.courses:
            course = self._api.course_info(course_id)
            self.storage.courses[course_id] = course
        return self.storage.courses[course_id]

    def get_vertical_block(self, block_id: VerticalBlockID) -> VerticalBlock | None:
        return self.storage.blocks.get(block_id)

    def skip_forever(self, block_id):
        self.storage.skipped.append(block_id)
        self.storage.save()

    def mark_block_as_completed(self, block_id: ProblemBlockID | VerticalBlockID):
        self.storage.mark_block_as_completed(block_id)

    def save(self):
        self._api.auth.save()
        self.storage.save()

    def logout(self):
        """Erase local auth data"""
        self._api.auth.drop()

    def get_vertical_page_html(self, blk: VerticalBlockID):
        return self._api.get_vertical_html(blk)

    def publish_completion(self, course_id: CourseID, block_id: BlockID):
        """Tell OpenEdu that you have visited the page"""
        self._api.publish_completion(course_id, block_id)

    def submit_answers(self, course_id: CourseID, blk: ProblemBlockID, answers: dict[str, str | list[str]]):
        return self._api.problem_check(course_id, blk, answers)

    def inject_csrf(self, csrftoken: str):
        """Set `csrftoken` cookie"""
        self._api.session.cookies['csrftoken'] = csrftoken
