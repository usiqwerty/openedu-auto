import json
import logging
import os.path
import re
import urllib.parse
from http.cookiejar import Cookie

import requests.utils
from requests import Session
from requests.cookies import RequestsCookieJar

import config
from errors import ReloginReceived


def try_pop(mapping, key):
    if key in mapping:
        mapping.pop(key)


def dict_to_cookiejar(cookies_dict: list):
    cookiejar = RequestsCookieJar()

    for cookie in cookies_dict:
        cookiejar.set_cookie(Cookie(
            **cookie,
            version=0,
            port=None,
            port_specified=False,
            domain_specified=True,
            domain_initial_dot=False,
            path_specified=True,
            discard=False,
            comment=None,
            comment_url=None,
            rest={},
        ))
    return cookiejar


def cookiejar_to_dict(cookiejar: RequestsCookieJar):
    r = []
    for cookie in cookiejar:
        r.append({
            "domain": cookie.domain,
            "path": cookie.path,
            "name": cookie.name,
            "value": cookie.value,
            "secure": cookie.secure,
            "expires": cookie.expires,
        })
    return r


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
                logging.debug(f"Loaded {len(jar_json)} cookies from file")
        except FileNotFoundError:
            jar_json = []

        self.session = Session()
        self.session.cookies = dict_to_cookiejar(jar_json) # requests.utils.cookiejar_from_dict(jar_json)

    def save(self):
        jar_json = cookiejar_to_dict(self.session.cookies) #requests.utils.dict_from_cookiejar(self.session.cookies)
        with open(self.jar_path, 'w', encoding='utf-8') as f:
            json.dump(jar_json, f)
            logging.debug("Cookie jar saved")

    def login(self, username: str, password: str):
        """Perform full login process"""
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.5",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site"
        }
        self.session.get('https://openedu.ru/', headers=headers)
        rd = self.session.get('https://openedu.ru/auth/login/npoedsso/', headers=headers, allow_redirects=False)
        assert rd.status_code == 302
        r = self.session.get(rd.headers['Location'], headers=headers)
        return self.post_login_data(username, password, r.text)

    def post_login_data(self, username: str, password: str, login_page_html: str):
        """Post login data using a given auth page"""
        re_result = re.search(login_action_regex, login_page_html)
        url = re_result.group(1)
        res = urllib.parse.urlparse(url)
        base = f"{res.scheme}://{res.netloc}{res.path}"
        params = urllib.parse.parse_qs(res.query)
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.5",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site"
        }
        return self.session.post(base, data={"username": username, "password": password}, params=params, headers=headers)

    def login_refresh(self):
        logging.debug("Login refresh")
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/json, text/plain, */*",
            "Referer": 'https://apps.openedu.ru/',
            "Origin": 'https://apps.openedu.ru',
            "Accept-Language": "en-US,en;q=0.5",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site"
        }
        # with CookieContext(self.session, COURSES_COOKIES):
        r = self.session.post("https://courses.openedu.ru/login_refresh", headers=headers)
        return r

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
            'Upgrade-Insecure-Requests': '1',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-site",
            "Priority": 'u=0, i'
        }
        url = 'https://courses.openedu.ru/auth/login/keycloak/'
        r = self.session.get(url, headers=h, params=params)
        if re.match(r'^https://sso.openedu.ru/realms/openedu/protocol/openid-connect/auth', r.url):
            logging.critical("Received relogin page during keycloak request")
            raise ReloginReceived
        return r

    def openid_auth(self):
        h = {
            "User-Agent": self.user_agent,
            "Accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://apps.openedu.ru/",
            'Upgrade-Insecure-Requests': '1',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-site",
            "Priority": 'u=0, i'
        }
        url = "https://sso.openedu.ru/realms/openedu/protocol/openid-connect/auth"
        params = {
            "client_id": "edx",
            "redirect_uri": "https://courses.openedu.ru/auth/complete/keycloak/",
            "state": "WY3duzh17XHy7zS3Ml2aIC2ZT6OyDaEq",
            "response_type": "code",
            "nonce": "ax6kW7bTQLtcNxeWK5HWzDxjnIiK9NOT6HR9KwjsciDgDMI7JUwlcRKKAh99oum4",
            "scope": "openid profile email"
        }
        return self.session.get(url, params=params, headers=h)

    def refresh(self):
        """Perform full token refresh process"""
        lr = self.login_refresh()
        if lr.status_code == 200:
            if len(lr.history) < 3:
                logging.warning("Too short login refresh history")
            return
        lk = self.login_keycloak()
        if lk.status_code != 200:
            raise Exception(f"login-keycloak returned code {lk.status_code}")

    def drop(self):
        self.session.cookies = RequestsCookieJar()
        self.save()
        logging.debug("Auth cookies reset")
