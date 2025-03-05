from abc import abstractmethod

from openedu.questions.choice import ChoiceQuestion
from openedu.questions.match import MatchQuestion


class AbstractSolver:
    @abstractmethod
    def solve(self, question: ChoiceQuestion | MatchQuestion) -> tuple[str, str | list[str]]:
        """

        :param question: question text
        :param options: answers
        :param ids: input tags IDs
        :return:
        """
        pass
