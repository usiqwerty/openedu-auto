import json
import logging
import os.path
import re

import requests.utils
from requests import Session

import config

userinfo = {
    "version": 1,
    "username": "kirillkizilov",
    "header_urls": {
        "logout": "https://courses.openedu.ru/logout",
        "account_settings": "https://courses.openedu.ru/account/settings",
        "learner_profile": "https://courses.openedu.ru/u/kirillkizilov",
        "resume_block": "https://courses.openedu.ru/courses/course-v1:spbstu+PHYLOS+spring_2024_4/jump_to/block-v1:spbstu+PHYLOS+spring_2024_4+type@problem+block@a70196866e8e3679f32c"
    }}


def try_pop(mapping, key):
    if key in mapping:
        mapping.pop(key)


class OpenEduAuth:
    session: Session
    jar_path = os.path.join(config.userdata_dir, "cookies.json")

    def __init__(self):
        try:
            with open(self.jar_path, encoding='utf-8') as f:
                jar_json = json.load(f)
        except FileNotFoundError:
            jar_json = {}

        self.session = Session()
        self.session.cookies = requests.utils.cookiejar_from_dict(jar_json)

        # self.session.cookies['edx-user-info'] = str(userinfo)

    def save(self):
        jar_json = requests.utils.dict_from_cookiejar(self.session.cookies)
        with open(self.jar_path, 'w', encoding='utf-8') as f:
            json.dump(jar_json, f)
            logging.debug("Cookie jar saved")

    def login(self, username: str, password: str):
        url = "https://sso.openedu.ru/realms/openedu/protocol/openid-connect/auth?client_id=plp&redirect_uri=https://openedu.ru/complete/npoedsso/&state=Rql06CWhDvFaNd7ZlezZmyx2arii4bmV&response_type=code&nonce=QrwV7JTo3IKcicdXBwq7RuWY7xFh9wb6oacL76tumVAMum87G2G8PoLNBQnmF28x&scope=openid+profile+email"
        r = self.session.get(url)
        re_result = re.search(
            r'"loginAction": "(https://sso.openedu.ru/realms/openedu/login-actions/authenticate\?session_code=[\w_-]+&execution=[\w_-]+&client_id=\w+&tab_id=[\w_-]+)',
            r.text)
        login_action = re_result.group(1)
        sid = r.cookies['AUTH_SESSION_ID']
        sidl = r.cookies['AUTH_SESSION_ID_LEGACY']
        kcr = r.cookies['KC_RESTART']

        r = self.session.post(login_action, data={"username": username, "password": password, "rememberMe": "on"})
        self.session.cookies['edxloggedin'] = "true"
        self.complete_login()

    def complete_login(self):
        if self.login_refresh() == 401:
            next = "https://apps.openedu.ru/learning/course/course-v1:urfu+HIST+spring_2025/block-v1:urfu+HIST+spring_2025+type@sequential+block@09fbecc104434360b01020d47e207973/block-v1:urfu+HIST+spring_2025+type@vertical+block@4c42e3f65b334f0c947a7ec1dc7e08d1"
            self.session.get(f"https://courses.openedu.ru/auth/login/keycloak/?auth_entry=login&next={next}")

        if self.login_refresh() == 401:
            pars = {
                "client_id": "edx",
                "redirect_uri": "https://courses.openedu.ru/auth/complete/keycloak/",
                "state": "2ZsdWa3y0eI0lMlvCHpIR3pe6jUO0wHR",
                "response_type": "code",
                "nonce": "JLDKnzMYbkmgRuCC3Q4s2UIpf4jibkK2feCKfiRFHlqNUVgXqawy4ELOg1UcgGqb",
                "scope": "openid profile email",
            }
            self.session.get("https://sso.openedu.ru/realms/openedu/protocol/openid-connect/auth", params=pars)

        # print(r)
        # print(r.history)
        # print(self.session.cookies['csrftoken'])

    def login_refresh(self):
        logging.debug("Login refresh")
        hdrs = config.get_headers(referer='https://apps.openedu.ru/', origin='https://apps.openedu.ru')
        hdrs['Sec-Fetch-Dest'] = 'empty'
        hdrs['Sec-Fetch-Mode'] = 'cors'
        hdrs['Sec-Fetch-Site'] = 'same-site'
        try_pop(self.session.cookies, "edx-jwt-cookie-header-payload")
        try_pop(self.session.cookies, "edx-jwt-cookie-signature")
        try_pop(self.session.cookies, "openedx-language-preference")
        r = self.session.post("https://courses.openedu.ru/login_refresh", headers=hdrs)
        logging.debug(f"Login refresh: {r.status_code}")
        return r.status_code
