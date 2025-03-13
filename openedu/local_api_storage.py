import json
import logging

import config
from openedu.course import Course, Chapter
from openedu.oed_parser import VerticalBlock


class LocalApiStorage:
    blocks: dict[str, VerticalBlock]
    courses: dict[str, Course]
    solved: set[str]

    def __init__(self, blocks: dict | None = None):

        if blocks is None:
            try:
                with open(config.blocks_fn, encoding='utf-8') as f:
                    self.blocks = {k: VerticalBlock(**json.loads(v)) for k, v in json.load(f).items()}
            except FileNotFoundError:
                self.blocks = {}
            try:
                with open(config.courses_fn, encoding='utf-8') as f:
                    json_data=json.load(f)
                self.courses = {}

                for c_id, c in json_data.items():
                    course = json.loads(c)

                    self.courses[c_id] = Course(id=course['id'], name=course['name'],
                                                chapters=[Chapter(**x) for x in course['chapters']])
            except FileNotFoundError:
                self.courses = {}
            try:
                with open(config.solved_fn, encoding='utf-8') as f:
                    self.solved = set(json.load(f))
            except FileNotFoundError:
                self.solved = set()
        else:
            self.blocks = blocks

    # TODO: what the hell
    #  duplicate method
    def is_block_complete(self, block_id: str):
        return self.blocks[block_id].complete

    def mark_block_as_completed(self, block_id: str):
        if not config.config.get('restrict-actions'):
            if block_id in self.blocks:
                self.blocks[block_id].complete = True
                logging.info("Block completed")
            else:
                logging.warning("block that we are checking is not saved, this should not have happened")
            self.solved.add(block_id)
            logging.info(f"Added to solved: {block_id}")

    def save(self):
        with open(config.blocks_fn, 'w', encoding='utf-8') as f:
            json.dump({k: v.json() for k, v in self.blocks.items()}, f)
        with open(config.courses_fn, 'w', encoding='utf-8') as f:
            json.dump({k: v.json() for k, v in self.courses.items()}, f)
        with open(config.solved_fn, 'w', encoding='utf-8') as f:
            json.dump(list(self.solved), f)
