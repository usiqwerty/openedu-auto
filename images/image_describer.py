import time
from abc import ABC, abstractmethod
import datetime


class ImageDescriber(ABC):
    last_described = 0
    interval_sec = 5

    def describe(self, url: str) -> str:
        now = datetime.datetime.now().timestamp()
        delta = now - self.last_described
        if delta < self.interval_sec:
            time.sleep(delta)
        description = self.get_description(url)
        self.last_described = now
        return f"Изображение: {description}"

    @abstractmethod
    def get_description(self, url: str)->str:
        pass
