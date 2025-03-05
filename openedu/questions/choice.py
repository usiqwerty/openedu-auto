from bs4 import Tag
from pydantic import BaseModel

from openedu.questions.question import Question


class ChoiceQuestion(BaseModel, Question):
    type: str = "choice"
    text: str
    options: list[str]
    ids: list[str]

    def query(self):
        return (f"{self.text}\n"
                f"В ответе напиши только ответ, разные ответы пиши в разных строках\n" +
                '\n'.join(f"{ans}" for ans in self.options))


def parse_choice_problem(questions: Tag):
    problem_text = ""

    for child in questions.children:
        if child.name == "p":
            problem_text += child.text
        elif child.name == "div":
            legend = child.find('legend')
            if legend:
                problem_text = legend.text
            qs = [question.text.strip() for question in child.find_all('label')]
            ids = [qid['id'] for qid in child.find_all('input')]

            if ids:
                return ChoiceQuestion(text=problem_text, options=qs, ids=ids)
