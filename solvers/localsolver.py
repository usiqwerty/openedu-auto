import csv

from fuzzywuzzy import process

from openedu.questions.choice import compose_choice

answers: list[list[str, str]] = []

start = 210
with open("../userdata/Filosofia.csv", encoding='utf-8') as f:
    rd = csv.reader(f, delimiter=';', quotechar='"')
    for row in list(rd)[start:]:
        answers.append(row)


def pick_answer(question, options) -> list | str:
    only_qs = list(map(lambda x: x[0], answers))
    known_question, _ = process.extractOne(question, only_qs)
    idx = only_qs.index(known_question)
    known_answer = answers[idx][1]

    if not options:
        return known_answer
    if '\n' in known_answer:
        real_answer = []
        for known_subanswer in known_answer.split('\n'):
            real_answer.append(process.extractOne(known_subanswer, options)[0])
    else:
        real_answer = process.extractOne(known_answer, options)[0]
    return real_answer


def solve(question: str, options: list[str], ids: list[str]) -> tuple[str, str | list[str]]:
    answer = pick_answer(question, options)
    return compose_choice(answer, ids, options)


