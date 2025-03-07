from abc import ABC

import config
from images.openai_describer import OpenAIImageDescriber


class OpenRouterImageDescriber(ABC, OpenAIImageDescriber):

    def __init__(self):
        super().__init__("https://openrouter.ai/api/v1", config.config['openrouter-key'])
