from typing import Any

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
