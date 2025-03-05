import config
from openedu.api import OpenEduAPI


class FakeSession:
    history: list

    def __init__(self):
        self.history = []

    def get(self, url, *, headers=None, cookies=None):
        print("fake get")
        self.history.append({"method": 'get', "url": url, "headers": headers, "cookies": cookies})

    def post(self, url, *, headers=None, cookies=None, json=None, data=None):
        print("fake post")
        self.history.append(
            {"method": 'post', "url": url, "headers": headers, "cookies": cookies, "json": json, "data": data})


def test_publish_completion():
    config.config['restrict-actions'] = False
    api = OpenEduAPI("test_course")
    api.session = FakeSession()
    api.publish_completion("test_block")
    assert len(api.session.history) == 1
    request = api.session.history[-1]
    assert request["url"] == ("https://courses.openedu.ru/courses/course-v1:test_course/"
                              "xblock/test_block/handler/publish_completion")
    assert request["method"] == "post"
    assert request["json"] == {"completion": 1}
