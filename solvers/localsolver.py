import hashlib
import json
import os
from typing import Any

import config
from errors import HashMismatch, NoSolutionFoundError
from openedu.questions.choice import ChoiceQuestion
from openedu.questions.fill import FillQuestion
from openedu.questions.freematch import FreeMatchQuestion
from openedu.questions.match import MatchQuestion
from openedu.questions.new_match import NewMatchQuestion
from openedu.questions.question import Question
from openedu.questions.select import SelectQuestion
from solvers.abstract_solver import AbstractSolver


class LocalSolver(AbstractSolver):
    answers: dict[str, Any]

    def __init__(self, solution_path: str):
        with open(os.path.join(solution_path), encoding='utf-8') as f:
            data = json.load(f)
        sha256 = data['sha256']
        self.answers = data['answers']
        got_hash = hashlib.sha256(str(self.answers).encode()).hexdigest()
        if got_hash != sha256 and not config.config.get("ls-allow-hash-mismatch"):
            raise HashMismatch("Solution corrupted")

    def solve(self, question: Question):
        ans = self.answers.get(question.id)
        if ans is None:
            raise NoSolutionFoundError(f"question: {question.id}, answer: {ans}")
        question_id = question.id
        if isinstance(ans, list) and len(ans) > 1:
            question_id += "[]"
        return question_id, ans

    def solve_choice(self, question: ChoiceQuestion) -> tuple[str, str | list[str]]:
        ...

    def solve_match(self, question: MatchQuestion) -> tuple[str, str | list[str]]:
        ...

    def solve_freematch(self, question: FreeMatchQuestion) -> tuple[str, str | list[str]]:
        ...

    def solve_select(self, question: SelectQuestion) -> tuple[str, str | list[str]]:
        ...

    def solve_fill(self, question: FillQuestion) -> tuple[str, str | list[str]]:
        ...

    def solve_new_match(self, question: NewMatchQuestion) -> tuple[str, str | list[str]]:
        ...
