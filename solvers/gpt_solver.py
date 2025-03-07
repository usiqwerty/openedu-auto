import json
import os.path
from abc import abstractmethod, ABC

import logging

from openedu.questions.freematch import FreeMatchQuestion
from openedu.questions.question import Question
from openedu.questions.choice import ChoiceQuestion
from openedu.questions.match import MatchQuestion
from solvers.abstract_solver import AbstractSolver
from solvers.utils import compose_answer, compose_match, compose_freematch


class LLMSolver(AbstractSolver, ABC):
    cache_fn: str

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
            self.cache_set(query, self.make_gpt_request(query))
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
        raw = filter(lambda x: x, raw)
        res: list[str] | str
        if len(raw) == 1:
            res = raw[0]
        else:
            res = raw
        return compose_answer(res, question.ids, question.options)

    def solve_match(self, question: MatchQuestion):
        res = self.get_answer(question.query()).split('\n')

        return compose_match(res, question.fields, question.options, question.id)

    def solve_freematch(self, question: FreeMatchQuestion):
        res = self.get_answer(question.query()).split('\n')
        res = list(filter(lambda x: x, res))
        return compose_freematch(res, question)