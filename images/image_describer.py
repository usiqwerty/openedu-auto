import datetime
import json
import os
import time
from abc import ABC, abstractmethod

from config import userdata_dir


class ImageDescriber(ABC):
    last_described = 0
    interval_sec = 5

    def describe(self, url: str) -> str:
        cache = self.load_cache()
        if url in cache:
            return cache[url]

        now = datetime.datetime.now().timestamp()
        delta = now - self.last_described
        if delta < self.interval_sec:
            time.sleep(delta)
        description = self.get_description(url)
        self.last_described = now
        cache[url] = description
        self.save_cache(cache)
        return f"Изображение: {description}"

    @abstractmethod
    def get_description(self, url: str) -> str:
        pass

    def load_cache(self):
        path = os.path.join(userdata_dir, "image-cache.json")
        try:
            with open(path, encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_cache(self, data: dict[str, str]):
        path = os.path.join(userdata_dir, "image-cache.json")
        with open(path, 'w', encoding='utf-8') as f:
            return json.dump(data, f)
