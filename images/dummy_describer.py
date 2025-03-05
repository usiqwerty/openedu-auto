from images.image_describer import ImageDescriber


class DummyDescriber(ImageDescriber):
    def get_description(self, url: str) -> str:
        return "Elon Musk"
