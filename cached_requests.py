import json
import logging
import os

import requests

from config import get_cookies, get_headers

cache_fn = os.path.join("userdata", "cache.json")
try:
    with open(cache_fn, encoding='utf-8') as f:
        cache = json.load(f)
except FileNotFoundError:
    cache = {}


def get(url, csrf="", headers=None, cookies=None, is_json=True):
    if headers is None:
        headers = get_headers()
    if cookies is None:
        cookies = get_cookies(csrf)
    global cache
    if url not in cache:
        logging.debug(f"Real request: {url}")
        r = requests.get(url, headers=headers, cookies=cookies)
        if is_json:
            cache[url] = r.json()
        else:
            cache[url] = r.text
    # save_cache()
    return cache[url]


def save_cache():
    with open(cache_fn, 'w', encoding='utf-8') as f:
        json.dump(cache, f)
    logging.debug("Cache saved")


class CacheContext:
    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        save_cache()
