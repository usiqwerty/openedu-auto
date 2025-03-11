from bs4 import Tag
from pydantic import BaseModel

from openedu.questions.question import Question
from openedu.utils import ensure_ids_same


class ChoiceQuestion(BaseModel, Question):
    type: str = "choice"
    text: str
    options: list[str]
    ids: list[str]

    def query(self):
        return (f"{self.text}\n"
                f"В ответе напиши только ответ, без каких-либо дополнений и пояснений, разные ответы пиши в разных строках. Ты можешь выбирать только среди вариантов:\n" +
                '\n'.join(f"{ans}" for ans in self.options))


def parse_choice_question(questions: Tag):
    problem_text = ""

    for child in questions.children:
        if child.name in ["p", "pre"]:
            problem_text += child.text
        elif child.name == "div":
            legend = child.find('legend')
            if legend:
                problem_text = legend.text
            qs = [question.text.strip() for question in child.find_all('label')]
            ids = [qid['id'] for qid in child.find_all('input')]

            if ids:
                ensure_ids_same(ids)
                return ChoiceQuestion(text=problem_text, options=qs, ids=ids)
