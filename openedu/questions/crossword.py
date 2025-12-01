import enum
import json
import re

from bs4 import Tag
from pydantic import BaseModel

from openedu.questions.question import Question


class CrosswordItemOrientation(enum.StrEnum):
    horizontal = "horizontal"
    vertical = "vertical"


class CrosswordItem(BaseModel):
    clue: str
    hint: str
    answer: str | None
    start_x: int
    start_y: int
    position: int
    unique_position: int
    orientation: CrosswordItemOrientation


class Crossword(BaseModel, Question):
    type: str = "crossword"
    text: str = ""
    id: str
    questions: list[CrosswordItem]

    def compose(self, answer) -> tuple[str, str | dict]:
        state = {}
        # А вдруг нет?
        # На странице всегда пишут макс. балл за задание, можно брать оттуда
        total = len(self.questions)
        for answer_string, question_item in zip(answer, self.questions):
            if question_item.orientation == CrosswordItemOrientation.horizontal:
                delta = 1, 0
            elif question_item.orientation == CrosswordItemOrientation.vertical:
                delta = 0, 1
            else:
                raise NotImplementedError
            x = question_item.start_x
            y = question_item.start_y
            position_dict = {}
            for letter in answer_string:
                # position is 1-based x,y tuple
                position_dict[f"{x},{y}"] = letter
                x += delta[0]
                y += delta[1]

            state[f"question_{question_item.unique_position}"] = {
                "position": position_dict,
                "word": answer_string
            }

        return self.id, json.dumps({"answer": {"user_state": state, "grade": total, "max_grade": total}},
                                   ensure_ascii=False)

    @staticmethod
    def parse(tag: Tag, prepend_lines: list[str] = None) -> "Question":
        questions = []
        for scr in tag.select("script"):
            r = re.search(r"let\s*data\s*=\s*\{'student_data':\s*(\[[\w\W]+])[,\'\"\w:\s]+};", scr.text)
            if r is None:
                continue
            l = r.group(1).replace("'", '"')

            for it in json.loads(l):
                if it['orientation'] == "across":
                    orient = CrosswordItemOrientation.horizontal
                elif it['orientation'] == "down":
                    orient = CrosswordItemOrientation.vertical
                else:
                    raise NotImplementedError(f"unknown crossword item orientation: {it['orientation']}")
                # clue is visible text
                questions.append(CrosswordItem(
                    clue=it['clue'],
                    hint=it['hint'],
                    answer=it['answer'],
                    start_x=it['start_x'],
                    start_y=it['start_y'],
                    position=it['position'],
                    unique_position=it['unique_position'],
                    orientation=orient))

        crossword_input = tag.select_one("#crossword_input").select_one("input")
        qid = crossword_input['id']
        return Crossword(id=qid, questions=questions)

    def query(self) -> str:
        raise NotImplementedError
