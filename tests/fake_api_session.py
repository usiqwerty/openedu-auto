import urllib.parse
from typing import Callable

from requests import Response, Request
from requests.cookies import RequestsCookieJar


class FakeApiSession:
    history: list
    cookies: RequestsCookieJar
    endpoints: dict[str, Callable[[Request], Response]] = {}
    logged_in: bool

    def __init__(self):
        self.history = []
        self.cookies = RequestsCookieJar()

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
        return resp

    def get(self, url, *, headers=None, cookies=None, params=None, allow_redirects=None):
        return self.send(Request(method='get', url=url, headers=headers, cookies=cookies, params=params))

    def post(self, url: str, *, headers=None, cookies=None, json=None, data=None, params=None):
        return self.send(
            Request(method='post', url=url, headers=headers, cookies=cookies, params=params, json=json, data=data))
