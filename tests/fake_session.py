from requests import Response


class FakeSession:
    history: list

    def __init__(self):
        self.history = []

    def get(self, url, *, headers=None, cookies=None):
        print("fake get")
        self.history.append({"method": 'get', "url": url, "headers": headers, "cookies": cookies})

    def post(self, url, *, headers=None, cookies=None, json=None, data=None):
        if json is None:
            json = data
        print("fake post")
        self.history.append(
            {"method": 'post', "url": url, "headers": headers, "cookies": cookies, "json": json, "data": data})
        r = Response()
        r.status_code = 200
        r._content = b'{"current_score": 1, "total_possible": 1}'
        return r
