import json

from bs4 import Tag
from pydantic import BaseModel

from openedu.questions.match.abstract_match import AbstractMatchQuestion, CellData


class FixedMatchQuestion(AbstractMatchQuestion):
    type: str = "fixed-match"

    @staticmethod
    def parse(problem: Tag, prepend_lines: list[str] | None = None):
        # TODO: field and options may have escaped characters
        #  for now this is expected (and so in tests), but maybe LLMs
        #  would feel better without redundant backslashes
        answers = []
        lines = prepend_lines or []
        for child in problem.select('p, table'):
            if child.name == 'p':
                if child.text.strip():
                    lines.append(child.text.strip())
            else:
                break

        table_div = problem  # .select_one("div.matching_table")
        table = table_div.find('table')
        headers = [th.text.strip() for th in table.find_all("th")]

        _table = []
        for tr in table.find_all("tr"):
            row = []
            for td in tr.find_all("td"):
                field_id = None
                field_value = None
                if "conf-answers-place" in td.get('class', ""):
                    field_id = td['id']
                else:
                    field_value = [td.text.strip()]
                row.append(CellData(id=field_id, value=field_value))
            if row:
                _table.append(row)

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

        answers.sort(key=lambda x: x[1])

        headers = [[CellData(value=[h]) for h in headers]]
        _table = headers + _table
        return FixedMatchQuestion(text='\n'.join(lines), id=q_id, options=answers,
                                  correct_answer=correct_answer, table=_table)
