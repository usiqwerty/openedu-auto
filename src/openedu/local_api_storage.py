import json
import logging
from typing import Any

from src import config
from src.openedu.course import Course, Chapter
from src.openedu.ids import BlockID, CourseID, VerticalBlockID
from src.openedu.oed_parser import VerticalBlock


class LocalApiStorage:
    vertical_blocks: dict[VerticalBlockID, VerticalBlock]
    courses: dict[CourseID, Course]
    solved: set[BlockID]
    skipped: list[BlockID]
    cache: dict[str, Any]

    def __init__(self):
        self.load_from_disk()

    def load_from_disk(self):
        try:
            # TODO: Why would we need to store vertical block data? We only need
            #  it's solution status, right?
            with open(config.blocks_fn, encoding='utf-8') as f:
                self.vertical_blocks = {k: VerticalBlock(**json.loads(v)) for k, v in json.load(f).items()}
        except FileNotFoundError:
            self.vertical_blocks = {}
        try:
            with open(config.courses_fn, encoding='utf-8') as f:
                json_data = json.load(f)
            self.courses = {}

            for c_id, c in json_data.items():
                course_id = CourseID.parse(c_id)
                course = json.loads(c)

                self.courses[course_id] = Course(id=course['id'], name=course['name'],
                                                 chapters=[Chapter(**x) for x in course['chapters']])
        except FileNotFoundError:
            self.courses = {}
        try:
            with open(config.solved_fn, encoding='utf-8') as f:
                self.solved = set(json.load(f))
        except FileNotFoundError:
            self.solved = set()
        try:
            with open(config.ignored_fn, encoding='utf-8') as f:
                self.skipped = json.load(f)
        except FileNotFoundError:
            self.skipped = []
        try:
            with open(config.cache_fn, encoding='utf-8') as f:
                self.cache = json.load(f)
        except FileNotFoundError:
            self.cache = {}

    def mark_block_as_completed(self, block_id: BlockID):
        if not config.config.get('restrict-actions'):
            self.solved.add(block_id)
            logging.info(f"Added to solved: {block_id}")

    def save(self):
        with open(config.blocks_fn, 'w', encoding='utf-8') as f:
            json.dump({str(k): v.json() for k, v in self.vertical_blocks.items()}, f)
        with open(config.courses_fn, 'w', encoding='utf-8') as f:
            json.dump({str(k): v.json() for k, v in self.courses.items()}, f)
        with open(config.solved_fn, 'w', encoding='utf-8') as f:
            json.dump([str(blkid) for blkid in self.solved], f)
        with open(config.ignored_fn, 'w', encoding='utf-8') as f:
            json.dump([str(blkid) for blkid in self.skipped], f)
        with open(config.cache_fn, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f)


class DummyApiStorage(LocalApiStorage):
    def load_from_disk(self):
        self.vertical_blocks = {}
        self.courses = {}
        self.solved = set()
        self.skipped = []
        self.cache = {}

    def mark_block_as_completed(self, block_id: BlockID):
        if not config.config.get('restrict-actions'):
            self.solved.add(block_id)
            logging.info(f"Added to solved (dummy): {block_id}")

    def save(self):
        pass
