from abc import abstractmethod, ABC
from typing import Any

from bs4 import Tag


class Question(ABC):
    type: str
    text: str
    id: str

    correct_answer: Any | None = None

    @abstractmethod
    def query(self) -> str:
        """Generate prompt for LLM"""

    @abstractmethod
    def compose(self, answer) -> tuple[str, str | dict]:
        """Compose respose payload"""

    @staticmethod
    @abstractmethod
    def parse(tag: Tag, prepend_lines: list[str] = None) -> "Question":
        """Parse question from HTML"""
