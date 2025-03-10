import tests.fake_api
from openedu.api import OpenEduAPI
from openedu.oed_parser import VerticalBlock
from tests.fake_api_session import FakeApiSession


def test_get_sequential_block():
    api = OpenEduAPI()
    api.session = FakeApiSession()
    api.get_sequential_block(tests.fake_api.course_id, tests.fake_api.block_id)


def test_publish_completion():
    api = OpenEduAPI()
    api.api_storage.blocks = {"test_block": VerticalBlock(id="test_block", title='', complete=False, type='')}
    api.session = FakeApiSession()
    api.publish_completion(tests.fake_api.course_id, tests.fake_api.block_id)


def test_problem_check():
    api = OpenEduAPI()
    api.session = FakeApiSession()
    api.problem_check(tests.fake_api.course_id, tests.fake_api.block_id, {"task": "ans"})
