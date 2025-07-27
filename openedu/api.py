import logging
import urllib.parse
from json import JSONDecodeError

from requests import Session

import config
from errors import Unauthorized, GenericOpenEduError
from openedu.auth import OpenEduAuth
from openedu.course import Course, Chapter
from openedu.ids import CourseID
from openedu.local_api_storage import LocalApiStorage

referer_params = urllib.parse.urlencode({
    "show_title": 0,
    "show_bookmark_button": 0,
    "recheck_access": 1,
    "view": "student_view",
    "format": "Тест к практическому занятию"
}, quote_via=urllib.parse.quote)


def ensure_login(method):
    def wrapper(self, *args, **kwargs):
        if not self.refreshed:
            logging.debug("Refreshing login")
            self.auth.refresh()
            self.refreshed = True
            if not int(self.status()['auth']):
                raise Unauthorized('Auth is 0 after login refresh')
        return method(self, *args, **kwargs)
    return wrapper


class OpenEduAPI:
    api_storage: LocalApiStorage
    session: Session
    refreshed: bool

    def __init__(self, api_storage: LocalApiStorage):
        self.api_storage = api_storage
        self.auth = OpenEduAuth()
        self.session = self.auth.session
        self.refreshed = False

    @ensure_login
    def get_sequential_block(self, course_id: str, block_id: str):
        url = (f"https://courses.openedu.ru/api/courseware/sequence/"
               f"block-v1:{course_id}+type@sequential"
               f"+block@{block_id}")
        hdrs = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0",
            "Referer": 'https://apps.openedu.ru/',
            "Origin": 'https://apps.openedu.ru',
            "USE-JWT-COOKIE": 'true',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            "Accept": "application/json, text/plain, */*"
        }

        r = self.session.get(url, headers=hdrs)
        if r.status_code == 401:
            self.auth.refresh()
            r = self.session.get(url, headers=hdrs)
            if r.status_code == 401:
                raise Exception("Unauthorized even after refresh")
        json_result = r.json()
        if 'developer_message' in json_result:
            raise Exception(json_result['developer_message'])
        return json_result

    @ensure_login
    def publish_completion(self, course_id: str, html_block_id: str):
        url = (f"https://courses.openedu.ru/courses/course-v1:{course_id}"
               f"/xblock/{html_block_id}"
               f"/handler/publish_completion")

        if html_block_id not in self.api_storage.solved:
            logging.debug(f"[COMPLETE] {url}")

            referer = f"https://courses.openedu.ru/xblock/{html_block_id}?show_title=0&show_bookmark_button=0&recheck_access=1&view=student_view"
            hdrs = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0",
                'X-CSRFToken': self.session.cookies.get('csrftoken', domain=''),
                "Referer": referer
            }
            if not config.config.get('restrict-actions'):
                logging.debug("[POST] publish completion")
                r = self.session.post(url, headers=hdrs, json={"completion": 1})
                try:
                    data = r.json()
                except JSONDecodeError as e:
                    logging.error(f"Could not decode JSON for publish completion response: {e}")
                    return  # remains not marked as complete

                if 'error' in data or (data['result'] != 'ok'):
                    logging.error(f"Completion was not okay: {data}")
                if r.status_code == 200:
                    logging.debug("Completion successful")
                else:
                    logging.error(f"Completion error: {r}")
        self.api_storage.mark_block_as_completed(html_block_id)

    @ensure_login
    def problem_check(self, course_id: str, blk: str, answers: dict[str, str]):
        logging.info(f"Checking answer: {answers}")
        url = f"https://courses.openedu.ru/courses/course-v1:{course_id}/xblock/{blk}/handler/xmodule_handler/problem_check"

        cccc = self.session.cookies.get('csrftoken', domain='')
        if cccc is None:
            raise Exception
        hdrs = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0",
            'X-CSRFToken': cccc,
            "Referer": f"https://courses.openedu.ru/xblock/{blk}?" + referer_params,
            "Origin": "https://courses.openedu.ru"
        }

        if not config.config.get('restrict-actions'):
            print(f"[POST] {answers}")
            r = self.session.post(url, headers=hdrs, data=answers)
            logging.debug(f"Response status: {r.status_code}")
            self.api_storage.mark_block_as_completed(blk)
            try:
                current = r.json()['current_score']
                maxscore = r.json()['total_possible']
            except KeyError as e:
                logging.warning(e)
                return 0, 0
            return current, maxscore
        else:
            logging.debug(f"False answer check {answers}")
            return 0, 0

    @ensure_login
    def course_info(self, course_id: CourseID):
        headers = {
            "Origin": "https://apps.openedu.ru",
            "Referer": "https://apps.openedu.ru/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "USE-JWT-COOKIE": "true",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0"
        }
        r_meta = self.session.get(f'https://courses.openedu.ru/api/course_home/course_metadata/course-v1:{course_id}')
        meta_data = r_meta.json()
        if not meta_data['course_access']['has_access']:
            logging.critical(meta_data['course_access']['user_message'])
            if meta_data['course_access']['error_code'] == 'enrollment_required':
                raise GenericOpenEduError(meta_data['course_access']['error_code'], meta_data['course_access']['user_message'])
            raise Unauthorized(meta_data['course_access']['user_message'])
        r = self.session.get(f"https://courses.openedu.ru/api/course_home/outline/course-v1:{course_id}",
                             headers=headers)
        data = r.json()
        course_block = None
        blocks = data['course_blocks']['blocks']
        for blk in blocks.values():
            if blk['type'] == 'course':
                course_block = blk
                break

        course_name = course_block['display_name']
        chapters = []
        for chapter_id in course_block['children']:
            chapter_name = blocks[chapter_id]['display_name']
            chapters.append(Chapter(name=chapter_name, sequentials=blocks[chapter_id]['children']))

        return Course(id=str(course_id), name=course_name, chapters=chapters)

    @ensure_login
    def get_vertical_html(self, blk: str) -> str:
        logging.debug("Requesting xblock")
        url = f"https://courses.openedu.ru/xblock/{blk}"
        return self.get(url)

    @ensure_login
    def get(self, url, is_json=False):
        print("openeduapi(get):", self.api_storage.cache.keys())
        if url not in self.api_storage.cache:
            r = self.session.get(url)
            if is_json:
                self.api_storage.cache[url] = r.json()
            else:
                self.api_storage.cache[url] = r.text
            self.api_storage.save()
        return self.api_storage.cache[url]

    def status(self):
        r = self.session.get("https://openedu.ru/auth/status?url=/")
        return r.json()
