import json
import logging
from collections import defaultdict
from typing import Literal

from errors import NoSolutionFoundError
from openedu.questions.choice import ChoiceQuestion
from openedu.questions.fill import FillQuestion
from openedu.questions.fixed_match import FixedMatchQuestion
from openedu.questions.freematch import FreeMatchQuestion
from openedu.questions.new_match import NewMatchQuestion
from openedu.questions.question import Question
from openedu.questions.select import SelectQuestion
from solvers.abstract_solver import AbstractSolver


def get_most_common_solution(solutions: list[tuple[str, list[str]]]) -> tuple[str, str | list[str]]:
    ans_variatns = []
    n_solvers = len(solutions)

    for taskid, ans_list in solutions:
        ans_variatns.append(ans_list)

    taskid = solutions[0][0]

    counts = defaultdict(int)
    for variant in ans_variatns:
        for opt in variant:
            counts[opt] += 1

    most_common_variants = []
    for option, count in counts.items():
        if count >= n_solvers - 1:  # all except one
            most_common_variants.append(option)

    return taskid, most_common_variants


def merge_tables(solutions: list):
    ans_keys = None

    summed_table = defaultdict(lambda: defaultdict(int))
    task_id = None
    for tid, ans in solutions:
        task_id = tid
        ans_dict: dict = json.loads(ans)['answer']
        print("ans_dict", ans_dict)
        if not ans_dict:
            continue  # TODO: maybe we should do this in other place
        # json error may occur here
        if ans_keys is None:
            ans_keys = sorted(ans_dict.keys())
        elif len(ans_keys) != len(ans_dict):
            raise NoSolutionFoundError("Consensus failed: solutions have different number of keys")

        for key in ans_keys:
            summed_table[key][json.dumps(ans_dict[key])] += 1

    final = {}
    for key in ans_keys:
        answers_distribution = summed_table[key]
        for cell_val, count in answers_distribution.items():
            if count >= len(solutions) - 1:  # all except one
                final[key] = json.loads(cell_val)

    assert task_id is not None
    return task_id, json.dumps({"answer": final}, sort_keys=True)


class ConsensusSolver(AbstractSolver):
    def __init__(self, solvers: list[AbstractSolver], negotiation: Literal["match", "most-common"] = "match"):
        self.solvers = solvers
        self.negotiation = negotiation
        logging.info(f"Set up ConsensusSolver: {self.solvers}")

    def __solve_with_all_solvers(self, question: Question, table_mode=False):
        solutions = []
        for solver in self.solvers:
            try:
                solutions.append(solver.solve(question))
            except NoSolutionFoundError as e:
                logging.error(e)
        print("All solutions retrieved")
        if not solutions:
            raise NoSolutionFoundError("None of solvers has found a solution")
        # has_atomic = any(isinstance(s[1], str) for s in solutions)
        if self.negotiation == 'match':
            if all(s == solutions[0] for s in solutions):
                return solutions[0]
        elif self.negotiation == 'most-common':
            if table_mode:
                return merge_tables(solutions)
            sols_as_lists = []
            for id, ans in solutions:
                if isinstance(ans, list):
                    sols_as_lists.append((id, ans))
                else:
                    sols_as_lists.append((id, [ans]))
            # all answers are lists
            id, ans = get_most_common_solution(sols_as_lists)
            if not ans:
                raise NoSolutionFoundError("No answer was in majority")
            if len(ans) == 1:
                if id.endswith('[]'):
                    id = id[:-2]
                ans = ans[0]
            assert isinstance(ans, str) or isinstance(ans, list)
            return id, ans

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
        return self.__solve_with_all_solvers(question, table_mode=True)
