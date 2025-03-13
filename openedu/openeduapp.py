import json
import re
from typing import Any

import requests
import logging

from cached_requests import get
from config import get_cookies, blocks_fn, get_headers, courses_fn, ignored_fn
from images.image_describer import ImageDescriber
from openedu.api import OpenEduAPI
from openedu.oed_parser import OpenEduParser, VerticalBlock
from openedu.questions.question import Question


class OpenEduApp:
    parser: OpenEduParser
    api: OpenEduAPI

    def __init__(self, describer: ImageDescriber):
        self.api = OpenEduAPI()
        self.parser = OpenEduParser(describer)

    def add_block_and_save(self, blk: VerticalBlock):
        self.api.api_storage.blocks[blk.id] = blk
        logging.debug(f"Block added: {blk.id}")
        self.save_blocks()

    def save_blocks(self):
        with open(blocks_fn, 'w', encoding='utf-8') as f:
            json.dump({k: v.json() for k, v in self.api.api_storage.blocks.items()}, f)
        logging.debug("Blocks saved")

    def parse_sequential_block(self, course_id: str, block_id: str):
        r = self.api.get_sequential_block(course_id, block_id)
        for blk in self.parser.parse_sequential_block_(r):
            self.add_block_and_save(blk)
            yield blk

    def is_block_solved(self, block_id: str) -> bool:
        return block_id in self.api.api_storage.solved

    def parse_and_save_sequential_block(self, course_id: str, block_id: str):
        for blk in self.parse_sequential_block(course_id, block_id):
            self.add_block_and_save(blk)

    def iterate_incomplete_blocks(self):
        for blk_id, block in self.api.api_storage.blocks.items():
            if not block.complete:
                yield blk_id, block

    def get_problems(self, blk: str) -> list[list[Question]]:
        logging.debug("Requesting xblock")
        url = f"https://courses.openedu.ru/xblock/{blk}"
        r = self.api.get(url, is_json=False)
        return self.parser.parse_vertical_block_html(r)

    def extract_quest_id(self, qfield: str) -> str:
        r = re.search(r"input_([\w\d]+)_\d+_\d+", qfield)
        return r.group(1)

    def login(self, username: str, password: str):
        self.api.auth.login(username, password)

    def get_course_info(self, course_id: str):
        if course_id not in self.api.api_storage.courses:
            course = self.api.course_info(course_id)
            self.api.api_storage.courses[course_id] = course
        return self.api.api_storage.courses[course_id]

    def skip_forever(self, block_id):
        try:
            with open(ignored_fn, encoding='utf-8') as f:
                skipped = json.load(f)
        except FileNotFoundError:
            skipped = []
        skipped.append(block_id)

        with open(ignored_fn, 'w', encoding='utf-8') as f:
            json.dump(skipped, f)
