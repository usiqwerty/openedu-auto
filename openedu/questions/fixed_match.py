import json
import re
from typing import Iterable

from bs4 import Tag
from pydantic import BaseModel

from errors import NoSolutionFoundError
from openedu.questions.question import Question
from solvers.utils import get_ans_id


def format_table_row(field: tuple[str, list[str]]):
    field_text, field_ids = field
    return f"|{field_text}|{'|'.join([' ' for _ in field_ids])}|"


def format_table(fields, headers):
    return f"""|{'|'.join(headers)}|
|{'|'.join(['---' for _ in headers])}|
{'\n'.join(format_table_row(field) for field in fields)}
"""


def fields_by_columns(fields: list[tuple[str, list[str]]])->Iterable[tuple[str, str]]:
    width = len(fields[0][1])
    for col in range(width):
        for field in fields:
            yield field[0], field[1][col]


class FixedMatchQuestion(BaseModel, Question):
    type: str = "fixed-match"
    text: str
    id: str
    headers: list[str]
    fields: list[tuple[str, list[str]]]
    options: list[tuple[str, str]]

    def query(self):
        return f"""Необходимо заполнить таблицу. Ваша задача — распределить варианты ответов, ответ нужно выводить по столбцам.
    
**Задание:**
{self.text}

**Таблица:**
{format_table(self.fields, self.headers)}

**Распределяемые элементы:**
{'\n'.join(ans for ans, aid in self.options)}

**Требования к ответу:**
1. Выведите ТОЛЬКО распределяемые элементы в порядке, соответствующем порядку фиксированных элементов.
2. Каждый элемент должен быть на отдельной строке.
3. Сначала нужно вывесли все элементы первого столбца, потом второго, потом третьего и т.д.
4. Не добавляйте пояснений, номеров или дополнительных символов.

Пример: 
Если таблица:
|Название|Тип|Размер|
|---|---|---|
|Солнце| | |
|Луна| | |

А распределяемые элементы:
Звезда
Спутник
Маленький
Большой

То правильный ответ будет
Звезда
Спутник
Большой
Маленький
"""

    def compose(self, answers: list[str]):
        answers = [re.sub(r"\s+", ' ', opt) for opt in answers]
        choices = {}
        # {"a1": [], "a2": [], "a3": [], "a4": [], "a5": ["b1"]}
        width = len(self.fields[0][1])
        table_size = width * len(self.fields)
        if len(answers) != table_size:
            raise NoSolutionFoundError(f"Answer expected to have {table_size} elements, but was {len(answers)}")

        for field, ans in zip(fields_by_columns(self.fields), answers):
            field_name, field_id = field
            choices[field_id] = [get_ans_id(self.options, ans)]
        return self.id, str({"answer": choices}).replace("'", '"')

    @staticmethod
    def parse(problem: Tag, prepend_lines: list[str] = None):
        # TODO: field and options may have escaped characters
        #  for now this is expected (and so in tests), but maybe LLMs
        #  would feel better without redundant backslashes
        questions: list[tuple[str, list[str]]] = []
        answers = []
        lines = prepend_lines or []
        lines += [problem.find('p').text]

        table_div = problem.select_one("div.matching_table")
        table = table_div.find('table')
        headers = [th.text.strip() for th in table.find_all("th")]
        for tr in table.find_all("tr"):
            field_ids = []
            field_text = ""
            for td in tr.find_all("td"):
                if "conf-answers-place" in td.get('class', ""):
                    field_ids.append(td['id'])
                else:
                    field_text = td.text
            if field_ids and field_text:
                questions.append((field_text.strip(), field_ids))

        ans_place = table_div.select_one("div.conf-answers-place")
        for answer in ans_place.find_all(attrs={"class": "conf-item conf-draggable"}):
            answers.append((answer.text.strip(), answer['id']))

        response_div = problem.select_one("div.wrapper-problem-response")
        answer_input = response_div.find("input")
        q_id = answer_input['id']

        answer_json_string = answer_input.get("value", "").replace("'", '"')
        if answer_json_string:
            correct_answer = json.loads(answer_json_string)['answer']
        else:
            correct_answer = None

        questions.sort(key=lambda x: x[1])
        answers.sort(key=lambda x: x[1])
        return FixedMatchQuestion(text='\n'.join(lines), id=q_id, fields=questions, options=answers,
                                  correct_answer=correct_answer, headers=headers)
