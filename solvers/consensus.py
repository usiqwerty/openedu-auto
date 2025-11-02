import logging

from errors import NoSolutionFoundError
from openedu.questions.choice import ChoiceQuestion
from openedu.questions.fill import FillQuestion
from openedu.questions.fixed_match import FixedMatchQuestion
from openedu.questions.freematch import FreeMatchQuestion
from openedu.questions.new_match import NewMatchQuestion
from openedu.questions.question import Question
from openedu.questions.select import SelectQuestion
from solvers.abstract_solver import AbstractSolver


class ConsensusSolver(AbstractSolver):
    def __init__(self, solvers: list[AbstractSolver]):
        self.solvers = solvers
        logging.info(f"Set up ConsensusSolver: {self.solvers}")

    def __solve_with_all_solvers(self, question: Question):
        solutions = [solver.solve(question) for solver in self.solvers]
        if all(s == solutions[0] for s in solutions):
            return solutions[0]
        logging.error(f"Consensus failed: {solutions}")
        raise NoSolutionFoundError(f"{question.id} {question.text}")

    def solve_choice(self, question: ChoiceQuestion) -> tuple[str, str | list[str]]:
        return self.__solve_with_all_solvers(question)

    def solve_match(self, question: FixedMatchQuestion) -> tuple[str, str | list[str]]:
        return self.__solve_with_all_solvers(question)

    def solve_freematch(self, question: FreeMatchQuestion) -> tuple[str, str | list[str]]:
        return self.__solve_with_all_solvers(question)

    def solve_select(self, question: SelectQuestion) -> tuple[str, str | list[str]]:
        return self.__solve_with_all_solvers(question)

    def solve_fill(self, question: FillQuestion) -> tuple[str, str | list[str]]:
        return self.__solve_with_all_solvers(question)

    def solve_new_match(self, question: NewMatchQuestion) -> tuple[str, str | list[str]]:
        return self.__solve_with_all_solvers(question)
