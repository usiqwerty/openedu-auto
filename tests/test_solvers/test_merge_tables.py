import json

from src.solvers.consensus import merge_tables


def test_basic_merge():
    a = 'aboba', json.dumps({'answer': {"a": "b", "c": "d"}})
    b = 'aboba', json.dumps({'answer': {"a": "b", "c": "e"}})
    c = 'aboba', json.dumps({'answer': {"a": "f", "c": "d"}})
    r = merge_tables([a, b, c])
    assert r == a

def test_no_result():
    a = 'aboba', json.dumps({'answer': {}})
    r = merge_tables([a])
    assert r == a
