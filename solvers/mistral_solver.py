from mistralai import Mistral
import logging

import config
from solvers.gpt_solver import LLMSolver


class MistralSolver(LLMSolver):
    model = "mistral-small-latest"
    cache_fn = "mistral-cache.json"

    def __init__(self):
        self.client = Mistral(api_key=config.config['mistral-key'])
        super().__init__()
        logging.debug("Mistral solver set up")

    def make_gpt_request(self, query) -> str:
        logging.debug("Making Mistral request")
        chat_response = self.client.chat.complete(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": query,
                },
            ]
        )
        return chat_response.choices[0].message.content
