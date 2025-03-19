import json
import re

from bs4 import Tag
from pydantic import BaseModel

from errors import NoSolutionFoundError
from openedu.questions.question import Question
from solvers.utils import get_ans_id


def parse_custom_markdown(text):
    pattern = re.compile(r"[*~]{0,2}([\w\s]+)[*~]{0,2}(\s*\.\{[\w\W]+})", re.UNICODE)
    match = re.search(pattern, text)
    if not match:
        return text

    # TODO: i think we can deal without strip
    return match.group(1).strip()


class NewMatchField(BaseModel):
    is_fixed: bool
    value: list[str] | None
    id: str | None


class NewMatchQuestion(BaseModel, Question):
    type: str = 'new-match'
    id: str
    text: str
    options: list[tuple[str, str]]
    fields: list[list[NewMatchField]]

    def format_table(self) -> str:
        lines = []
        for row in self.fields:
            srow = "|" + '|'.join((c.value or ['   '])[0] for c in row) + "|"
            lines.append(srow)
        return '\n'.join(lines)

    def query(self) -> str:
        return f"""Реши задачу, необходимо заполнить таблицу, в ответе необходимо вывести уже заполенную таблицу.
Выводить нужно только выбранные данные, без комментариев, пояснений или форматирования. Используй только предложенные варианты, никак их не изменяя

**Задание:**  
{self.text}

{self.format_table()}

**Варианты ответов:**
{'\n'.join(x[0] for x in self.options)}
"""

    def compose(self, answer: list[list[str | None]]) -> tuple[str, str | dict]:
        answers = {}
        for row_ans, row_table in zip(answer, self.fields):
            for cell_ans, cell_table in zip(row_ans, row_table):
                if not cell_table.is_fixed:
                    cell_ans_id = get_ans_id(self.options, cell_ans)
                    answers[cell_table.id] = [cell_ans_id]
        return self.id, str({'answer': answers}).replace("'", '"')


def parse_new_match(tag: Tag) -> NewMatchQuestion:
    json_data = json.loads(tag.select_one('.adv-app')['data-initial-data'].replace("'", '"'))
    text = json_data['content']['body']
    qid = tag.find('input')['id']
    options = [(x['title'], x['id']) for x in json_data['answers']]
    fields = []
    for json_row in json_data['table']:
        row = []
        for cell in json_row:
            value = cell.get('value')
            if value is None:
                final_value = None
            else:
                final_value = [parse_custom_markdown(v) for v in value]
            row.append(NewMatchField(is_fixed=cell['isFixed'], value=final_value, id=cell.get('id')))
        fields.append(row)
    return NewMatchQuestion(id=qid, text=text, fields=fields, options=options)
