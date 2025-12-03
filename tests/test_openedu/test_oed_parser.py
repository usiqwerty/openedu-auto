import json
import os

import pytest
from bs4 import BeautifulSoup

from errors import FormatError
from openedu.oed_parser import OpenEduParser, VerticalBlock
from tests.fakes import DummyDescriber


@pytest.mark.parametrize('inp', ['sequential'])
def test_parse_sequential_block(inp):
    parser = OpenEduParser(None)
    with open(os.path.join('tests', 'data', 'blocks', inp + ".json"), encoding='utf-8') as f:
        seq = json.load(f)
    with open(os.path.join('tests', 'data', 'blocks', inp + ".exp.json"), encoding='utf-8') as f:
        exp = json.load(f)

    assert list(parser.parse_sequential_block_(seq)) == [VerticalBlock(**x) for x in exp]


@pytest.mark.parametrize(
    "testname",
    ["test", "free_match_whole_page", "multiple_questions_in_prob", "new_mt_and_fill", "outer_question_text",
     "i_dont_know", "with_video", "map_problem", "problem_crossword", "problem_match_multicolumn", "many_different_things"]
)
def test_parse_vertical_block_html(testname: str):
    filename_input = f"tests/data/pages/{testname}.html"
    filename_result = f"tests/data/pages/{testname}.json"
    with open(filename_input, encoding='utf-8') as f:
        html = f.read()

    with open(filename_result, encoding='utf-8') as f:
        expected = json.load(f)

    parser = OpenEduParser(DummyDescriber())
    problems_got = parser.parse_vertical_block_html(html)
    assert [[json.loads(q.json()) for q in prob] for prob in problems_got] == expected


@pytest.mark.parametrize("testname",
                         ["problem_choice_single", "problem_choice_multiple", "problem_match", "problem_fixed_match"])
def test_parse_problem(testname):
    filename_input = f"tests/data/problems/{testname}.html"
    filename_result = f"tests/data/problems/{testname}.json"

    with open(filename_input, encoding='utf-8') as f:
        html = f.read()

    with open(filename_result, encoding='utf-8') as f:
        expected = json.load(f)

    parser = OpenEduParser(DummyDescriber())
    assert [json.loads(x.json()) for x in parser.parse_problem(BeautifulSoup(html, "html.parser"))] == expected


def test_parse_choice_different_ids():
    filename_input = f"tests/data/problems/problem_choice_diff_ids.html"
    with open(filename_input, encoding='utf-8') as f:
        html = f.read()

    parser = OpenEduParser(DummyDescriber())

    with pytest.raises(FormatError):
        parser.parse_problem(BeautifulSoup(html, "html.parser"))
