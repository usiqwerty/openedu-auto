from abc import ABC

from openai import OpenAI

from images.image_describer import ImageDescriber


class OpenAIImageDescriber(ABC, ImageDescriber):
    client: OpenAI
    model: str

    def __init__(self, base_url: str, api_key: str):
        self.client = OpenAI(base_url=base_url, api_key=api_key)

    def get_description(self, url: str) -> str:
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Кто или что изображено на фотографии"
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": url}  # there's also a 'detail' parameter
                        }
                    ]
                }
            ]
        )
        return completion.choices[0].message.content
