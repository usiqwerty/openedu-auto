from bs4 import Tag
from pydantic import BaseModel

from openedu.questions.question import Question


class SelectQuestion(BaseModel, Question):
    type: str = "select"
    text: str = "text here"
    id: str
    options: list[tuple[str, str]]

    def query(self) -> str:
        raise NotImplementedError


def parse_select_question(tag: Tag) -> SelectQuestion:
    text = ""
    q_id = None
    answers = []
    for child in tag.children:

        if child.name == "p":
            text += child.text

    sel = tag.select_one('select')
    q_id = sel['id']
    for opt in sel.find_all('option'):
        if 'default' not in opt['value']:
            answers.append((opt.text.strip(), opt['value']))

    return SelectQuestion(id=q_id, text=text, options=answers)
