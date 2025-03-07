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


class OpenEdu(OpenEduAPI, OpenEduParser):
    course_id: str
    blocks: dict[str, VerticalBlock]

    def __init__(self, course_id: str, describer: ImageDescriber):
        super().__init__(course_id)
        self.describer = describer
        if self.csrf is None:
            self.get_csrf()

    def add_block_and_save(self, blk: VerticalBlock):
        self.blocks[blk.id] = blk
        logging.debug(f"Block added: {blk.id}")
        self.save_blocks()

    def save_blocks(self):
        with open(blocks_fn, 'w', encoding='utf-8') as f:
            json.dump({k: v.json() for k, v in self.blocks.items()}, f)
        logging.debug("Blocks saved")

    def parse_and_save_sequential_block(self, url: str):
        logging.debug(f"Parsing {url}")
        r = get(url, self.csrf or "")
        for blk in self.parse_sequential_block_(r):
            self.add_block_and_save(blk)

    def iterate_incomplete_blocks(self):
        for blk_id, block in self.blocks.items():
            if not block.complete:
                yield blk_id, block

    def get_problems(self, blk: str) -> list[list[Question]]:
        logging.debug("Requesting xblock")
        url = f"https://courses.openedu.ru/xblock/{blk}"
        r = get(url, headers=get_headers(), cookies=get_cookies(self.csrf), is_json=False)
        return self.parse_vertical_block_html(r)

    def get_csrf(self) -> str:
        logging.debug('Requesting csrf token')
        r = requests.get('https://courses.openedu.ru/csrf/api/v1/token',
                         headers=get_headers(),
                         cookies=get_cookies(self.csrf))
        self.csrf = r.json()['csrfToken']
        config.config['csrf'] = self.csrf
        self.save_config(config.config)

        return self.csrf

    def extract_quest_id(self, qfield: str) -> str:
        r = re.search(r"input_([\w\d]+)_\d+_\d+", qfield)
        return r.group(1)

    def save_config(self, cfg: dict[str, Any]):
        with open(config.config_fn, 'w', encoding='utf-8') as f:
            json.dump(cfg, f)
        logging.debug("Config saved")
