from abc import abstractmethod, ABC

from errors import NoSolutionFoundError
from src.openedu.questions.choice import ChoiceQuestion
from src.openedu.questions.crossword import Crossword
from src.openedu.questions.fill import FillQuestion
from src.openedu.questions.match.abstract_match import AbstractMatchQuestion
from src.openedu.questions.match.fixed_match import FixedMatchQuestion
from src.openedu.questions.match.freematch import FreeMatchQuestion
from src.openedu.questions.match.new_match import NewMatchQuestion
from src.openedu.questions.question import Question
from src.openedu.questions.select import SelectQuestion


class AbstractSolver(ABC):
    def solve(self, question: Question) -> tuple[str, str | list[str]]:
        if isinstance(question, ChoiceQuestion):
            return self.solve_choice(question)
        elif isinstance(question, FixedMatchQuestion):
            return self.solve_match(question)
        elif isinstance(question, FreeMatchQuestion):
            return self.solve_freematch(question)
        elif isinstance(question, SelectQuestion):
            return self.solve_select(question)
        elif isinstance(question, FillQuestion):
            return self.solve_fill(question)
        elif isinstance(question, NewMatchQuestion):
            return self.solve_new_match(question)
        elif isinstance(question, Crossword):
            return self.solve_crossword(question)
        raise NotImplementedError(f"Unsupported question type: {type(question)}")

    @abstractmethod
    def solve_choice(self, question: ChoiceQuestion) -> tuple[str, str | list[str]]:
        pass

    @abstractmethod
    def solve_unified_match(self, question: AbstractMatchQuestion) -> tuple[str, str | list[str]]:
        pass

    def solve_match(self, question: FixedMatchQuestion) -> tuple[str, str | list[str]]:
        return self.solve_unified_match(question)

    def solve_freematch(self, question: FreeMatchQuestion) -> tuple[str, str | list[str]]:
        return self.solve_unified_match(question)

    def solve_new_match(self, question: NewMatchQuestion) -> tuple[str, str | list[str]]:
        return self.solve_unified_match(question)

    @abstractmethod
    def solve_select(self, question: SelectQuestion) -> tuple[str, str | list[str]]:
        pass

    @abstractmethod
    def solve_fill(self, question: FillQuestion) -> tuple[str, str | list[str]]:
        pass

    def solve_crossword(self, question: Crossword):
        ans = []
        for item in question.questions:
            if item.answer is None:
                raise NoSolutionFoundError("Answers were not inserted into crossword data")
            ans.append((item.unique_position, item.answer))
        ans.sort(key=lambda x: x[0])

        return question.compose([answer for _, answer in ans])
