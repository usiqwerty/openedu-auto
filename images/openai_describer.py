import logging
from abc import ABC

from openai import OpenAI

from images.image_describer import ImageDescriber


class OpenAIImageDescriber(ImageDescriber, ABC):
    client: OpenAI
    model: str

    def __init__(self, base_url: str, api_key: str):
        self.client = OpenAI(base_url=base_url, api_key=api_key, timeout=10)

    def get_description(self, url: str) -> str:
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": 'Кто или что изображено на фотографии. В ответе напиши только имя или название, например "Илон Маск" или "красный автомобиль"'
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": url}  # there's also a 'detail' parameter
                        }
                    ]
                }
            ]
        )
        if completion.choices is None:
            error = completion.model_extra['error']
            logging.critical(f"Error while describing image")
            logging.critical(f"Code {error['code']}: {error['message']}")
            logging.critical(error['metadata'])
            exit(1)
        return completion.choices[0].message.content
