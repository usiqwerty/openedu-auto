import logging
from abc import ABC

from openai import OpenAI

import config
from solvers.llm_solver import LLMSolver


class OpenRouterSolver(LLMSolver, ABC):
    client: OpenAI
    model: str
    base_url = "https://openrouter.ai/api/v1"

    interval_sec = 10

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

        if completion.choices is None:
            error = completion.model_extra['error']
            logging.critical(f"Error solving")
            logging.critical(f"Code {error['code']}: {error['message']}")
            logging.critical(error['metadata'])
            raise Exception
        return completion.choices[0].message.content


def openrouter_solver(model_: str):
    class Solver(OpenRouterSolver):
        model = model_
        cache_fn = "generic-openrouter-cache.json"

    return Solver()
