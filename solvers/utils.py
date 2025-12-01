import re

from errors import NoSolutionFoundError
from fuzzywuzzy import fuzz

def extract_choice_from_id(choid_id: str):
    r = re.search(r"(input_[\w\d]+_\d+_\d+)_(choice_\d+)", choid_id)
    return r.group(1), r.group(2)


def get_ans_id(answers: list[tuple[str, str]], answer: str):
    for ans, aid in answers:
        ans = re.sub(r"\s+", ' ', ans)
        if answer == ans:
            return aid
    raise NoSolutionFoundError(f"'{answer}' was not present in options {answers}")


def get_similar_index(ans: str, options: list[str]):
    for i, opt in enumerate(options):
        if len(opt) == len(ans):
            ratio = fuzz.ratio(opt, ans)

            similar_characters = len(opt) * ratio / 100
            if similar_characters >= len(ans) - 1:
                return i
        else:
            threshold = 90

            if max(len(opt), len(ans)) <= 7:
                threshold = 85

            if fuzz.ratio(opt, ans) > threshold:
                return i


def lookup_option_id_in_columns(answer, option_columns: list[list[tuple[str, str]]]):
    for col in option_columns:
        for option, opt_id in col:
            if option == answer:
                return opt_id
