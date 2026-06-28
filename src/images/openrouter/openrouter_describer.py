from abc import ABC

from src import config
from src.images.openai_describer import OpenAIImageDescriber


class OpenRouterImageDescriber(OpenAIImageDescriber, ABC):

    def __init__(self):
        super().__init__("https://openrouter.ai/api/v1", config.config['openrouter-key'])
