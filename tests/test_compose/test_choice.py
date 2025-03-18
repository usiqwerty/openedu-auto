import pytest

from errors import NoSolutionFoundError
from openedu.questions.choice import ChoiceQuestion


def test_success_single():
    ans = "second"
    options = ["first", "second"]
    ids = ["input_bibaboba_0_1_choice_0", "input_bibaboba_0_1_choice_1"]
    q = ChoiceQuestion(text="", options=options, ids=ids)
    assert q.compose(ans) == ("input_bibaboba_0_1", "choice_1")


def test_no_solution_single():
    ans = "third"
    options = ["first", "second"]
    ids = ["input_bibaboba_0_1_choice_0", "input_bibaboba_0_1_choice_1"]
    q = ChoiceQuestion(text="", options=options, ids=ids)
    with pytest.raises(NoSolutionFoundError):
        q.compose(ans)


def test_success_multiple():
    ans = ["second", "third"]
    options = ["first", "second", "third"]
    ids = ["input_bibaboba_0_1_choice_0", "input_bibaboba_0_1_choice_1", "input_bibaboba_0_1_choice_2"]
    q = ChoiceQuestion(text="", options=options, ids=ids)
    assert q.compose(ans) == ("input_bibaboba_0_1[]", ["choice_1", "choice_2"])


def test_no_solution_multiple():
    ans = ["third", "fourth"]
    options = ["first", "second", "third"]
    ids = ["input_bibaboba_0_1_choice_0", "input_bibaboba_0_1_choice_1", "input_bibaboba_0_1_choice_2"]
    q = ChoiceQuestion(text="", options=options, ids=ids)
    with pytest.raises(NoSolutionFoundError):
        q.compose(ans)
