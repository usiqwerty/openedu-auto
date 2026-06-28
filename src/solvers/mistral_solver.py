import logging

from mistralai import Mistral
from mistralai import UserMessageTypedDict

from src import config
from src.solvers.llm_solver import LLMSolver


class MistralSolver(LLMSolver):
    model = "mistral-small-latest"
    cache_fn = "mistral-cache.json"

    def __init__(self):
        self.client = Mistral(api_key=config.config['mistral-key'])
        super().__init__()
        logging.debug("Mistral solver set up")

    def make_gpt_request(self, query, *, sysprompt, _json) -> str:
        logging.debug("Making Mistral request")
        messages: list[UserMessageTypedDict] = [
            UserMessageTypedDict(role="user", content=query)
        ]
        chat_response = self.client.chat.complete(
            model=self.model,
            messages=messages
        )
        assert chat_response.choices
        return chat_response.choices[0].message.content
