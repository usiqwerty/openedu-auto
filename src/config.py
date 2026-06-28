import json
import os
from typing import TypedDict, Literal

from errors import ConfigError

Config = TypedDict(
    "Config",
    {
        "last-course": str,
        "openrouter-key": str,
        "openai-key": str,
        "openai-base-url": str,
        "openai-model": str,
        "consensus-models": list[str]
    },
    total=False
)

ConfigKeys = Literal["last-course", "openrouter-key", "openai-key", "openai-base-url",
"openai-model", "consensus-models"]


def set_config(key: ConfigKeys, val):
    global config
    config[key] = val

    with open(config_fn, 'w', encoding='utf-8') as f:
        json.dump(config, f)


def require_config_field(name: ConfigKeys):
    if name in config:
        return config[name]
    raise ConfigError(f"Config field '{name}' was not found")


userdata_dir = "userdata"
solutions_dir = os.path.join(userdata_dir, "solutions")
config_fn = os.path.join(userdata_dir, "config.json")
cache_fn = os.path.join(userdata_dir, "cache.json")
blocks_fn = os.path.join(userdata_dir, "blocks.json")
courses_fn = os.path.join(userdata_dir, "courses.json")
solved_fn = os.path.join(userdata_dir, "solved.json")
ignored_fn = os.path.join(userdata_dir, "ignored.json")
cookies_fn = os.path.join(userdata_dir, "cookies.json")
os.makedirs(solutions_dir, exist_ok=True)

config: Config
try:
    with open(config_fn, encoding='utf-8') as f:
        config = json.load(f)
except FileNotFoundError:
    config = {}
