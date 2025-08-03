import pytest

from errors import NoSolutionFoundError
from openedu.questions.fixed_match import FixedMatchQuestion


def test_success():
    fields = [
        ("first_field", "a1"),
        ("second_field", "a2"),
    ]
    options = [
        ("first_option", "b1"),
        ("second_option", "b2"),
        ("third_option", "b3"),
    ]
    ans = ["first_option", "third_option"]
    qid = "asod"
    should = {'answer': {"a1": ["b1"], "a2": ["b3"]}}
    q = FixedMatchQuestion(text="", id=qid, options=options, fields=fields)
    assert q.compose(ans) == (qid, str(should).replace("'", '"'))


def test_no_solution():
    fields = [
        ("first_field", "a1"),
        ("second_field", "a2"),
    ]
    options = [
        ("first_option", "b1"),
        ("second_option", "b2"),
        ("third_option", "b3"),
    ]
    ans = ["first_option", "fourth_option"]
    qid = "question id"
    q = FixedMatchQuestion(text="", id=qid, options=options, fields=fields)
    with pytest.raises(NoSolutionFoundError):
        q.compose(ans)
