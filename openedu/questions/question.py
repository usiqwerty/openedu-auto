from abc import abstractmethod, ABC
from typing import Any


class Question(ABC):
    type: str
    text: str

    correct_answer: Any | None = None

    @abstractmethod
    def query(self) -> str:
        """Generate prompt for LLM"""

    @abstractmethod
    def compose(self, answer) -> tuple[str, str | dict]:
        """Compose respose payload"""
