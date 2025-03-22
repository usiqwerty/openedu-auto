from bs4 import Tag
from pydantic import BaseModel

from openedu.questions.question import Question


class FillQuestion(BaseModel, Question):
    type: str = "fill"
    id: str
    text: str

    def query(self) -> str:
        return f"""{self.text}\nВ ответе напиши только ответ, без каких-либо дополнений, пояснений и прочих лишних обозначений."""

    def compose(self, answer: str):
        return self.id, answer


def parse_fill_question(tag: Tag) -> FillQuestion:
    text = ""
    for p in tag.find_all("p"):
        text += p.text
    label = tag.find('label')
    if label:
        text += "\n" + label.text

    input_tag = tag.find("input")
    q_id = input_tag['id']
    correct_answer = input_tag['value']
    return FillQuestion(id=q_id, text=text, correct_answer=correct_answer)

