import re
from typing import Literal


class BlockID:
    course_id: str
    block_id: str
    type: Literal['sequential', 'vertical', 'videoxblock', 'html', 'problem']

    def __init__(self, course_id: str, block_id: str, block_type: Literal['sequential', 'vertical']):
        self.course_id = course_id
        self.block_id = block_id
        self.type = block_type

    def __str__(self):
        return f"block-v1:{self.course_id}+type@{self.type}+block@{self.block_id}"

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def parse(rich_id: str):
        course_id, block_type, block_id = re.search(r"block-v1:([\w+_]+)\+type@(\w+)\+block@([\w\W]+)", rich_id).groups()
        if block_type == 'sequential':
            return SequentialBlockID(course_id, block_id, block_type)
        elif block_type == 'vertical':
            return VerticalBlockID(course_id, block_id, block_type)
        else:
            return BlockID(course_id, block_id, block_type)


class VerticalBlockID(BlockID):
    type = 'vertical'


class SequentialBlockID(BlockID):
    type = 'sequential'
