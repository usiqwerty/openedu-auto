import json
import os

from errors import ConfigError


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


def set_config(key: str, val):
    global config
    config[key] = val

    with open(config_fn, 'w', encoding='utf-8') as f:
        json.dump(config, f)


def require_config_field(name: str):
    if name in config:
        return config[name]
    raise ConfigError(f"Config field '{name}' was not found")


userdata_dir = "userdata"
config_fn = os.path.join(userdata_dir, "config.json")
blocks_fn = os.path.join(userdata_dir, "blocks.json")
courses_fn = os.path.join(userdata_dir, "courses.json")
solved_fn = os.path.join(userdata_dir, "solved.json")
ignored_fn = os.path.join(userdata_dir, "ignored.json")

with open(config_fn, encoding='utf-8') as f:
    config = json.load(f)
