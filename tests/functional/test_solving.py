import pytest
import responses

from errors import WrongAnswer, ReloginReceived
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


with open('tests/data/full/login.html', encoding='utf-8') as f:
    login_page_html = f.read()


@responses.activate
def test_solve_correct_answer(empty_auto_solver, problem_check_result):
    register_api_endpoints()
    responses.get('https://openedu.ru/auth/status?url=/', json={'auth': 1})
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
    responses.get('https://openedu.ru/auth/status?url=/', json={'auth': 1})
    responses.post(
        f"https://courses.openedu.ru/courses/course-v1:{test_course}/xblock/block-v1:{test_course}+type@problem+block@test_problem/handler/xmodule_handler/problem_check",
        json=problem_check_bad_result
    )
    empty_auto_solver.app.inject_csrf('thetoken')
    with pytest.raises(WrongAnswer):
        empty_auto_solver.process_course(test_course)
    assert_calls_counts_except_login(1)


@responses.activate
def test_solve_with_relogin_received(empty_auto_solver, problem_check_bad_result):
    register_api_endpoints()
    responses.get('https://openedu.ru/auth/status?url=/', json={'auth': 0})
    responses.replace(
        responses.POST,
        "https://courses.openedu.ru/login_refresh", status=401, body='"Unauthorized"'
    )
    responses.get(
        "https://courses.openedu.ru/auth/login/keycloak/",
        status=302,
        headers={'location':'https://sso.openedu.ru/realms/openedu/protocol/openid-connect/auth?client_id=edx&redirect_uri=https://courses.openedu.ru/auth/complete/keycloak/&state=QQ1jV9mqcRjL4mDHjhGTga467JHBN8i1&response_type=code&nonce=mKSFfzFxtBsEyTrqYgixlER817j3AzUI19cRDDzCxaWatBMPhuNmtRSZc7qs3BDl&scope=openid+profile+email'}
    )
    responses.get(
        "https://sso.openedu.ru/realms/openedu/protocol/openid-connect/auth",
        body=login_page_html
    )

    empty_auto_solver.app.inject_csrf('thetoken')
    with pytest.raises(ReloginReceived):
        empty_auto_solver.process_course(test_course)
