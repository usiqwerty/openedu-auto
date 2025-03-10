import json
from http.cookiejar import Cookie

from requests import Request, Response

from tests.fake_api_session import FakeApiSession

course_id = 'test_course'
block_id = 'test_block'


@FakeApiSession.register("https://courses.openedu.ru/login_refresh")
def refresh_login(req: Request):
    resp = Response()
    resp.status_code = 401
    resp.cookies.set_cookie(Cookie(**{
        "name": "sessionid",
        "domain": ".openedu.ru",
        "expires": "2025-03-24T10:33:01.000Z",
        "httpOnly": 'true',
        "path": "/",
        "samesite": "None",
        "secure": 'true',
        "value": "blablabla"
    }))
    return resp


@FakeApiSession.register(
    f"https://courses.openedu.ru/api/courseware/sequence/block-v1:{course_id}+type@sequential+block@{block_id}")
def get_seq_block(req: Request):
    resp = Response()
    d = {"items": [{"content": "",
                    "page_title": "Учебное задание",
                    "type": "problem",
                    "id": f"block-v1:{course_id}+type@vertical+block@{block_id[::-1]}",
                    "bookmarked": False,
                    "path": "Тема 1. История как наука > Учебное задание > Учебное задание",
                    "graded": True,
                    "contains_content_type_gated_content": False,
                    "href": "",
                    "complete": False}],
         "element_id": f"{block_id}",
         "item_id": f"block-v1:{course_id}+type@sequential+block@{block_id}",
         "is_time_limited": False,
         "is_proctored": False,
         "position": 1,
         "tag": "sequential",
         "next_url": None,
         "prev_url": None,
         "banner_text": None,
         "save_position": True,
         "show_completion": True,
         "gated_content": {"prereq_id": None,
                           "prereq_url": None,
                           "prereq_section_name": None,
                           "gated": False,
                           "gated_section_name": "Учебное задание"},
         "sequence_name": "Учебное задание",
         "exclude_units": True,
         "gated_sequence_paywall": None,
         "is_gated_milestone_passed": True,
         "display_name": "Учебное задание",
         "format": None,
         "is_hidden_after_due": False}
    resp._content = json.dumps(d).encode()
    return resp


@FakeApiSession.register(
    f"https://courses.openedu.ru/courses/course-v1:{course_id}/xblock/{block_id}/handler/publish_completion")
def publish_completion(req: Request):
    resp = Response()
    resp._content = b'{"completion": 1}'
    return resp


@FakeApiSession.register(
    f"https://courses.openedu.ru/courses/course-v1:{course_id}/xblock/{block_id}/handler/xmodule_handler/problem_check")
def problecm_check(req: Request):
    resp = Response()
    resp._content = b'{"current_score": 1, "total_possible": 1}'
    return resp
