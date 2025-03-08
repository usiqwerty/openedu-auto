import pytest

from errors import NoSolutionFoundError
from solvers.utils import compose_match


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
    assert compose_match(ans, fields, options, qid) == (qid, str(should).replace("'", '"'))


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
    with pytest.raises(NoSolutionFoundError):
        compose_match(ans, fields, options, qid)
