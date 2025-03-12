import urllib.parse
from typing import Callable

import requests.utils
from requests import Response, Request
from requests.cookies import RequestsCookieJar


class FakeApiSession:
    history: list
    cookies: RequestsCookieJar
    endpoints: dict[str, Callable[[Request], Response]] = {}
    logged_in: bool
    last_request: Request

    def __init__(self):
        self.history = []
        self.cookies = requests.utils.cookiejar_from_dict({
            "csrftoken": "token",
            "edx-user-info": "userinfp",
            "edxloggedin": "true",
            "sessionid": "sid",
            "openedx-language-preference": "ru",
            "KEYCLOAK_SESSION": "openedu/123",
            "KEYCLOAK_IDENTITY": "123",
            "KEYCLOAK_SESSION_LEGACY": "openedu/123",
            "KEYCLOAK_REMEMBER_ME": "username:user",
            "AUTH_SESSION_ID": "asid",
            "KEYCLOAK_IDENTITY_LEGACY": "id",
            "KEYCLOAK_LOCALE": "ru",
            "AUTH_SESSION_ID_LEGACY": "asid",
            "KC_RESTART": "keysee-restart",
            "edx-jwt-cookie-header-payload": "jwt",
            "edx-jwt-cookie-signature": "jwt-sign"
        })



    @staticmethod
    def register(url: str):
        def dec(func):
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            FakeApiSession.endpoints[url] = wrapper
            return wrapper

        return dec

    def send(self, req: Request):
        resp = self.endpoints[req.url](req)
        hdrs = dict(req.headers)
        for h in ["Host", "Referer", "Origin"]:
            try:
                hdrs.pop("Host")
            except KeyError:
                pass
        while resp.status_code == 302:
            loc = resp.headers['Location']
            res = urllib.parse.urlparse(loc)
            params = urllib.parse.parse_qs(res.query)
            r = self.get(f"{res.scheme}://{res.netloc}{res.path}", params=params, headers=hdrs)
            r.history += resp.history
            r.history.insert(0, resp)
            resp = r
        self.last_request = req
        return resp

    def get(self, url, *, headers=None, cookies=None, params=None, allow_redirects=None):
        return self.send(Request(method='get', url=url, headers=headers, cookies=cookies, params=params))

    def post(self, url: str, *, headers=None, cookies=None, json=None, data=None, params=None):
        return self.send(
            Request(method='post', url=url, headers=headers, cookies=cookies, params=params, json=json, data=data))
