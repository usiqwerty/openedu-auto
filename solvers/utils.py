import re

from errors import NoSolutionFoundError
from openedu.questions.freematch import FreeMatchQuestion
from openedu.questions.select import SelectQuestion


def extract_choice_from_id(choid_id: str):
    r = re.search(r"(input_[\w\d]+_\d+_\d+)_(choice_\d+)", choid_id)
    return r.group(1), r.group(2)


def compose_choice(answer: list[str] | str, ids: list[str], options: list[str]):
    if isinstance(answer, str):
        return singular_choice(answer, ids, options)
    else:
        return plural_choice(answer, ids, options)


def get_ans_id(answers: list[tuple[str, str]], answer: str):
    for ans, aid in answers:
        if answer == ans:
            return aid
    raise NoSolutionFoundError(f"'{answer}' was not present in options {answers}")

def compose_match(answers: list[str], fields: list[tuple[str, str]], options: list[tuple[str, str]], quest_id: str):
    choices = {}
    # {"a1": [], "a2": [], "a3": [], "a4": [], "a5": ["b1"]}
    for field, ans in zip(fields, answers):
        field_name, field_id = field
        choices[field_id] = [get_ans_id(options, ans)]
    return quest_id, str({"answer": choices}).replace("'", '"')


def plural_choice(answer: list, ids: list[str], options: list[str]) -> tuple[str, str | list[str]]:
    choices = []
    for ans in answer:
        try:
            index = options.index(ans)
        except ValueError:
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
        raise NoSolutionFoundError(f"'{answer}' is not in options {options}")
        quest_id = ids[0]
        return quest_id, answer


def lookup_option_id_in_columns(answer, option_columns: list[list[tuple[str, str]]]):
    for col in option_columns:
        for option, opt_id in col:
            if option == answer:
                return opt_id


def compose_freematch(flat_answers: list[str], question: FreeMatchQuestion):
    col_num = 2
    answer = {}

    for i in range(0, len(flat_answers), col_num):
        row_ = i // col_num
        for col in range(col_num):
            row_key = question.field_columns[col][row_]
            ans_id = lookup_option_id_in_columns(flat_answers[i + col], question.option_columns)
            if ans_id is None:
                raise NoSolutionFoundError(f"Answer {flat_answers} does not solve {question!r}")
            answer[row_key] = [ans_id]

    return question.id, str({'answer': answer})


def compose_select(answer: str, question: SelectQuestion):
    return question.id, answer.strip()
