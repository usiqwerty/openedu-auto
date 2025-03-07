import urllib.parse

from bs4 import Tag
from pydantic import BaseModel

from images.image_describer import ImageDescriber
from openedu.questions.question import Question


class FreeMatchQuestion(BaseModel, Question):
    type: str = "freematch"
    id: str
    text: str
    column_headers: list[str]
    field_columns: list[list[str]]
    option_columns: list[list[tuple[str, str]]]

    def query(self) -> str:
        return f"""Реши задачу, в ответе необходимо выбрать по элементу из каждой группы  

**Задание:**  
{self.text}

**Элементы группы 1:**
{'\n'.join(x[0] for x in self.option_columns[0])}

**Элементы группы 2:**
{'\n'.join(x[0] for x in self.option_columns[1])}


**Формат вывода:**  
- Каждый элемент — на отдельной строке.  
- Без комментариев, пояснений или форматирования, только выбранные данные  

**Пример структуры вывода:**  
Имя 1    
Изображение 1
Имя 2
Изображение 2
"""


def parse_freematch_problem(problem: Tag, describer: ImageDescriber):
    questions = []
    answers = []
    q_text = problem.find('p').text
    table_div = problem.select_one("div.matching_table")
    table = table_div.find('table')

    column_headers = []
    columns = []

    for tr in table.select("tr"):
        for th in tr.find_all("th"):
            column_headers.append(th.text.strip())
            columns.append([])

        for i, td in enumerate(tr.select("td")):
            if "conf-answers-place" in td.get('class', ""):
                columns[i].append(td['id'])
            else:
                print(f"strange, conf-answers-place is not in td.class: {td}")

    all_col_answers = []
    for ans_place in table_div.select("div.conf-answers-place"):
        column_answers = []
        for answer in ans_place.select("div.conf-item"):
            if answer.text:
                column_answers.append((answer.text, answer['id']))
            else:
                img = answer.find("img")
                img_url = urllib.parse.urljoin("https://courses.openedu.ru/", img['src'])
                img_content = describer.describe(img_url)
                column_answers.append((img_content, answer['id']))
            # answers.append((answer.text, answer['id']))
        column_answers.sort(key=lambda x: x[1])
        all_col_answers.append(column_answers)

    response_div = problem.select_one("div.wrapper-problem-response")
    q_id = response_div.find("input")['id']
    # print(all_col_answers)
    return FreeMatchQuestion(text=q_text,
                          id=q_id,
                          column_headers=column_headers,
                          field_columns=columns,
                          option_columns=all_col_answers
                          )
