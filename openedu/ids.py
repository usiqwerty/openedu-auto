import re
from typing import Literal

from pydantic import BaseModel


class CourseID(BaseModel):
    org: str
    course_id: str
    run: str
    def __init__(self, org: str, course_id: str, run: str):
        super().__init__(org=org, course_id=course_id, run=run)
        self.org = org
        self.course_id = course_id
        self.run = run

    def __repr__(self):
        return f"{self.org}+{self.course_id}+{self.run}"

    def __str__(self):
        return repr(self)

    def __hash__(self):
        return hash(repr(self))

    def same_course(self, other: "CourseID"):
        """Check both coures are same except, maybe, course run"""
        return self.org == other.org and self.course_id == other.course_id

    @staticmethod
    def parse(rich_id: str):
        org, course_id, run = re.search(r"(\w+)\+(\w+)\+(\w+)", rich_id).groups()
        return CourseID(org, course_id, run)

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
        course_id, block_type, block_id = re.search(r"block-v1:([\w+_]+)\+type@([\w-]+)\+block@([\w\W]+)",
                                                    rich_id).groups()
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
