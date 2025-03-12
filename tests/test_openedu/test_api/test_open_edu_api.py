import os

from openedu.api import OpenEduAPI
from openedu.auth import OpenEduAuth
from tests.fake_api_session import FakeApiSession
from tests.test_openedu.test_api.api import courses, fake_api, auth

courses, fake_api, auth
course_id = "test_course"
block_id = "test_block"


def test_get_sequential_block():
    api = OpenEduAPI()
    api.session = FakeApiSession()
    api.get_sequential_block(course_id, block_id)

    assert api.session.last_request.headers == {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0',
        'Referer': 'https://apps.openedu.ru/',
        'Origin': 'https://apps.openedu.ru',
        'USE-JWT-COOKIE': 'true',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site'
    }


def test_problem_check():
    api = OpenEduAPI()
    api.session = FakeApiSession()
    api.session.cookies['csrftoken'] = 'token'
    api.problem_check(course_id, block_id, {"task": "ans"})
    assert api.session.last_request.headers == {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0',
        'X-CSRFToken': 'token',
        'Referer': 'https://courses.openedu.ru/xblock/test_block?show_title=0&show_bookmark_button=0&recheck_access=1&view=student_view&format=%D0%A2%D0%B5%D1%81%D1%82%20%D0%BA%20%D0%BF%D1%80%D0%B0%D0%BA%D1%82%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%BE%D0%BC%D1%83%20%D0%B7%D0%B0%D0%BD%D1%8F%D1%82%D0%B8%D1%8E',
        'Origin': 'https://courses.openedu.ru'
    }


def test_login():
    auth = OpenEduAuth()
    auth.session = FakeApiSession()
    auth.login("user", "pass")
    assert auth.session.last_request.headers == {}


def test_post_login_data():
    auth = OpenEduAuth()
    auth.session = FakeApiSession()
    with open(os.path.join("tests", "data", "auth.html"), encoding='utf-8') as f:
        auth_page = f.read()
    auth.post_login_data("user", "pass", auth_page)
    assert auth.session.last_request.headers == {}
    assert auth.session.last_request.data == {'password': 'pass', 'username': 'user'}
