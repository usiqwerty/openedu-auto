import json
import urllib.parse

from bs4 import Tag
from pydantic import BaseModel

from errors import NoSolutionFoundError
from images.image_describer import ImageDescriber
from openedu.questions.question import Question
from solvers.utils import lookup_option_id_in_columns


class FreeMatchQuestion(BaseModel, Question):
    type: str = "freematch"
    id: str
    text: str
    column_headers: list[str]
    field_columns: list[list[str]]
    option_columns: list[list[tuple[str, str]]]

    def query(self) -> str:
        return f"""Реши задачу, в ответе необходимо выбрать по элементу из каждой группы.
Выводить нужно только выбранные данные, без комментариев, пояснений или форматирования.  
**Пример структуры вывода:**  
Имя 1
Изображение 1
Имя 2
Изображение 2

**Задание:**  
{self.text}

**Элементы группы 1:**
{'\n'.join(x[0] for x in self.option_columns[0])}

**Элементы группы 2:**
{'\n'.join(x[0] for x in self.option_columns[1])}

"""

    def compose(self, flat_answers: list[str]):
        col_num = 2
        answer = {}

        for i in range(0, len(flat_answers), col_num):
            row_ = i // col_num
            for col in range(col_num):
                row_key = self.field_columns[col][row_]
                ans_id = lookup_option_id_in_columns(flat_answers[i + col], self.option_columns)
                if ans_id is None:
                    raise NoSolutionFoundError(f"Answer {flat_answers} does not solve {self!r}")
                answer[row_key] = [ans_id]

        return self.id, str({'answer': answer})


    @staticmethod
    def parse(problem: Tag, prepend_lines: list[str] = None, describer: ImageDescriber = None):
        lines = prepend_lines or []
        lines += [p.text for p in problem.select('.matching_table > p')]

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
        answer_input = response_div.find("input")
        q_id = answer_input['id']

        answer_json_string = answer_input.get("value", "").replace("'", '"')
        if answer_json_string:
            correct_answer = json.loads(answer_json_string)['answer']
        else:
            correct_answer = None
        return FreeMatchQuestion(text='\n'.join(lines),
                              id=q_id,
                              column_headers=column_headers,
                              field_columns=columns,
                              option_columns=all_col_answers,
                              correct_answer=correct_answer)
