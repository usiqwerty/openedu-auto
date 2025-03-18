from abc import abstractmethod, ABC


class Question(ABC):
    type: str
    text: str

    @abstractmethod
    def query(self) -> str:
        """Generate prompt for LLM"""


    @abstractmethod
    def compose(self, answer) -> tuple[str, str | dict]:
        """Compose respose payload"""
