import json
import logging
import os

import requests
from requests import Session

from config import get_cookies, get_headers

cache_fn = os.path.join("userdata", "cache.json")


def get(url, session: Session, headers=None, cookies=..., is_json=True):
    if headers is None:
        headers = get_headers()
    global cache

    if url not in cache:
        logging.debug(f"Real request: {url}")
        r = session.get(url, headers=headers)
        if is_json:
            cache[url] = r.json()
        else:
            cache[url] = r.text
    return cache[url]


def save_cache():
    with open(cache_fn, 'w', encoding='utf-8') as f:
        json.dump(cache, f)
    logging.debug("Cache saved")


class CacheContext:
    callbacks: list

    def __init__(self, callbacks: list):
        self.callbacks = callbacks

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        for callback in self.callbacks:
            callback()
