from pydantic import BaseModel


class Chapter(BaseModel):
    name: str
    sequentials: list[str]


class Course(BaseModel):
    id: str
    name: str
    chapters: list[Chapter]
