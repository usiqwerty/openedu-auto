from bs4 import Tag
from pydantic import BaseModel

from openedu.questions.question import Question


class MatchQuestion(BaseModel, Question):
    type: str = "match"
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


def parse_match_question(problem: Tag):
    questions = []
    answers = []
    q_text = problem.find('p').text
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
            questions.append((field_text, field_id))

    ans_place = table_div.select_one("div.conf-answers-place")
    for answer in ans_place.find_all():
        answers.append((answer.text.strip(), answer['id']))

    response_div = problem.select_one("div.wrapper-problem-response")
    q_id = response_div.find("input")['id']

    questions.sort(key=lambda x: x[1])
    answers.sort(key=lambda x: x[1])
    return MatchQuestion(text=q_text, id=q_id, fields=questions, options=answers)
