from mistralai import Mistral

import config
from images.image_describer import ImageDescriber


class MistralDescriber(ImageDescriber):
    model = "pixtral-12b-2409"

    def __init__(self):
        self.client = Mistral(api_key=config.config["mistral-key"])

    def get_description(self, url: str) -> str:
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": 'Кто или что изображено на картинке? Напиши только короткий ответ, например, "Илон Маск" или "красный автомобиль"'
                    },
                    {
                        "type": "image_url",
                        "image_url": url
                    }
                ]
            }
        ]
        chat_response = self.client.chat.complete(
            model=self.model,
            messages=messages
        )
        return chat_response.choices[0].message.content
