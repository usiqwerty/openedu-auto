import json
import re

from bs4 import Tag

from src.openedu.questions.match.abstract_match import AbstractMatchQuestion, CellData


def parse_custom_markdown(text):
    pattern = re.compile(r"^[*~_]{0,2}([\w\W\s]*?[^\s_])[*~_]{0,2}\s*(\.\{[\w\W]+})?$", re.UNICODE)
    match = re.search(pattern, text)
    if not match:
        return text
    return match.group(1)


class NewMatchQuestion(AbstractMatchQuestion):
    type: str = 'new-match'

    @staticmethod
    def parse(tag: Tag, prepend_lines: list[str] | None = None) -> "NewMatchQuestion":
        # tag.select_one('.adv-app')
        json_data = json.loads(tag['data-initial-data'].replace("'", '"'))
        lines = prepend_lines or []
        text = '\n'.join(lines) + json_data['content']['body']
        text = text.strip()
        qid = tag.parent.find('input')['id']
        options = [(x['title'], x['id']) for x in json_data['answers']]
        table = []
        answer_input = tag.parent.select_one("input")

        answer_json_string = answer_input.get('value', "").replace("'", '"')
        if answer_json_string:
            correct_answer = json.loads(answer_json_string)['answer']
        else:
            correct_answer = None

        for json_row in json_data['table']:
            row = []
            for cell in json_row:
                value = cell.get('value')
                if value is None:
                    final_value = None
                else:
                    final_value = [parse_custom_markdown(v) for v in value]
                    assert isinstance(final_value[0], str)
                row.append(CellData(value=final_value, id=cell.get('id')))
            table.append(row)
        return NewMatchQuestion(id=qid, text=text, table=table, options=options, correct_answer=correct_answer)
