from abc import abstractmethod, ABC
from typing import Any

from bs4 import Tag
from pydantic import BaseModel


class Question(BaseModel, ABC):
    type: str
    text: str
    id: str

    correct_answer: Any | None = None

    @abstractmethod
    def query(self) -> str:
        """Generate prompt for LLM"""

    @abstractmethod
    def compose(self, answer) -> tuple[str, str | list | dict]:
        """Compose respose payload"""

    @staticmethod
    @abstractmethod
    def parse(tag: Tag, prepend_lines: list[str] | None = None) -> "Question":
        """Parse question from HTML"""
