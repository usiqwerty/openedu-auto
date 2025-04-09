from typing import Any

from bs4 import Tag
from pydantic import BaseModel

from errors import UnsupportedProblemType
from openedu.questions.question import Question


class UnsupportedQuestion(BaseModel, Question):
    type: str = 'unsupported'
    id: str

    def query(self) -> str:
        raise UnsupportedProblemType

    def compose(self, answer) -> tuple[str, str | dict]:
        return self.id, self.answer

    @staticmethod
    def parse(tag: Tag, prepend_lines: list[str] = None) -> "Question":
        raise UnsupportedProblemType
