import json

import pytest

from errors import NoSolutionFoundError
from openedu.questions.abstract_match import CellData
from openedu.questions.fixed_match import FixedMatchQuestion


def test_success():
    options = [
        ("first_option", "b1"),
        ("second_option", "b2"),
        ("third_option", "b3"),
    ]
    ans = [
        ["h1", "h2"],
        ["first_field", ["first_option"]],
        ["second_field", ["third_option"]],
    ]
    qid = "asod"
    should = {'answer': {"a1": ["b1"], "a2": ["b3"]}}
    table = [
        [CellData(id=None, value='h1'), CellData(id=None, value='h2')],
        [CellData(value="first_field"), CellData(id='a1')],
        [CellData(value="second_field"), CellData(id='a2')]
    ]
    q = FixedMatchQuestion(text="", id=qid, options=options, table=table)
    assert q.compose(ans) == (qid, json.dumps(should, sort_keys=True))


def test_no_solution():
    options = [
        ("first_option", "b1"),
        ("second_option", "b2"),
        ("third_option", "b3"),
    ]
    ans = [
        ["h1", "h2"],
        ["first_field", ["first_option"]],
        ["second_field", ["fourth_option"]],
    ]
    qid = "question id"
    table = [
        [CellData(id=None, value='h1'), CellData(id=None, value='h2')],
        [CellData(value="first_field"), CellData(id='a1')],
        [CellData(value="second_field"), CellData(id='a2')]
    ]
    q = FixedMatchQuestion(text="", id=qid, options=options, table=table)
    with pytest.raises(NoSolutionFoundError):
        q.compose(ans)


def test_success_multicol():
    options = [
        ("first_option", "b1"),
        ("second_option", "b2"),
        ("third_option", "b3"),
        ("fourth_option", "b4"),
        ("fifth_option", "b5"),
        ("sixth_option", "b6"),
        ("seventh_option", "b7"),
    ]
    ans = [
        ["h1", "h2", "h2"],
        ["first_field", ["first_option"], ["seventh_option"]],
        ["second_field", ["third_option"], ["fifth_option"]],
    ]
    qid = "asod"
    table = [
        [CellData(value='h1'), CellData(value='h2'), CellData(value='h3')],
        [CellData(value="first_field"), CellData(id='a1'), CellData(id='a3')],
        [CellData(value="second_field"), CellData(id='a2'), CellData(id='a4')]
    ]
    should = {'answer': {"a1": ["b1"], "a2": ["b3"], "a3": ['b7'], 'a4': ['b5']}}
    q = FixedMatchQuestion(text="", id=qid, options=options, table=table)
    assert q.compose(ans) == (qid, json.dumps(should, sort_keys=True))


def test_no_solution_multicol():
    options = [
        ("first_option", "b1"),
        ("second_option", "b2"),
        ("third_option", "b3"),
        ("fourth_option", "b4"),
        ("fifth_option", "b5"),
        ("sixth_option", "b6"),
        ("seventh_option", "b7"),
    ]
    ans = [
        ["h1", "h2", "h2"],
        ["first_field", ["first_option"], ["tenth_option"]],
        ["second_field", ["third_option"], ["fifth_option"]],
    ]
    qid = "question id"
    table = [
        [CellData(value='h1'), CellData(value='h2'), CellData(value='h3')],
        [CellData(value="first_field"), CellData(id='a1'), CellData(id='a3')],
        [CellData(value="second_field"), CellData(id='a2'), CellData(id='a4')]
    ]
    q = FixedMatchQuestion(text="", id=qid, options=options, table=table)
    with pytest.raises(NoSolutionFoundError):
        q.compose(ans)


def test_multicol_short_answer():
    options = [
        ("first_option", "b1"),
        ("second_option", "b2"),
        ("third_option", "b3"),
        ("fourth_option", "b4"),
        ("fifth_option", "b5"),
        ("sixth_option", "b6"),
        ("seventh_option", "b7"),
    ]
    ans = [
        ["h1", "h2", "h2"],
        ["first_field", ["first_option"], ["tenth_option"]],
    ]
    qid = "asod"
    should = {'answer': {"a1": ["b1"], "a2": ["b3"], "a3": ['b7'], 'a4': ['b5']}}
    table = [
        [CellData(value='h1'), CellData(value='h2'), CellData(value='h3')],
        [CellData(value="first_field"), CellData(id='a1'), CellData(id='a3')],
        [CellData(value="second_field"), CellData(id='a2'), CellData(id='a4')]
    ]
    q = FixedMatchQuestion(text="", id=qid, options=options, table=table)
    with pytest.raises(NoSolutionFoundError):
        q.compose(ans)
