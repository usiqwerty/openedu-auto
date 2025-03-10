from typing import Callable

from requests import Response, Request


class FakeApiSession:
    history: list
    cookies: dict
    endpoints: dict[str, Callable[[Request], Response]] = {}

    def __init__(self):
        self.history = []
        self.cookies = {}

    @staticmethod
    def register(url: str):
        def dec(func):
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            FakeApiSession.endpoints[url] = wrapper
            return wrapper

        return dec

    def send(self, req: Request):
        return self.endpoints[req.url](req)

    def get(self, url, *, headers=None, cookies=None, params=None):
        return self.send(Request(method='get', url=url, headers=headers, cookies=cookies, params=params))

    def post(self, url: str, *, headers=None, cookies=None, json=None, data=None, params=None):
        return self.send(
            Request(method='post', url=url, headers=headers, cookies=cookies, params=params, json=json, data=data))
