from abc import ABC, abstractmethod


class ImageDescriber(ABC):

    def describe(self, url: str) -> str:
        return f"Изображение: {self.get_description(url)}"

    @abstractmethod
    def get_description(self, url: str)->str:
        pass