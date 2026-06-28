from bs4 import Tag

from errors import UnsupportedProblemType
from src.openedu.questions.question import Question


class UnsupportedQuestion(Question):
    type: str = 'unsupported'
    id: str

    def query(self) -> str:
        raise UnsupportedProblemType

    def compose(self, answer) -> tuple[str, str | dict]:
        raise TypeError("Can't solve unsupported question")

    @staticmethod
    def parse(tag: Tag, prepend_lines: list[str] | None = None) -> "Question":
        raise UnsupportedProblemType
