import json
from collections import defaultdict
from dataclasses import dataclass

from openedu.questions.question import Question
from solvers.utils import get_ans_id

AnswerType = list[str]


@dataclass
class CellData:
    id: str | None = None
    value: str | None = None


def format_table_row(row: list[CellData]):
    return f"|{'|'.join(cd.value or '   ' for cd in row)}|"


def format_table(table: list[list[CellData]]):
    heading = f"|{'|'.join(cd.value for cd in table[0])}|"
    heading += "\n" + f"|{'|'.join(['---' for _ in table[0]])}|"
    body = f"{'\n'.join(format_table_row(row) for row in table[1:])}"
    return heading + body


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
                answers_ids = [get_ans_id(self.options, ans) for ans in answer_col]
                _answer[table_col.id].extend(answers_ids)

        return self.id, json.dumps({"answer": _answer}, sort_keys=True)

    def query(self):
        return f"""Необходимо заполнить таблицу.Ваша задача — распределить варианты ответов.
** Задание: **
{self.text}

** Таблица: **
{format_table(self.table)}

** Распределяемые
элементы: **
{'\n'.join(ans for ans, aid in self.options)}

** Требования к ответу: **
1. Выведите ячейки заполненной таблицы обходя таблицу по  строкам.
2. Каждый элемент должен быть на отдельной  строке.
3. Значения в одной ячейке нужно отделять от значений в другой с помощью пустой строки
3. Сначала нужно вывести все элементы первой сроки, потом второй, потом третьей и т.д.
4. Чтобы отделить ячейки одной строки от ячеек другой, нужно использовать две пустые строки в качестве разделителя
5. Не добавляйте пояснений, номеров или дополнительных символов, все значения должны выглядеть так же, как они были даны

Пример: Если таблица:
| Название | Тип | Размер |
| --- | --- | --- |
| Солнце | | |
| Луна | | |

А распределяемые элементы:
Звезда
Спутник
Маленький
Большой

То правильный ответ будет:
Название

Тип

Размер

Солнце

Звезда

Большой

Луна

Спутник

Маленький
"""
