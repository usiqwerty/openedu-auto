from requests import Request, Response

from tests.fake_api_session import FakeApiSession


@FakeApiSession.register("https://courses.openedu.ru/api/courseware/sequence/block-v1:test_course+type@sequential+block@test_block")
def seq_block(req: Request):
    resp = Response()
    resp.status_code = 200
    resp._content = b'{}'
    return resp


@FakeApiSession.register("https://courses.openedu.ru/courses/course-v1:test_course/xblock/test_block/handler/xmodule_handler/problem_check")
def seq_block(req: Request):
    resp = Response()
    resp.status_code = 200
    resp._content = b'{}'
    return resp
