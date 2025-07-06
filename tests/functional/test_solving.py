import pytest
import responses

from errors import WrongAnswer
from tests.functional.common import test_course, problem_check, register_api_endpoints, empty_auto_solver, \
    assert_calls_counts_except_login


@pytest.fixture
def problem_check_result():
    return problem_check.copy()


@pytest.fixture
def problem_check_bad_result():
    r = problem_check.copy()
    r['current_score'] = 5
    return r


@responses.activate
def test_solve_correct_answer(empty_auto_solver, problem_check_result):
    register_api_endpoints()
    responses.post(
        f"https://courses.openedu.ru/courses/course-v1:{test_course}/xblock/block-v1:{test_course}+type@problem+block@test_problem/handler/xmodule_handler/problem_check",
        json=problem_check_result
    )
    empty_auto_solver.app.inject_csrf('thetoken')
    empty_auto_solver.process_course(test_course)
    assert_calls_counts_except_login(1)


@responses.activate
def test_solve_wrong_answer(empty_auto_solver, problem_check_bad_result):
    register_api_endpoints()
    responses.post(
        f"https://courses.openedu.ru/courses/course-v1:{test_course}/xblock/block-v1:{test_course}+type@problem+block@test_problem/handler/xmodule_handler/problem_check",
        json=problem_check_bad_result
    )
    empty_auto_solver.app.inject_csrf('thetoken')
    with pytest.raises(WrongAnswer):
        empty_auto_solver.process_course(test_course)
    assert_calls_counts_except_login(1)
