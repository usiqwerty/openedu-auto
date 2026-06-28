from pydantic import BaseModel

from src.openedu.ids import CourseID, SequentialBlockID


class Chapter(BaseModel):
    name: str
    sequentials: list[SequentialBlockID]


class Course(BaseModel):
    id: CourseID
    name: str
    chapters: list[Chapter]
