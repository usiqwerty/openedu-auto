import json

import pytest
import responses

from autosolver import OpenEduAutoSolver
from openedu.local_api_storage import DummyApiStorage
from tests.fakes import DummySolver, DummyDescriber

test_course = "test_course"
test_seq = '123'
test_vert = '987'
with open("tests/data/full/outline.json", encoding='utf-8') as f:
    outline = json.load(f)
with open("tests/data/full/course_meta.json", encoding='utf-8') as f:
    course_meta = json.load(f)
with open("tests/data/full/seq.json", encoding='utf-8') as f:
    seq = json.load(f)
with open("tests/data/full/problem_check.json", encoding='utf-8') as f:
    probcheck = json.load(f)
responses.post(
    url="https://courses.openedu.ru/login_refresh",
)
responses.get(
    url=f"https://courses.openedu.ru/api/course_home/course_metadata/course-v1:{test_course}",
    json=course_meta
)
responses.get(
    url=f'https://courses.openedu.ru/api/course_home/outline/course-v1:{test_course}',
    json=outline
)
for vert in ["987", "876", "765", "654", "543", "432"]:
    responses.post(
        url=f'https://courses.openedu.ru/courses/course-v1:test_course/xblock/block-v1:{test_course}+type@html+block@{vert}/handler/publish_completion'
    )

responses.get(
    url=f'https://courses.openedu.ru/api/courseware/sequence/block-v1:{test_course}+type@sequential+block@{test_seq}',
    json=seq
)


@pytest.fixture
def testing_solver():
    solver = DummySolver()
    describer = DummyDescriber()
    aslv = OpenEduAutoSolver(solver, describer)
    aslv.app.api.api_storage = DummyApiStorage()

    return aslv


@pytest.fixture
def problem_check_template():
    return probcheck


@responses.activate
def test_auto_solve(testing_solver, problem_check_template):
    problem_check_response = problem_check_template
    problem_check_response['current_score'] = 10
    responses.post(
        url="https://courses.openedu.ru/courses/course-v1:test_course/xblock/block-v1:test_course+type@problem+block@test_problem/handler/xmodule_handler/problem_check",
        json=problem_check_response,

    )
    with open("tests/data/full/with_video.html", encoding='utf-8') as f:
        content = f.read()
    responses.get(
        url=f"https://courses.openedu.ru/xblock/block-v1:{test_course}+type@vertical+block@{test_vert}",
        body=content
    )

    testing_solver.process_course(test_course)


@responses.activate
def test_auto_solve_wrong_answer(testing_solver, problem_check_template):
    problem_check_response = problem_check_template
    problem_check_response['current_score'] = 9

    responses.post(
        url="https://courses.openedu.ru/courses/course-v1:test_course/xblock/block-v1:test_course+type@problem+block@test_problem/handler/xmodule_handler/problem_check",
        json=problem_check_response,

    )
    with open("tests/data/full/with_video.html", encoding='utf-8') as f:
        content = f.read()
    responses.get(
        url=f"https://courses.openedu.ru/xblock/block-v1:{test_course}+type@vertical+block@{test_vert}",
        body=content
    )

    testing_solver.process_course(test_course)
