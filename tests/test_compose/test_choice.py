import pytest

from errors import NoSolutionFoundError, FormatError
from solvers.utils import compose_choice


def test_success_single():
    ans = "second"
    options = ["first", "second"]
    ids = ["input_bibaboba_0_1_choice_0", "input_bibaboba_0_1_choice_1"]
    assert compose_choice(ans, ids, options) == ("input_bibaboba_0_1", "choice_1")


def test_no_solution_single():
    ans = "third"
    options = ["first", "second"]
    ids = ["input_bibaboba_0_1_choice_0", "input_bibaboba_0_1_choice_1"]
    with pytest.raises(NoSolutionFoundError):
        compose_choice(ans, ids, options)


def test_success_multiple():
    ans = ["second", "third"]
    options = ["first", "second", "third"]
    ids = ["input_bibaboba_0_1_choice_0", "input_bibaboba_0_1_choice_1", "input_bibaboba_0_1_choice_2"]
    assert compose_choice(ans, ids, options) == ("input_bibaboba_0_1[]", ["choice_1", "choice_2"])


def test_no_solution_multiple():
    ans = ["third", "fourth"]
    options = ["first", "second", "third"]
    ids = ["input_bibaboba_0_1_choice_0", "input_bibaboba_0_1_choice_1", "input_bibaboba_0_1_choice_2"]
    with pytest.raises(NoSolutionFoundError):
        compose_choice(ans, ids, options)
