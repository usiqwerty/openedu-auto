from abc import abstractmethod, ABC


class Question(ABC):
    type: str
    text: str

    @abstractmethod
    def query(self) -> str:
        """Generate prompt for LLM"""


