import datetime
import json
import logging
import os.path
import time
from abc import abstractmethod, ABC
from typing import Any

from pydantic import BaseModel

from openedu.questions.choice import ChoiceQuestion
from openedu.questions.fill import FillQuestion
from openedu.questions.match.abstract_match import AbstractMatchQuestion
from openedu.questions.select import SelectQuestion
from solvers.abstract_solver import AbstractSolver


def striplines(raw_result: str) -> str:
    "Call .strip() on each line and then join back"
    return '\n'.join([result_line.strip() for result_line in raw_result.split('\n')])


class LLMSolver(AbstractSolver, ABC):
    cache_fn: str
    last_described: float = 0
    interval_sec = 5

    @property
    def cache_path(self):
        return os.path.join("userdata", self.cache_fn)

    _cache: dict

    def __init__(self):
        self._cache = self.load_cache()

    def cache_get(self, key: str):
        return self._cache[key]

    def cache_set(self, key: str, val):
        self._cache[key] = val
        self.save_cache(self._cache)

    @abstractmethod
    def make_gpt_request(self, query, *, sysprompt, _json) -> str:
        pass

    def get_answer(self, query, *, sysprompt=None, _json: type | None = None) -> str:
        print("Getting LLM answer...")
        if query not in self._cache:
            logging.debug("Question was not in cache")

            now = datetime.datetime.now().timestamp()
            delta = now - self.last_described
            if delta < self.interval_sec:
                time.sleep(delta)
            raw_result = self.make_gpt_request(query, sysprompt=sysprompt, _json=_json)
            result = raw_result
            if not _json:
                result = striplines(raw_result.strip())
            self.cache_set(query, result)
            self.last_described = now
        else:
            logging.debug("Picking LLM answer from cache")
        return self.cache_get(query)

    def load_cache(self):
        try:
            with open(self.cache_path, encoding='utf-8') as f:
                cache = json.load(f)
        except FileNotFoundError:
            cache = {}
        return cache

    def save_cache(self, data):
        with open(self.cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f)

    def solve_choice(self, question: ChoiceQuestion) -> tuple[str, str | list[str]]:
        raw = self.get_answer(question.query()).split('\n')
        raw = list(filter(lambda x: x, raw))
        res: list[str] | str
        if len(raw) == 1:
            res = raw[0]
        else:
            res = raw
        return question.compose(res)

    def solve_unified_match(self, question: AbstractMatchQuestion):
        class TableType(BaseModel):
            result: list[list[list[str]]]

        json_data: Any = self.get_answer(question.query(), _json=TableType)
        return question.compose(json_data)

    def solve_select(self, question: SelectQuestion) -> tuple[str, str]:
        res = self.get_answer(question.query())
        return question.compose(res)

    def solve_fill(self, question: FillQuestion) -> tuple[str, str]:
        res = self.get_answer(question.query())
        return question.compose(res)
