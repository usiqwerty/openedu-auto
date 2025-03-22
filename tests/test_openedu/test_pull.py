import json

import pytest

from openedu.oed_parser import OpenEduParser
from tests.fakes import DummyDescriber


@pytest.mark.parametrize("testname", ["pull_choice_both", "pull_fill", "pull_new_mt", "pull_freematch", "pull_select", "pull_match"])
def test_choice_both(testname):
    filename_input = f"tests/data/pull/{testname}.html"
    filename_result = f"tests/data/pull/{testname}.json"

    with open(filename_input, encoding='utf-8') as f:
        html = f.read()

    with open(filename_result, encoding='utf-8') as f:
        expected = json.load(f)

    parser = OpenEduParser(DummyDescriber())
    problems_got = parser.parse_vertical_block_html(html)
    assert [[json.loads(q.json())for q in prob] for prob in problems_got] == expected
