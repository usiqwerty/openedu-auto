import json
import os

import pytest
from bs4 import BeautifulSoup

from openedu.oed_parser import OpenEduParser, VerticalBlock, parse_problem


@pytest.mark.parametrize('inp', ['sequential'])
def test_parse_sequential_block(inp):
    parser = OpenEduParser()
    with open(os.path.join('tests', 'data', 'blocks', inp + ".json"), encoding='utf-8') as f:
        seq = json.load(f)
    with open(os.path.join('tests', 'data', 'blocks', inp + ".exp.json"), encoding='utf-8') as f:
        exp = json.load(f)

    assert list(parser.parse_sequential_block_(seq)) == [VerticalBlock(**x) for x in exp]


@pytest.mark.parametrize(
    "testname",
    ["test", "free_match_whole_page", "multiple_questions_in_prob"]
)
def test_parse_vertical_block_html(testname: str):
    filename_input = f"tests/data/pages/{testname}.html"
    filename_result = f"tests/data/pages/{testname}.json"
    # TODO: use utf-8
    if testname != 'multiple_questions_in_prob':
        enc = 'cp1251'
    else:
        enc='utf-8'
    with open(filename_input, encoding=enc) as f:
        html = f.read()

    with open(filename_result, encoding='utf-8') as f:
        expected = json.load(f)

    parser = OpenEduParser()
    problems_got = parser.parse_vertical_block_html(html)
    assert [[json.loads(q.json())for q in prob] for prob in problems_got] == expected


@pytest.mark.parametrize("testname", ["problem_choice_single", "problem_choice_multiple", "problem_match"])
def test_parse_problem(testname):
    filename_input = f"tests/data/{testname}.html"
    filename_result = f"tests/data/{testname}.json"
    with open(filename_input, encoding='utf-8') as f:
        html = f.read()

    with open(filename_result, encoding='utf-8') as f:
        expected = json.load(f)
    assert [json.loads(x.json()) for x in parse_problem(BeautifulSoup(html, "html.parser"))] == expected
