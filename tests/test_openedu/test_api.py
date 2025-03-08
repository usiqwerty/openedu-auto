import pytest

import config
from openedu.api import OpenEduAPI
from openedu.local_api_storage import LocalApiStorage
from openedu.oed_parser import VerticalBlock
from tests.fakes import FakeSession


@pytest.mark.parametrize("safemode", [True, False], ids=['safemode', 'no safemode'])
def test_publish_completion(safemode):
    testing_block = VerticalBlock(id="test_block", title="Тестировочный блок", complete=False, type="problem")
    config.config['restrict-actions'] = safemode
    api = OpenEduAPI("test_course")
    api.api_storage = LocalApiStorage({testing_block.id: testing_block})
    api.session = FakeSession()
    api.publish_completion("test_block")
    if safemode:
        assert len(api.session.history) == 0
    else:
        assert len(api.session.history) == 1
        request = api.session.history[-1]
        assert request["url"] == ("https://courses.openedu.ru/courses/course-v1:test_course/"
                                  "xblock/test_block/handler/publish_completion")
        assert request["method"] == "post"
        assert request["json"] == {"completion": 1}


@pytest.mark.parametrize("safemode", [True, False], ids=['safemode', 'no safemode'])
def test_problem_check(safemode):
    testing_block = VerticalBlock(id="test_block", title="Тестировочный блок", complete=False, type="problem")
    config.config['restrict-actions'] = safemode
    api = OpenEduAPI("test_course")
    api.api_storage = LocalApiStorage({testing_block.id: testing_block})
    api.session = FakeSession()
    api.problem_check("test_block", {"input_id": "input_value"})
    if safemode:
        assert len(api.session.history) == 0
    else:
        assert len(api.session.history) == 1
        request = api.session.history[-1]
        assert request["url"] == ("https://courses.openedu.ru/courses/course-v1:test_course/"
                                  "xblock/test_block/handler/xmodule_handler/problem_check")

        assert request["method"] == "post"
        assert request["json"] == {"input_id": "input_value"}
