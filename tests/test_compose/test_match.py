import pytest

from errors import NoSolutionFoundError
from openedu.questions.fixed_match import FixedMatchQuestion


def test_success():
    fields = [
        ("first_field", ["a1"]),
        ("second_field", ["a2"]),
    ]
    options = [
        ("first_option", "b1"),
        ("second_option", "b2"),
        ("third_option", "b3"),
    ]
    headers = ['h1', 'h2']
    ans = ["first_option", "third_option"]
    qid = "asod"
    should = {'answer': {"a1": ["b1"], "a2": ["b3"]}}
    q = FixedMatchQuestion(text="", id=qid, options=options, fields=fields, headers=headers)
    assert q.compose(ans) == (qid, str(should).replace("'", '"'))


def test_no_solution():
    fields = [
        ("first_field", ["a1"]),
        ("second_field", ["a2"]),
    ]
    options = [
        ("first_option", "b1"),
        ("second_option", "b2"),
        ("third_option", "b3"),
    ]
    headers = ['h1', 'h2']
    ans = ["first_option", "fourth_option"]
    qid = "question id"
    q = FixedMatchQuestion(text="", id=qid, options=options, fields=fields, headers=headers)
    with pytest.raises(NoSolutionFoundError):
        q.compose(ans)


def test_success_multicol():
    fields = [
        ("first_field", ["a1", "a3"]),
        ("second_field", ["a2", "a4"]),
    ]
    options = [
        ("first_option", "b1"),
        ("second_option", "b2"),
        ("third_option", "b3"),
        ("fourth_option", "b4"),
        ("fifth_option", "b5"),
        ("sixth_option", "b6"),
        ("seventh_option", "b7"),
    ]
    headers = ['h1', 'h2', 'h3']
    ans = ["first_option", "third_option", "seventh_option", "fifth_option"]
    qid = "asod"
    should = {'answer': {"a1": ["b1"], "a2": ["b3"], "a3":['b7'], 'a4':['b5']}}
    q = FixedMatchQuestion(text="", id=qid, options=options, fields=fields, headers=headers)
    assert q.compose(ans) == (qid, str(should).replace("'", '"'))


def test_no_solution_multicol():
    fields = [
        ("first_field", ["a1", "a3"]),
        ("second_field", ["a2", "a4"]),
    ]
    options = [
        ("first_option", "b1"),
        ("second_option", "b2"),
        ("third_option", "b3"),
        ("fourth_option", "b4"),
        ("fifth_option", "b5"),
        ("sixth_option", "b6"),
        ("seventh_option", "b7"),
    ]
    headers = ['h1', 'h2', 'h3']
    ans = ["first_option", "third_option", "tenth_option", "fifth_option"]
    qid = "question id"
    q = FixedMatchQuestion(text="", id=qid, options=options, fields=fields, headers=headers)
    with pytest.raises(NoSolutionFoundError):
        q.compose(ans)

def test_multicol_short_answer():
    fields = [
        ("first_field", ["a1", "a3"]),
        ("second_field", ["a2", "a4"]),
    ]
    options = [
        ("first_option", "b1"),
        ("second_option", "b2"),
        ("third_option", "b3"),
        ("fourth_option", "b4"),
        ("fifth_option", "b5"),
        ("sixth_option", "b6"),
        ("seventh_option", "b7"),
    ]
    headers = ['h1', 'h2', 'h3']
    ans = ["first_option", "third_option"]
    qid = "asod"
    should = {'answer': {"a1": ["b1"], "a2": ["b3"], "a3":['b7'], 'a4':['b5']}}
    q = FixedMatchQuestion(text="", id=qid, options=options, fields=fields, headers=headers)
    with pytest.raises(NoSolutionFoundError):
        q.compose(ans)
