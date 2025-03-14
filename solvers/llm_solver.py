import datetime
import json
import os.path
import time
from abc import abstractmethod, ABC

import logging

from openedu.questions.freematch import FreeMatchQuestion
from openedu.questions.question import Question
from openedu.questions.choice import ChoiceQuestion
from openedu.questions.match import MatchQuestion
from openedu.questions.select import SelectQuestion
from solvers.abstract_solver import AbstractSolver
from solvers.utils import compose_choice, compose_match, compose_freematch, compose_select


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
    def make_gpt_request(self, query) -> str:
        pass

    def get_answer(self, query) -> str:
        if query not in self.__cache:
            logging.debug("Question was not in cache")

            now = datetime.datetime.now().timestamp()
            delta = now - self.last_described
            if delta < self.interval_sec:
                time.sleep(delta)
            self.cache_set(query, self.make_gpt_request(query))
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

    def solve_choice(self, question: ChoiceQuestion):
        raw = self.get_answer(question.query()).split('\n')
        raw = list(filter(lambda x: x, raw))
        res: list[str] | str
        if len(raw) == 1:
            res = raw[0]
        else:
            res = raw
        return compose_choice(res, question.ids, question.options)

    def solve_match(self, question: MatchQuestion):
        res = self.get_answer(question.query()).split('\n')

        return compose_match(res, question.fields, question.options, question.id)

    def solve_freematch(self, question: FreeMatchQuestion):
        res = self.get_answer(question.query()).split('\n')
        res = list(filter(lambda x: x, res))
        return compose_freematch(res, question)

    def solve_select(self, question: SelectQuestion) -> tuple[str, str | list[str]]:
        res = self.get_answer(question.query())
        return compose_select(res, question)
