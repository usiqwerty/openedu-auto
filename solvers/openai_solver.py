import json
import logging
import re

from openai import OpenAI

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
        self.client = OpenAI(api_key=config.config["openai-key"], base_url=config.config["openai-base-url"])

    def make_gpt_request(self, query, *, sysprompt=None, _json=False) -> str:
        messages = [
            {"role": "user", "content": query},
        ]
        if sysprompt:
            messages.insert(0, {"role": "system", "content": sysprompt})
        while True:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=False,
                reasoning_effort=None
            )
            if response.choices is None:
                error = response.model_extra['error']
                logging.critical(f"Error solving")
                logging.critical(f"Code {error['code']}: {error['message']}")
                logging.critical(error['metadata'])
                raise Exception
            content = response.choices[0].message.content
            if not _json:
                break
            else:
                try:
                    json.loads(content)
                    break
                except json.JSONDecodeError as e:
                    logging.error("Could not decode json from LLM")
                    logging.error(e)
                    messages.append({"role": "assistant", "content": content})
                    messages.append({"role": "user", "content": "Невалидный JSON"})
        return content
