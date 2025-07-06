import json
import os
import re
import shutil

import pytest
import responses

import config
from automation.autosolver import OpenEduAutoSolver
from images.image_describer import ImageDescriber
from openedu.api import OpenEduAPI
from openedu.local_api_storage import DummyApiStorage
from openedu.openedu import OpenEdu
from tests.fakes import DummySolver, DummyDescriber

test_course = "test_course"

with open('tests/data/full/course_meta.json', encoding='utf-8') as f:
    course_meta = json.load(f)

with open('tests/data/full/outline.json', encoding='utf-8') as f:
    outline = json.load(f)
with open('tests/data/full/seq.json', encoding='utf-8') as f:
    sequential = json.load(f)
with open('tests/data/full/with_video.html', encoding='utf-8') as f:
    vertical = f.read()
with open('tests/data/full/problem_check.json', encoding='utf-8') as f:
    problem_check = json.load(f)


def register_api_endpoints():
    responses.post(
        "https://courses.openedu.ru/login_refresh",
        status=200,
        json={
            "success": True,
            "user_id": 3851040,
            "response_epoch_seconds": 1751282414.3901932,
            "response_http_date": "Mon, 30 Jun 2025 11:20:14 GMT",
            "expires": "Mon, 30 Jun 2025 11:23:14 GMT",
            "expires_epoch_seconds": 1751282594
        }
    )

    responses.get(
        f"https://courses.openedu.ru/api/course_home/course_metadata/course-v1:{test_course}",
        json=course_meta
    )
    responses.get(
        f"https://courses.openedu.ru/api/course_home/outline/course-v1:{test_course}",
        json=outline
    )
    responses.get(
        f"https://courses.openedu.ru/api/courseware/sequence/block-v1:{test_course}+type@sequential+block@123",
        json=sequential
    )

    responses.get(
        f"https://courses.openedu.ru/xblock/block-v1:{test_course}+type@vertical+block@987",
        body=vertical,
        headers={'Set-Cookie': 'csrftoken=thetoken'},
    )
    responses.post(
        re.compile(
            r"https://courses.openedu.ru/courses/course-v1:test_course/xblock/block-v1:test_course\+type@html\+block@[\W\w]+/handler/publish_completion", ),
        json={"result": "ok"}
    )


# still need this, because of userdata/solutions
@pytest.fixture(scope='session', autouse=True)
def cleanup_userdata_in_testdir():
    yield
    if os.path.exists(config.userdata_dir):
        shutil.rmtree(config.userdata_dir)


class TestingOpenEdu(OpenEdu):
    def __init__(self, describer: ImageDescriber):
        super().__init__(describer)

        self.storage = DummyApiStorage()
        self._api = OpenEduAPI(self.storage)


@pytest.fixture(scope='function')
def empty_auto_solver():
    solver = DummySolver()
    describer = DummyDescriber()
    aslv = OpenEduAutoSolver(solver, describer)
    aslv.app = TestingOpenEdu(aslv.describer)

    # aslv.app.storage = DummyApiStorage()
    # aslv.app.api.api_storage = aslv.app.storage
    aslv.app.logout()
    # print(aslv.app.storage.cache)
    yield aslv
    print('teardown')


def assert_calls_counts_except_login(count: int):
    request_urls = [call.request.url for call in responses.calls]
    for resp in responses.registered():
        if isinstance(resp.url, str):
            if resp.url != 'https://courses.openedu.ru/login_refresh':
                assert responses.assert_call_count(resp.url, count)
        else:
            for u in request_urls:
                if resp.url.match(u):
                    assert responses.assert_call_count(u, count)
