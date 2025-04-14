import json
import re

import logging

from config import ignored_fn
from images.image_describer import ImageDescriber
from openedu.api import OpenEduAPI
from openedu.ids import CourseID
from openedu.oed_parser import OpenEduParser, VerticalBlock
from openedu.questions.question import Question


def extract_quest_id(qfield: str) -> str:
    r = re.search(r"input_([\w\d]+)_\d+_\d+", qfield)
    return r.group(1)


class OpenEduApp:
    parser: OpenEduParser
    api: OpenEduAPI

    def __init__(self, describer: ImageDescriber):
        self.api = OpenEduAPI()
        self.parser = OpenEduParser(describer)

    def save_block(self, blk: VerticalBlock):
        self.api.api_storage.blocks[blk.id] = blk
        logging.debug(f"Block added: {blk.id}")

    def get_sequential_block(self, course_id: str, block_id: str):
        r = self.api.get_sequential_block(course_id, block_id)
        for blk in self.parser.parse_sequential_block_(r):
            self.save_block(blk)
            yield blk

    def is_block_solved(self, block_id: str) -> bool:
        block = self.api.api_storage.blocks.get(block_id)
        if block is None:
            complete_in_blocks = False
        else:
            complete_in_blocks = block.complete
        return block_id in self.api.api_storage.solved or complete_in_blocks

    def get_problems_for_vertical(self, blk: str) -> list[list[Question]]:
        r = self.api.get_vertical_html(blk)
        return self.parser.parse_vertical_block_html(r)

    def login(self, username: str, password: str):
        self.api.auth.login(username, password)
        return self.api.status()

    def get_course_info(self, course_id: CourseID):
        if course_id not in self.api.api_storage.courses:
            self.api.auth.refresh()
            course = self.api.course_info(course_id)
            self.api.api_storage.courses[str(course_id)] = course
        return self.api.api_storage.courses[str(course_id)]

    def get_vertical_block(self, block_id: str) -> VerticalBlock:
        return self.api.api_storage.blocks.get(block_id)

    def skip_forever(self, block_id):
        try:
            with open(ignored_fn, encoding='utf-8') as f:
                skipped = json.load(f)
        except FileNotFoundError:
            skipped = []
        skipped.append(block_id)

        with open(ignored_fn, 'w', encoding='utf-8') as f:
            json.dump(skipped, f)
