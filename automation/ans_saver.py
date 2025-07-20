import hashlib
import json
import logging
import os.path

import config
from openedu.questions.question import Question
from automation.openedu_processor import OpenEduProcessor
from tests.fakes import DummyDescriber

solutions_dir = os.path.join(config.userdata_dir, 'solutions')


class AnswersSaver(OpenEduProcessor):
    require_incomplete = False

    answers: dict

    def __init__(self):
        super().__init__(None, DummyDescriber())

    def pull_answers(self, course_id: str):
        self.answers = {}
        os.makedirs(solutions_dir, exist_ok=True)
        self.process_course(course_id)

    def process_problem(self, course_id: str, problem: list[Question]):
        solution_fn = os.path.join(solutions_dir, f"{course_id}.json")

        for question in problem:
            if not question.correct_answer:
                logging.error(f"Question doesn't have a correct answer: {question}")
            self.answers[question.id] = question.correct_answer
        answers_str = str(self.answers)
        sha256_hash = hashlib.sha256(answers_str.encode()).hexdigest()
        data = {"course": course_id, "sha256": sha256_hash, "answers": self.answers}
        with open(solution_fn, 'w', encoding='utf-8') as f:
            json.dump(data, f)
