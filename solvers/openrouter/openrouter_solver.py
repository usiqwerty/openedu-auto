import logging
from abc import ABC

from openai import OpenAI

import config
from solvers.gpt_solver import LLMSolver


class OpenRouterSolver(LLMSolver, ABC):
    client: OpenAI
    model: str
    base_url = "https://openrouter.ai/api/v1"

    def __init__(self):
        self.client = OpenAI(base_url=self.base_url, api_key=config.config['openrouter-key'])
        super().__init__()
        logging.debug("OpenRouter solver set up")

    def make_gpt_request(self, query) -> str:
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": query
                }
            ]
        )
        return completion.choices[0].message.content
