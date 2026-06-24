import logging
import re

from openai import OpenAI, Omit

import config
from solvers.llm_solver import LLMSolver


class GenericOpenAISolver(LLMSolver):
    client: OpenAI
    model = config.config["openai-model"]
    cache_fn = "openai-cache.json"

    def __init__(self, model: str | None = None):
        super().__init__()
        if model is not None:
            logging.info(f"Model overriden: {model}")
            self.model = model
            self.cache_fn = re.sub(r"\W", "_", model) + self.cache_fn
            self._cache = self.load_cache()
        self.client = OpenAI(api_key=config.config["openai-key"], base_url=config.config["openai-base-url"])

    def make_gpt_request(self, query, *, sysprompt=None, _json: type | None = None) -> str:
        messages = [
            {"role": "user", "content": query},
        ]
        if sysprompt:
            messages.insert(0, {"role": "system", "content": sysprompt})
        response = self.client.responses.parse(
            text_format=_json if _json else Omit(),
            model=self.model,
            input=messages,
            stream=False,
            reasoning={"effort": "low"},
        )
        if response.error:
            error = response.model_extra['error']
            logging.critical("Error solving")
            logging.critical(f"Code {error['code']}: {error['message']}")
            logging.critical(error['metadata'])
            raise Exception
        if not _json:
            return response.output_text
        else:
            return response.output_parsed.result
