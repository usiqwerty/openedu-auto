import re
from typing import Literal, Any

from pydantic import BaseModel, GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema


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
        r = re.search(r"(\w+)\+(\w+)\+(\w+)", rich_id)
        if not r:
            raise ValueError(f"Invalid course id: {rich_id}")
        org, course_id, run = r.groups()
        return CourseID(org, course_id, run)


class BlockID:
    course_id: CourseID
    block_id: str
    type: Literal['sequential', 'vertical', 'videoxblock', 'html', 'problem']

    def __init__(self,
                 course_id: CourseID,
                 block_id: str,
                 block_type: Literal['sequential', 'vertical', 'videoxblock', 'html', 'problem']):
        self.course_id = course_id
        self.block_id = block_id
        self.type = block_type

    def __str__(self):
        return f"block-v1:{self.course_id}+type@{self.type}+block@{self.block_id}"

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def parse(rich_id: str):
        r = re.search(r"block-v1:([\w+_]+)\+type@([\w-]+)\+block@([\w\W]+)", rich_id)
        if not r:
            raise ValueError(f"Invalid block id: {rich_id}")
        course_id, block_type, block_id = r.groups()
        course_id = CourseID.parse(course_id)
        if block_type == 'sequential':
            return SequentialBlockID(course_id, block_id, block_type)  # type: ignore[arg-type]
        elif block_type == 'vertical':
            return VerticalBlockID(course_id, block_id, block_type)  # type: ignore[arg-type]
        else:
            return BlockID(course_id, block_id, block_type)

    def __eq__(self, other):
        return str(self) == str(other)

    def __hash__(self):
        return hash(str(self))

    @classmethod
    def __get_pydantic_core_schema__(
            cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        from_str_schema = core_schema.chain_schema([
            core_schema.str_schema(),
            core_schema.no_info_after_validator_function(cls.parse, handler(str)),
        ])

        return core_schema.json_or_python_schema(
            json_schema=from_str_schema,
            python_schema=core_schema.union_schema([
                from_str_schema,
                core_schema.is_instance_schema(cls)
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(repr)
        )


class VerticalBlockID(BlockID):
    type = 'vertical'


class SequentialBlockID(BlockID):
    type = 'sequential'


class ProblemBlockID(BlockID):
    type = 'problem'
