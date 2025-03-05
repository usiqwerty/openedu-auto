import json

from requests import Session
import logging

import config
from openedu.oed_parser import VerticalBlock


class OpenEduAPI:
    blocks: dict[str, VerticalBlock]

    def __init__(self, course_id):
        self.csrf = config.config.get('csrf')
        self.blocks = {}
        self.course_id = course_id
        self.session = Session()
        try:
            with open(config.blocks_fn, encoding='utf-8') as f:
                self.blocks = {k: VerticalBlock(**json.loads(v)) for k, v in json.load(f).items()}
        except FileNotFoundError:
            pass

    def publish_completion(self, block_id: str):
        url = ("https://courses.openedu.ru/courses/"
               f"course-v1:{self.course_id}/xblock/"
               f"{block_id}"
               "/handler/publish_completion")

        if 1 or not self.blocks[block_id]['complete']:
            logging.debug(f"[COMPLETE] {url}")
            mhdrs = config.get_headers(
                csrf=self.csrf,
                referer=f"https://courses.openedu.ru/xblock/{block_id}?show_title=0&show_bookmark_button=0&recheck_access=1&view=student_view"
            )
            if not config.config.get('restrict-actions'):
                logging.debug("[POST] publish completion")
                r = self.session.post(url, headers=mhdrs, cookies=config.get_cookies(self.csrf), json={"completion": 1})
                logging.debug(r)
        if config.config.get('restrict-actions'):
            if self.blocks.get(block_id):
                self.blocks[block_id].complete = True

    def problem_check(self, blk: str, answers: dict[str, str]):
        logging.info(f"Checking answer: {answers}")
        url = f"https://courses.openedu.ru/courses/course-v1:{self.course_id}/xblock/{blk}/handler/xmodule_handler/problem_check"
        # url = f"https://courses.openedu.ru/courses/course-v1:{self.course_id}/xblock/block-v1:{self.course_id}+type@problem+block@{blk}/handler/xmodule_handler/problem_check"
        hdrs = config.get_headers(
            csrf=self.csrf,
            referer=f"https://courses.openedu.ru/xblock/{blk}?show_title=0&show_bookmark_button=0&recheck_access=1&view=student_view&format=%D0%A2%D0%B5%D1%81%D1%82%20%D0%BA%20%D0%BF%D1%80%D0%B0%D0%BA%D1%82%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%BE%D0%BC%D1%83%20%D0%B7%D0%B0%D0%BD%D1%8F%D1%82%D0%B8%D1%8E",
            origin="https://courses.openedu.ru"
        )

        if not config.config.get('restrict-actions'):
            print(f"[POST] {answers}")
            r = self.session.post(url, headers=hdrs, cookies=config.get_cookies(self.csrf), data=answers)
            logging.debug(f"Response status: {r.status_code}")
            if blk in self.blocks:
                self.blocks[blk]['complete'] = True
            else:
                logging.warning("block that we are checking is not saved, this should not have happened")
            current = r.json()['current_score']
            maxscore = r.json()['total_possible']
            return current, maxscore
        else:
            logging.debug(f"fake POST {answers}")
            return 0, 0

    def next_page(self):
        curtab = 2
        tabcount = 4

        blk = f"block-v1:{self.course_id}+type@vertical+block@e6894837138c4d6d93012b8deb45643d"
        seq_blk = f"block-v1:{self.course_id}+type@sequential+block@6396cae92b0442419cbf0491de7626a2"

        page = f"https://apps.openedu.ru/learning/course/course-v1:{self.course_id}/{seq_blk}/{blk}"
        event = {"current_tab": curtab,
                 "id": blk,
                 "tab_count": tabcount,
                 "widget_placement": "top",
                 "target_tab": curtab + 1}
        dt = {
            "event_type": "edx.ui.lms.sequence.tab_selected",
            "event": str(event),
            "page": page
        }
        url = "https://courses.openedu.ru/event"
        if not config.config.get('restrict-actions'):
            logging.debug("[POST] next page event")
            hdrs = config.get_headers()
            return self.session.post(url, headers=hdrs, cookies=config.get_cookies(self.csrf), data=dt)
        else:
            logging.debug("fake [POST] next page event")

    def tick_page(self, blk: str):
        logging.debug("Sending page close event")
        url = (f"https://courses.openedu.ru/event?"
               f"event_type=page_close"
               f"&event="
               f"&page"f"=https://courses.openedu.ru/xblock/{blk}?"
               f"show_title=0"
               f"&show_bookmark_button=0"
               f"&recheck_access=1"
               f"&view=student_view")
        if not config.config.get('restrict-actions'):
            logging.debug("[GET] tick page")
            hrds = config.get_headers()
            self.session.get(url, headers=hrds, cookies=config.get_cookies(self.csrf))
        else:
            logging.debug("fake [GET] tick page")
