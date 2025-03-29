import json
import logging
import urllib.parse
from typing import Any

from requests import Session

import config
from cached_requests import cache_fn
from errors import Unauthorized
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


class OpenEduAPI:
    api_storage: LocalApiStorage
    session: Session
    cache: dict[str, Any]

    def __init__(self):
        self.api_storage = LocalApiStorage()
        self.auth = OpenEduAuth()
        self.session = self.auth.session

        try:
            with open(cache_fn, encoding='utf-8') as f:
                self.cache = json.load(f)
        except FileNotFoundError:
            self.cache = {}

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
                data = r.json()
                if 'error' in data or (data['result'] != 'ok'):
                    logging.error(f"Completion was not okay: {data}")
                if r.status_code == 200:
                    logging.debug("Completion successful")
                else:
                    logging.error(f"Completion error: {r}")
        self.api_storage.mark_block_as_completed(html_block_id)

    def problem_check(self, course_id: str, blk: str, answers: dict[str, str]):
        logging.info(f"Checking answer: {answers}")
        url = f"https://courses.openedu.ru/courses/course-v1:{course_id}/xblock/{blk}/handler/xmodule_handler/problem_check"

        cccc = self.session.cookies.get('csrftoken', domain='')
        if cccc is None:
            raise Exception
        hdrs = config.get_headers(
            csrf=cccc,
            referer=f"https://courses.openedu.ru/xblock/{blk}?" + referer_params,
            origin="https://courses.openedu.ru"
        )

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
            logging.error(meta_data['course_access']['user_message'])
            raise Unauthorized
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

    def get_vertical_html(self, blk: str) -> str:
        logging.debug("Requesting xblock")
        url = f"https://courses.openedu.ru/xblock/{blk}"
        # r = self.session.get(url)
        # return r.text
        return self.get(url)

    def get(self, url, is_json=False):
        if url not in self.cache:
            r = self.session.get(url)
            if is_json:
                self.cache[url] = r.json()
            else:
                self.cache[url] = r.text
            self.save()
        return self.cache[url]

    def save(self):
        with open(config.cache_fn, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f)
    # def next_page(self):
    #     curtab = 2
    #     tabcount = 4
    #
    #     blk = f"block-v1:{self.course_id}+type@vertical+block@e6894837138c4d6d93012b8deb45643d"
    #     seq_blk = f"block-v1:{self.course_id}+type@sequential+block@6396cae92b0442419cbf0491de7626a2"
    #
    #     page = f"https://apps.openedu.ru/learning/course/course-v1:{self.course_id}/{seq_blk}/{blk}"
    #     event = {"current_tab": curtab,
    #              "id": blk,
    #              "tab_count": tabcount,
    #              "widget_placement": "top",
    #              "target_tab": curtab + 1}
    #     dt = {
    #         "event_type": "edx.ui.lms.sequence.tab_selected",
    #         "event": str(event),
    #         "page": page
    #     }
    #     url = "https://courses.openedu.ru/event"
    #     if not config.config.get('restrict-actions'):
    #         logging.debug("[POST] next page event")
    #         hdrs = config.get_headers()
    #         return self.session.post(url, headers=hdrs, cookies=config.get_cookies(self.csrf), data=dt)
    #     else:
    #         logging.debug("fake [POST] next page event")

    # def tick_page(self, blk: str):
    #     logging.debug("Sending page close event")
    #     urllib.parse.urlencode({
    #         "event_type":"page_close",
    #         "event":"",
    #         "page":f"https://courses.openedu.ru/xblock/{blk}?",
    #         f"show_title=0"
    #         f"&show_bookmark_button=0"
    #         f"&recheck_access=1"
    #         f"&view=student_view"
    #     })
    #     url = (f"https://courses.openedu.ru/event?"
    #         )
    #     if not config.config.get('restrict-actions'):
    #         logging.debug("[GET] tick page")
    #         hrds = config.get_headers()
    #         self.session.get(url, headers=hrds, cookies=config.get_cookies(self.csrf))
    #     else:
    #         logging.debug("fake [GET] tick page")
