import json

from bs4 import Tag
from pydantic import BaseModel

from openedu.questions.question import Question
from solvers.utils import get_ans_id


class FixedMatchQuestion(BaseModel, Question):
    type: str = "fixed-match"
    text: str
    id: str
    fields: list[tuple[str, str]]
    options: list[tuple[str, str]]

    def query(self):
        return f"""Необходимо установить однозначное соответствие между элементами двух групп. Элементы первой группы (фиксированные) уже расположены в определенном порядке. Ваша задача — распределить элементы второй группы (распределяемые) так, чтобы каждый элемент из второй группы соответствовал элементу из первой группы, сохраняя порядок фиксированных элементов.
    
**Задание:**
{self.text}

**Фиксированные элементы:**
{'\n'.join(field for field, fid in self.fields)}

**Распределяемые элементы:**
{'\n'.join(ans for ans, aid in self.options)}

**Требования к ответу:**
1. Выведите ТОЛЬКО распределяемые элементы в порядке, соответствующем порядку фиксированных элементов.
2. Каждый элемент должен быть на отдельной строке.
3. Не добавляйте пояснений, номеров или дополнительных символов.

Пример: 
Если фиксированные элементы:
Солнце
Луна

А распределяемые элементы:
Звезда
Спутник

То правильный ответ будет
Звезда
Спутник
"""

    def compose(self, answers: list[str]):
        choices = {}
        # {"a1": [], "a2": [], "a3": [], "a4": [], "a5": ["b1"]}
        for field, ans in zip(self.fields, answers):
            field_name, field_id = field
            choices[field_id] = [get_ans_id(self.options, ans)]
        return self.id, str({"answer": choices}).replace("'", '"')

    @staticmethod
    def parse(problem: Tag, prepend_lines: list[str] = None):
        # TODO: field and options may have escaped characters
        #  for now this is expected (and so in tests), but maybe LLMs
        #  would feel better without redundant backslashes
        questions = []
        answers = []
        lines = prepend_lines or []
        lines += [problem.find('p').text]

        table_div = problem.select_one("div.matching_table")
        table = table_div.find('table')
        for tr in table.find_all("tr"):
            field_id = ""
            field_text = ""
            for td in tr.find_all("td"):
                if "conf-answers-place" in td.get('class', ""):
                    field_id = td['id']
                else:
                    field_text = td.text
            if field_id and field_text:
                questions.append((field_text.strip(), field_id))

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
        return FixedMatchQuestion(text='\n'.join(lines), id=q_id, fields=questions, options=answers, correct_answer=correct_answer)
