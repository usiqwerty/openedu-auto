from bs4 import Tag
from pydantic import BaseModel

from errors import NoSolutionFoundError
from openedu.questions.question import Question
from openedu.utils import ensure_ids_same
from solvers.utils import get_similar_index, extract_choice_from_id


class ChoiceQuestion(BaseModel, Question):
    type: str = "choice"
    text: str
    options: list[str]
    ids: list[str]

    def query(self):
        return (f"{self.text}\n"
                f"В ответе напиши только ответ, без каких-либо дополнений и пояснений, разные ответы пиши в разных строках. Ты можешь выбирать только среди вариантов (в каждой строке отдельный вариант):\n" +
                '\n'.join(f"{ans}" for ans in self.options))

    def compose(self, answer: list[str] | str):
        if isinstance(answer, str):
            return singular_choice(answer, self.ids, self.options)
        else:
            return plural_choice(answer, self.ids, self.options)


def parse_choice_question(questions: Tag):
    problem_text = ""

    for child in questions.children:
        if child.name in ["p", "pre"]:
            problem_text += child.text
        elif child.name == "div":
            legend = child.find('legend')
            if legend:
                problem_text += legend.text
            qs = [question.text.strip() for question in child.find_all('label')]
            ids = [qid['id'] for qid in child.find_all('input')]

            ans_labels = [label for label in child.select("label.field-label")]
            corrects = [label['for'] for label in ans_labels if "choicegroup_correct" in label.get('class', '')]
            if ids:
                ensure_ids_same(ids)
                correct_answers = [extract_choice_from_id(ans)[1]  for ans in corrects]
                if len(correct_answers) > 1:
                    correct_answer = correct_answers
                elif len(correct_answers) == 1:
                    correct_answer = correct_answers[0]
                else:
                    correct_answer = None
                quest_id, choice_id = extract_choice_from_id(ids[0])

                return ChoiceQuestion(id=quest_id, text=problem_text, options=qs, ids=ids, correct_answer=correct_answer)


def plural_choice(answer: list, ids: list[str], options: list[str]) -> tuple[str, str | list[str]]:
    choices = []
    for ans in answer:
        try:
            index = options.index(ans)
        except ValueError:
            index = get_similar_index(ans, options)
            if index is None:
                raise NoSolutionFoundError(f"'{ans}' was not a present option: {options}")
        ans_input_id = ids[index]
        quest_id, choice_id = extract_choice_from_id(ans_input_id)
        choices.append(choice_id)
    quest_id += "[]"
    return quest_id, choices


def singular_choice(answer: str, ids: list[str], options: list[str]) -> tuple[str, str | list[str]]:
    if answer in options:
        index = options.index(answer)
        ans_input_id = ids[index]
        quest_id, choice_id = extract_choice_from_id(ans_input_id)

        return quest_id, choice_id
    else:
        index = get_similar_index(answer, options)
        if index is None:
            raise NoSolutionFoundError(f"'{answer}' is not in options {options}")

    ans_input_id = ids[index]
    quest_id, choice_id = extract_choice_from_id(ans_input_id)

    return quest_id, choice_id
