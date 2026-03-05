import datetime
import json
import logging
import os.path
import time
from abc import abstractmethod, ABC

from openedu.questions.choice import ChoiceQuestion
from openedu.questions.fill import FillQuestion
from openedu.questions.fixed_match import FixedMatchQuestion
from openedu.questions.freematch import FreeMatchQuestion
from openedu.questions.new_match import NewMatchQuestion
from openedu.questions.select import SelectQuestion
from solvers.abstract_solver import AbstractSolver


def striplines(raw_result: str) -> str:
    "Call .strip() on each line and then join back"
    return '\n'.join([result_line.strip() for result_line in raw_result.split('\n')])


class LLMSolver(AbstractSolver, ABC):
    cache_fn: str
    last_described = 0
    interval_sec = 5

    @property
    def cache_path(self):
        return os.path.join("userdata", self.cache_fn)

    __cache: dict

    def __init__(self):
        self.__cache = self.load_cache()

    def cache_get(self, key: str):
        return self.__cache[key]

    def cache_set(self, key: str, val):
        self.__cache[key] = val
        self.save_cache(self.__cache)

    @abstractmethod
    def make_gpt_request(self, query, *, sysprompt, _json) -> str:
        pass

    def get_answer(self, query, *, sysprompt=None, json=False) -> str:
        if query not in self.__cache:
            logging.debug("Question was not in cache")

            now = datetime.datetime.now().timestamp()
            delta = now - self.last_described
            if delta < self.interval_sec:
                time.sleep(delta)
            raw_result = self.make_gpt_request(query, sysprompt=sysprompt, _json=json).strip()
            result = striplines(raw_result)
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

    def solve_match(self, question: FixedMatchQuestion) -> tuple[str, str]:
        # res = self.get_answer(question.query()).split('\n')
        raw = self.get_answer(question.query())
        json_data = json.loads(raw)
        return question.compose(json_data)

    def solve_freematch(self, question: FreeMatchQuestion) -> tuple[str, str]:
        res = self.get_answer(question.query()).split('\n')
        res = list(filter(lambda x: x, res))
        return question.compose(res)

    def solve_select(self, question: SelectQuestion) -> tuple[str, str]:
        res = self.get_answer(question.query())
        return question.compose(res)

    def solve_fill(self, question: FillQuestion) -> tuple[str, str]:
        res = self.get_answer(question.query())
        return question.compose(res)

    def solve_new_match(self, question: NewMatchQuestion) -> tuple[str, str]:
        raw = self.get_answer(question.query(), sysprompt="Ответ должен содержать валидный JSON", json=True)
        json_data = json.loads(raw)
        return question.compose(json_data)
