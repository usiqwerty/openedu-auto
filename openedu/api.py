import json
import logging
import urllib.parse
from typing import Any

from requests import Session

import config
from cached_requests import get
from config import get_headers
from openedu.local_api_storage import LocalApiStorage

referer_params = urllib.parse.urlencode({
    "show_title": 0,
    "show_bookmark_button": 0,
    "recheck_access": 1,
    "view": "student_view",
    "format": "Тест к практическому занятию"
}, quote_via=urllib.parse.quote)


class OpenEduAPI:
    __csrf = None
    api_storage: LocalApiStorage
    session: Session
    course_id: str

    @property
    def csrf(self):
        if self.__csrf is None:
            self.get_csrf()
        return self.__csrf

    @csrf.setter
    def csrf(self, value):
        self.__csrf = value

    def __init__(self, course_id):
        self.csrf = config.config.get('csrf')
        self.course_id = course_id
        self.session = Session()
        self.api_storage = LocalApiStorage()

    def get_csrf(self) -> str:
        logging.debug('Requesting csrf token')
        r = self.session.get('https://courses.openedu.ru/csrf/api/v1/token',
                             headers=config.get_headers(),
                             cookies=config.get_cookies(""))

        self.csrf = r.cookies['csrftoken'] # r.json()['csrfToken']
        config.config['csrf'] = self.csrf
        self.save_config(config.config)

        return self.csrf

    def get_sequential_block(self, block_id: str):
        url = (f"https://courses.openedu.ru/api/courseware/sequence/"
               f"block-v1:{self.course_id}+type@sequential"
               f"+block@{block_id}")
        hdrs = get_headers(referer='https://apps.openedu.ru', origin='https://apps.openedu.ru')
        # hdrs["USE-JWT-COOKIE"] = 'true'
        return get(url, self.csrf, headers=hdrs)

    def save_config(self, cfg: dict[str, Any]):
        with open(config.config_fn, 'w', encoding='utf-8') as f:
            json.dump(cfg, f)
        logging.debug("Config saved")

    def publish_completion(self, block_id: str):
        url = ("https://courses.openedu.ru/courses/"
               f"course-v1:{self.course_id}/xblock/"
               f"{block_id}"
               "/handler/publish_completion")

        if not self.api_storage.is_block_complete(block_id):
            logging.debug(f"[COMPLETE] {url}")
            mhdrs = config.get_headers(
                csrf=self.csrf,
                referer=f"https://courses.openedu.ru/xblock/{block_id}?show_title=0&show_bookmark_button=0&recheck_access=1&view=student_view"
            )
            if not config.config.get('restrict-actions'):
                logging.debug("[POST] publish completion")
                r = self.session.post(url, headers=mhdrs, cookies=config.get_cookies(self.csrf), json={"completion": 1})
                logging.debug(r)
        self.api_storage.mark_block_as_completed(block_id)

    def problem_check(self, blk: str, answers: dict[str, str]):
        logging.info(f"Checking answer: {answers}")
        url = f"https://courses.openedu.ru/courses/course-v1:{self.course_id}/xblock/{blk}/handler/xmodule_handler/problem_check"

        hdrs = config.get_headers(
            csrf=self.csrf,
            referer=f"https://courses.openedu.ru/xblock/{blk}?" + referer_params,
            origin="https://courses.openedu.ru"
        )

        if not config.config.get('restrict-actions'):
            print(f"[POST] {answers}")
            r = self.session.post(url, headers=hdrs, cookies=config.get_cookies(self.csrf), data=answers)
            logging.debug(f"Response status: {r.status_code}")
            self.api_storage.mark_block_as_completed(blk)
            current = r.json()['current_score']
            maxscore = r.json()['total_possible']
            return current, maxscore
        else:
            logging.debug(f"False answer check {answers}")
            return 0, 0

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
