import pytest

from solvers.utils import extract_choice_from_id
from openedu.questions.choice import ChoiceQuestion


@pytest.mark.parametrize(["answer", "ids", "options", "expected"],
                         [
                             ("археология",
                              [f'input_e0fe1d42a264ff27ca9c_2_1_choice_{i}' for i in [3, 1, 2, 0]],
                              ["этнопсихология", "археология", "палеозоология", "палеонтология"],
                              ("input_e0fe1d42a264ff27ca9c_2_1", "choice_1"))
                         ], ids=["Single choice"])
def test_compose_answer(answer, ids, options, expected):
    q=ChoiceQuestion(text="", ids=ids, options=options)
    assert q.compose(answer) == expected


def test_extract_choice_from_id():
    assert extract_choice_from_id("input_e0fe1d42a264ff27ca9c_2_1_choice_2") == ("input_e0fe1d42a264ff27ca9c_2_1", "choice_2")
