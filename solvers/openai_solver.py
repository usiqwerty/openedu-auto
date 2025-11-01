import logging

from openai import OpenAI

import config
from solvers.llm_solver import LLMSolver


class GenericOpenAISolver(LLMSolver):
    client: OpenAI
    model = config.config["openai-model"]
    cache_fn = "openai-cache.json"

    def __init__(self):
        super().__init__()
        self.client = OpenAI(api_key=config.config["openai-key"], base_url=config.config["openai-base-url"])

    def make_gpt_request(self, query) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": query},
            ],
            stream=False
        )
        if response.choices is None:
            error = response.model_extra['error']
            logging.critical(f"Error solving")
            logging.critical(f"Code {error['code']}: {error['message']}")
            logging.critical(error['metadata'])
            raise Exception
        return response.choices[0].message.content
