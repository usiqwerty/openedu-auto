import pytest

from openedu.questions.choice import ChoiceQuestion
from solvers.mistral_solver import MistralSolver

d1 = {
    "type": "choice",
    "text": "Выберите все правильные варианты ответа\nОсновные теории исторического процесса, получившие распространение в науке XX – начала XXI вв. – это…",
    "options": [
        "Формационная",
        "Религиозная",
        "Цивилизационная",
        "Модернизационная",
        "Классовая",
        "Эволюционная"
    ],
    "ids": [
        "input_03c8e6629b074732fde5_2_1_choice_0",
        "input_03c8e6629b074732fde5_2_1_choice_1",
        "input_03c8e6629b074732fde5_2_1_choice_2",
        "input_03c8e6629b074732fde5_2_1_choice_3",
        "input_03c8e6629b074732fde5_2_1_choice_4",
        "input_03c8e6629b074732fde5_2_1_choice_5"
    ]
}

d2 = {
    "type": "choice",
    "text": "Укажите три разновидности письменных исторических источников, относящихся к категории частных (личного происхождения)",
    "options": [
        "законодательные акты",
        "дневники",
        "письма",
        "периодическая печать",
        "мемуары",
        "статистика"
    ],
    "ids": [
        "input_e5321b891f47fdaf61c0_2_1_choice_0",
        "input_e5321b891f47fdaf61c0_2_1_choice_1",
        "input_e5321b891f47fdaf61c0_2_1_choice_2",
        "input_e5321b891f47fdaf61c0_2_1_choice_3",
        "input_e5321b891f47fdaf61c0_2_1_choice_4",
        "input_e5321b891f47fdaf61c0_2_1_choice_5"
    ]
}


@pytest.mark.skip("Might do a web request")
@pytest.mark.parametrize(["data", "correct"], [
    (d1, {'input_03c8e6629b074732fde5_2_1': ['choice_0', 'choice_2', 'choice_3']}),
    (d2, {"input_e5321b891f47fdaf61c0_2_1[]": ["choice_1","choice_2","choice_4"]})
])
def test_for_correct_solution(data, correct):
    q = ChoiceQuestion(**data)
    slv = MistralSolver()
    k, v = slv.solve(q)

    assert {k: v} == correct
