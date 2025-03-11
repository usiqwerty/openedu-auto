import json
import logging
import os.path
import re
import urllib.parse

import requests.utils
from requests import Session

import config


def try_pop(mapping, key):
    if key in mapping:
        mapping.pop(key)


login_action_regex = r'"loginAction": "(https://sso.openedu.ru/realms/openedu/login-actions/authenticate\?session_code=[\w_-]+&execution=[\w_-]+&client_id=\w+&tab_id=[\w_-]+)'

SSO_COOKIES = {"KC_RESTART", "KEYCLOAK_IDENTITY", "KEYCLOAK_LOCALE", "KEYCLOAK_REMEMBER_ME", "KEYCLOAK_SESSION",
               "KEYCLOAK_SESSION_LEGACY", "AUTH_SESSION_ID", "AUTH_SESSION_ID_LEGACY", "KEYCLOAK__LEGACY",
               "KEYCLOAK_IDENTITY_LEGACY", "openedx-language-preference", 'edxloggedin', 'edx-user-info', 'sessionid'}
COURSES_COOKIES = {"csrftoken", "edx-user-info", "edxloggedin", "openedx-language-preference", "sessionid"}


class CookieContext:
    def __init__(self, session: Session, allowed: set[str]):
        self.session = session
        self.allowed = allowed

    def __enter__(self):
        self.temp = self.session.cookies.get_dict()
        self.session.cookies.clear()
        for k in self.allowed:
            if k in self.temp:
                self.session.cookies[k] = self.temp[k]

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.cookies.update(self.temp)


class OpenEduAuth:
    session: Session
    jar_path = os.path.join(config.userdata_dir, "cookies.json")
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0'

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
        """Perform full login process"""
        headers = {
            "User-Agent": self.user_agent,
            "Host": "openedu.ru",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.5",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site"
        }
        self.session.get('https://openedu.ru/')
        r = self.session.get('https://openedu.ru/login/npoedsso/', params={"next": "/"}, headers=headers)
        return self.post_login_data(username, password, r.text)

    def post_login_data(self, username: str, password: str, login_page_html: str):
        """Post login data using a given auth page"""
        re_result = re.search(login_action_regex, login_page_html)
        url = re_result.group(1)
        res = urllib.parse.urlparse(url)
        base = f"{res.scheme}://{res.netloc}{res.path}"
        params = urllib.parse.parse_qs(res.query)
        return self.session.post(base, data={"username": username, "password": password}, params=params)

    def login_refresh(self):
        logging.debug("Login refresh")
        headers = {
            "User-Agent": self.user_agent,
            "Host": "courses.openedu.ru",
            "Accept": "application/json, text/plain, */*",
            "Referer": 'https://apps.openedu.ru/',
            "Origin": 'https://apps.openedu.ru',
            "Accept-Language": "en-US,en;q=0.5",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site"
        }
        with CookieContext(self.session, COURSES_COOKIES):
            r = self.session.post("https://courses.openedu.ru/login_refresh", headers=headers)
        return r
        if r.status_code == 200:
            return
        elif r.status_code != 401:
            raise Exception(f"login_refresh returned {r.status_code}")
        logging.debug(f"Login refresh: {r.status_code}")
        return r.status_code

    def login_keycloak(self):
        """Touch /auth/login/keycloak"""
        params = {
            "auth_entry": "login",
            "next": "https://apps.openedu.ru/learning/course/course-v1:urfu+HIST+spring_2025/block-v1:urfu+HIST+spring_2025+type@sequential+block@55b86722df2445dd958566d725199d00/block-v1:urfu+HIST+spring_2025+type@vertical+block@ee4bd86f2fb0493cae7f326685469638"
        }

        h = {
            "User-Agent": self.user_agent,
            "Accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://apps.openedu.ru/",
            "Host": "courses.openedu.ru",
            'Upgrade-Insecure-Requests': '1',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-site",
            "Priority": 'u=0, i'
        }
        url = 'https://courses.openedu.ru/auth/login/keycloak/'
        with CookieContext(self.session, COURSES_COOKIES):
            r = self.session.get(url, headers=h, params=params, allow_redirects=False)
        return r

    def openid_auth(self, url: str):
        """"""
        h = {
            "User-Agent": self.user_agent,
            "Accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://apps.openedu.ru/",
            "Host": "sso.openedu.ru",
            'Upgrade-Insecure-Requests': '1',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-site",
            "Priority": 'u=0, i'
        }
        res = urllib.parse.urlparse(url)
        base_url = f"{res.scheme}://{res.netloc}/{res.path}"
        params = {k: v for k, v in urllib.parse.parse_qsl(res.query)}
        with CookieContext(self.session, SSO_COOKIES):
            return self.session.get(base_url, params=params, headers=h)

    def refresh(self):
        """Perform full token refresh process"""
        lr = self.login_refresh()
        kr = self.login_keycloak()
        oiar = self.openid_auth(kr.headers['location'])
        if oiar.status_code == 200 and len(oiar.history) == 1:
            logn = self.post_login_data(config.config['username'], config.config['password'], oiar.text)
        pass
