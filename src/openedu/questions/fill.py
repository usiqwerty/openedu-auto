from bs4 import Tag

from src.openedu.questions.question import Question


class FillQuestion(Question):
    type: str = "fill"
    id: str
    text: str

    def query(self) -> str:
        return f"""{self.text}\nВ ответе напиши только ответ, без каких-либо дополнений, пояснений и прочих лишних обозначений."""

    def compose(self, answer: str) -> tuple[str, str]:
        return self.id, answer

    @staticmethod
    def parse(tag: Tag, prepend_lines: list[str] | None = None) -> "FillQuestion":
        lines = (prepend_lines or []) + []
        for p in tag.find_all("p"):
            lines.append(p.text.strip())
        label = tag.find('label')
        if label:
            lines.append(label.text.strip())

        input_tag = tag.find("input")
        q_id = input_tag['id']
        correct_answer = input_tag['value']

        question_text = '\n'.join(filter(lambda x: x, lines))
        return FillQuestion(id=q_id, text=question_text, correct_answer=correct_answer)  # type:ignore[call-arg]
