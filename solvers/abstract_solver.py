from abc import abstractmethod, ABC

from openedu.questions.choice import ChoiceQuestion
from openedu.questions.freematch import FreeMatchQuestion
from openedu.questions.match import MatchQuestion


class AbstractSolver(ABC):
    def solve(self, question: ChoiceQuestion | MatchQuestion | FreeMatchQuestion) -> tuple[str, str | list[str]]:
        """

        :param question: question text
        :param options: answers
        :param ids: input tags IDs
        :return:
        """
        if isinstance(question, ChoiceQuestion):
            return self.solve_choice(question)
        elif isinstance(question, MatchQuestion):
            return self.solve_match(question)
        elif isinstance(question, FreeMatchQuestion):
            return self.solve_freematch(question)

    @abstractmethod
    def solve_choice(self, question: ChoiceQuestion):
        pass

    @abstractmethod
    def solve_match(self, question: MatchQuestion):
        pass

    @abstractmethod
    def solve_freematch(self, question: FreeMatchQuestion):
        pass
