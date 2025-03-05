from openai import OpenAI

import config


def a():
    client = OpenAI(api_key=config.config["openai-key"], base_url=config.config["openai-base-url"])

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "Hello"},
        ],
        stream=False
    )

    print(response.choices[0].message.content)
