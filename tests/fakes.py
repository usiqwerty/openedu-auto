from requests import Response

from images.image_describer import ImageDescriber
from openedu.questions.choice import ChoiceQuestion
from openedu.questions.freematch import FreeMatchQuestion
from openedu.questions.match import MatchQuestion
from solvers.abstract_solver import AbstractSolver


class FakeSession:
    history: list
    cookies: dict

    def __init__(self):
        self.history = []
        self.cookies = {}

    def get(self, url, *, headers=None, cookies=None):
        print("fake get")
        self.history.append({"method": 'get', "url": url, "headers": headers, "cookies": cookies})

    def post(self, url, *, headers=None, cookies=None, json=None, data=None):
        if json is None:
            json = data
        print("fake post")
        self.history.append(
            {"method": 'post', "url": url, "headers": headers, "cookies": cookies, "json": json, "data": data})
        r = Response()
        r.status_code = 200
        r._content = b'{"current_score": 1, "total_possible": 1}'
        return r


class DummySolver(AbstractSolver):
    def solve_choice(self, question: ChoiceQuestion):
        return "input_bibaboba_0_0", "choice_0"

    def solve_match(self, question: MatchQuestion):
        return "input_id", ["value1", "value2"]

    def solve_freematch(self, question: FreeMatchQuestion):
        return "input_id", '{"answer": {"a1": "b1, "a2": "b2"}}'


class DummyDescriber(ImageDescriber):
    def get_description(self, url: str) -> str:
        pass

    def describe(self, url: str) -> str:
        return "Изображение: Elon Musk"
