import json
import os

from sqlalchemy.testing.plugin.plugin_base import config


def get_headers(*, csrf=None, referer=None, origin=None):
    hrds = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0",
    }
    if csrf:
        hrds['X-CSRFToken'] = csrf
    if referer:
        hrds['Referer'] = referer
    if origin:
        hrds['Origin'] = origin
    return hrds


def get_cookies(csrf):
    return {
        "csrftoken": csrf,
        "edx-jwt-cookie-header-payload": config["edx-jwt-cookie-header-payload"],
        "edx-jwt-cookie-signature": config["edx-jwt-cookie-signature"],
        "edx-user-info": str(config["edx-user-info"]),
        "edxloggedin": "true",
        "openedx-language-preference": "ru",
        "sessionid": config["sessionid"]
    }


config_fn = os.path.join("userdata", "config.json")
with open(config_fn, encoding='utf-8') as f:
    config = json.load(f)
blocks_fn = os.path.join("userdata", "blocks.json")
userdata_dir = "userdata"