import re


def extract_choice_from_id(choid_id: str):
    r = re.search(r"(input_[\w\d]+_\d+_\d+)_(choice_\d+)", choid_id)
    return r.group(1), r.group(2)


def compose_answer(answer: list[str] | str, ids: list[str], options: list[str]):
    if isinstance(answer, str):
        return singular_answer(answer, ids, options)
    else:
        return plural_answer(answer, ids, options)


def get_ans_id(answers: list[tuple[str, str]], answer: str):
    for ans, aid in answers:
        if answer == ans:
            return aid


def compose_match(answers: list[str], fields: list[tuple[str, str]], options: list[tuple[str, str]], quest_id: str):
    choices = {}
    # {"a1": [], "a2": [], "a3": [], "a4": [], "a5": ["b1"]}
    for field, ans in zip(fields, answers):
        field_name, field_id = field
        choices[field_id] = [get_ans_id(options, ans)]
    return quest_id, str({"answer": choices}).replace("'", '"')


def plural_answer(answer: list, ids: list[str], options: list[str]) -> tuple[str, str | list[str]]:
    choices = []
    for ans in answer:
        index = options.index(ans)
        ans_input_id = ids[index]
        quest_id, choice_id = extract_choice_from_id(ans_input_id)
        choices.append(choice_id)
    quest_id += "[]"
    return quest_id, choices


def singular_answer(answer: str, ids: list[str], options: list[str]) -> tuple[str, str | list[str]]:
    if answer in options:
        index = options.index(answer)
        ans_input_id = ids[index]
        quest_id, choice_id = extract_choice_from_id(ans_input_id)

        return quest_id, choice_id
    else:
        raise KeyError(f"'{answer}' is not in options {options}")
        quest_id = ids[0]
        return quest_id, answer
