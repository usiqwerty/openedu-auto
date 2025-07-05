import urllib.parse

import pytest
import responses
from requests import PreparedRequest

from autosolver import OpenEduAutoSolver
from tests.functional.common import register_api_endpoints, empty_auto_solver

with open('tests/data/full/home.html', encoding='utf-8') as f:
    home = f.read()
with open('tests/data/full/login.html', encoding='utf-8') as f:
    login = f.read()

test_username = "user"
test_password = "pass"
login_redir_url = 'https://sso.openedu.ru/realms/openedu/protocol/openid-connect/auth?client_id=plp&redirect_uri=https://openedu.ru/complete/npoedsso/&state=73SRwU4YHyFcSgFgb13mM9CSaWO2KA78&response_type=code&nonce=x5QFpzMqsXzosnAMsCZQ4Nt9iJrzRmONbJudhCYXQxnmOlVFcpopNDWkxHQCJBT0&scope=openid+profile+email'
complete_npoedsso = 'https://openedu.ru/complete/npoedsso/?state=73SRwU4YHyFcSgFgb13mM9CSaWO2KA78&session_state=daf7eaef-08f4-49e3-b996-433b186448de&code=803f064e-1f6d-4dfc-9afb-e0eb02c9fcb8.daf7eaef-08f4-49e3-b996-433b186448de.a8bac7c8-08f0-4ab2-b194-a6f565c61399'
login_action_url = "https://sso.openedu.ru/realms/openedu/login-actions/authenticate?session_code=4XNotAkKMzm4z46VKDQWKisem1PHPlZZs3n7QJqLT5M&execution=268f8c1b-34e5-4303-9ca7-f655361ae590&client_id=plp&tab_id=5VMoPD1aJZc"


def test_empty_logged_out(empty_auto_solver):
    register_api_endpoints()
    empty_auto_solver: OpenEduAutoSolver
    assert len(empty_auto_solver.app.api.session.cookies) == 0, "Empty aslv claims to be logged in"


def respond_login_data(req: PreparedRequest):
    request_json = urllib.parse.parse_qs(req.body)

    if request_json['username'] == [test_username] and request_json['password'] == [test_password]:
        return 302, {'location': complete_npoedsso}, None
    else:
        # in fact, it should be login page with error message,
        # but it should work this way as well, i think
        return 200, {}, login


@pytest.mark.parametrize("correct", [True, False], ids=['correct password', 'incorrect password'])
@responses.activate
def test_login(empty_auto_solver, correct: bool):
    responses.get("https://openedu.ru/", body=home)

    responses.get("https://openedu.ru/login/npoedsso/?next=%2F", status=302, headers={'location': login_redir_url})
    responses.get(login_redir_url, body=login)

    responses.add_callback(
        "POST",
        login_action_url,
        respond_login_data
    )
    responses.get(
        "https://openedu.ru/complete/npoedsso/?state=73SRwU4YHyFcSgFgb13mM9CSaWO2KA78&session_state=daf7eaef-08f4-49e3-b996-433b186448de&code=803f064e-1f6d-4dfc-9afb-e0eb02c9fcb8.daf7eaef-08f4-49e3-b996-433b186448de.a8bac7c8-08f0-4ab2-b194-a6f565c61399",
        status=302,
        headers={'location': "/"}
    )
    responses.get("https://openedu.ru/auth/status?url=/", json={"auth": int(correct)})
    empty_auto_solver: OpenEduAutoSolver

    if correct:
        status = empty_auto_solver.app.login(test_username, test_password)
    else:
        status = empty_auto_solver.app.login(test_username, test_password[::-1])
    assert bool(status.get("auth")) == correct

    responses.assert_call_count("https://openedu.ru/auth/status?url=/", 1)
    responses.assert_call_count("https://openedu.ru/login/npoedsso/?next=%2F", 1)
    responses.assert_call_count(login_redir_url, 1)
    responses.assert_call_count(login_action_url, 1)
