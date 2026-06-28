import json
import urllib.parse

from bs4 import Tag

from src.images.image_describer import ImageDescriber
from src.openedu.questions.match.abstract_match import AbstractMatchQuestion, CellData


class FreeMatchQuestion(AbstractMatchQuestion):
    type: str = "freematch"

    @staticmethod
    def parse(problem: Tag, prepend_lines: list[str] | None = None, describer: ImageDescriber | None = None):
        lines = prepend_lines or []
        if describer is None:
            raise TypeError("Image describer should be given to parse this question")
        lines += [p.text for p in problem.select('.matching_table > p')]

        table_div = problem  # .select_one("div.matching_table")
        table = table_div.find('table')

        _table: list[list[CellData]] = []
        for tr in table.select("tr"):
            row = []
            for th in tr.find_all("th"):
                row.append(CellData(value=[th.text.strip()]))

            for i, td in enumerate(tr.select("td")):
                if "conf-answers-place" in td.get('class', ""):
                    row.append(CellData(id=td['id']))
                else:
                    print(f"strange, conf-answers-place is not in td.class: {td}")
            _table.append(row)

        answer_options: list[tuple[str, str]] = []
        for ans_place in table_div.select("div.conf-answers-place"):
            for answer in ans_place.select("div.conf-item"):
                if answer.text:
                    answer_options.append((answer.text, answer['id']))
                else:
                    img = answer.find("img")
                    img_url = urllib.parse.urljoin("https://courses.openedu.ru/", img['src'])
                    img_content = describer.describe(img_url)
                    answer_options.append((img_content, answer['id']))
                # answers.append((answer.text, answer['id']))

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
                                 options=answer_options,
                                 correct_answer=correct_answer,
                                 table=_table)
