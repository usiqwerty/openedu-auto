import json
import os.path

import config
from openedu.questions.question import Question
from openedu_processor import OpenEduProcessor

solutions_dir = os.path.join(config.userdata_dir, 'solutions')


class AnswersSaver(OpenEduProcessor):
    require_incomplete = False

    answers: dict

    def __init__(self):
        super().__init__(None, None)

    def pull_answers(self, course_id: str):
        self.answers = {}
        os.makedirs(solutions_dir, exist_ok=True)
        self.process_course(course_id)
        solution_fn = os.path.join(solutions_dir, f"{course_id}.json")
        with open(solution_fn, 'w', encoding='utf-8') as f:
            json.dump(self.answers, f)

    def process_problem(self, course_id: str, problem: list[Question]):
        for question in problem:
            self.answers[question.id] = question.correct_answer
