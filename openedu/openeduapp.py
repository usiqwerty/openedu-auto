import json
import re
from typing import Any

import requests
import logging

from cached_requests import get
from config import get_cookies, blocks_fn, get_headers, config
from images.image_describer import ImageDescriber
from openedu.api import OpenEduAPI
from openedu.oed_parser import OpenEduParser, VerticalBlock
from openedu.questions.question import Question


class OpenEduApp:
    course_id: str
    blocks: dict[str, VerticalBlock]

    parser: OpenEduParser
    api: OpenEduAPI

    def __init__(self, describer: ImageDescriber):
        self.api = OpenEduAPI()
        self.parser = OpenEduParser(describer)

    def add_block_and_save(self, blk: VerticalBlock):
        self.blocks[blk.id] = blk
        logging.debug(f"Block added: {blk.id}")
        self.save_blocks()

    def save_blocks(self):
        with open(blocks_fn, 'w', encoding='utf-8') as f:
            json.dump({k: v.json() for k, v in self.blocks.items()}, f)
        logging.debug("Blocks saved")

    def parse_and_save_sequential_block(self, course_id: str, block_id: str):
        r = self.api.get_sequential_block(course_id, block_id)
        for blk in self.parser.parse_sequential_block_(r):
            self.add_block_and_save(blk)

    def iterate_incomplete_blocks(self):
        for blk_id, block in self.blocks.items():
            if not block.complete:
                yield blk_id, block

    def get_problems(self, blk: str) -> list[list[Question]]:
        logging.debug("Requesting xblock")
        url = f"https://courses.openedu.ru/xblock/{blk}"
        r = get(url, headers=get_headers(), cookies=get_cookies(self.api.csrf), is_json=False)
        return self.parser.parse_vertical_block_html(r)

    def extract_quest_id(self, qfield: str) -> str:
        r = re.search(r"input_([\w\d]+)_\d+_\d+", qfield)
        return r.group(1)
