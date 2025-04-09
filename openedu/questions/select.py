from bs4 import Tag
from fuzzywuzzy import fuzz
from pydantic import BaseModel

from errors import NoSolutionFoundError
from openedu.questions.question import Question


class SelectQuestion(BaseModel, Question):
    type: str = "select"
    text: str = "text here"
    id: str
    options: list[tuple[str, str]]

    def query(self) -> str:
        return (f"{self.text}\n"
                f"В ответе напиши только ответ, без каких-либо дополнений и поясненийх. Ты можешь выбирать только среди вариантов:\n" +
                '\n'.join(f"{ans[0]}" for ans in self.options))

    def compose(self, answer: str):
        ans_id = None
        for opt, option_id in self.options:
            if fuzz.ratio(opt, answer.strip()) > 85:
                ans_id = option_id
                break
        if ans_id is None:
            raise NoSolutionFoundError
        return self.id, ans_id

    @staticmethod
    def parse(tag: Tag, prepend_lines: list[str] = None) -> "SelectQuestion":
        lines = prepend_lines + []
        q_id = None
        answers = []
        for child in tag.children:

            if child.name == "p":
                lines.append(child.text)

        sel = tag.select_one('select')
        q_id = sel['id']
        correct_answer = None
        for opt in sel.find_all('option'):
            if 'default' not in opt['value']:
                if opt.get('selected'):
                    correct_answer = opt['value']
                answers.append((opt.text.strip(), opt['value']))

        return SelectQuestion(id=q_id, text='\n'.join(lines), options=answers, correct_answer=correct_answer)
