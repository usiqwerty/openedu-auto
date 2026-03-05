import json
from collections import defaultdict
from dataclasses import dataclass

from openedu.questions.question import Question
from solvers.utils import get_ans_id, get_ans_id_best

AnswerType = list[str]


@dataclass
class CellData:
    id: str | None = None
    value: str | None = None


def format_table(table: list[list[CellData]]):
    return [[[cell.value or []] for cell in row] for row in table]


class AbstractMatchQuestion(Question):
    type: str = "unified-match"
    text: str
    id: str

    options: list[tuple[str, str]]
    table: list[list[CellData]]

    def compose(self, answer: list[list[AnswerType]]) -> tuple[str, str | dict]:
        _answer: dict[str, list[str]] = defaultdict(list)
        for answer_row, table_row in zip(answer, self.table):
            for answer_col, table_col in zip(answer_row, table_row):
                if table_col.value is not None:
                    continue
                print(answer_col)
                answers_ids = [get_ans_id_best(self.options, ans) for ans in answer_col]
                _answer[table_col.id].extend(answers_ids)

        return self.id, json.dumps({"answer": _answer}, sort_keys=True)

    def query(self):
        return f"""Необходимо заполнить таблицу. Ваша задача — распределить варианты ответов.
** Задание: **
{self.text}

** Таблица: **
{format_table(self.table)}

** Распределяемые
элементы: **
{'\n'.join(ans for ans, aid in self.options)}

** Требования к ответу: **
0. Ответ обрабатывается автоматизированной системой, поэтому нужно чётко соответствовать требованиям 
1. Выведите ответ в формате json
2. Каждая ячейка - list[str] (т.к. может быть несколько значений в ячейке)
3. Каждая строка - list[list[str]]
4. Ответ (таблица) - list[list[list[str]]] 
5. Не добавляйте пояснений, номеров или дополнительных символов, все значения должны выглядеть так же, как они были даны

Пример ответа:
[[['1'], ['текст']], [['2'], ['второй']]]
"""
