from openai import OpenAI
from typing import Literal

client = OpenAI()


def send_message(message: str, role: Literal['system', 'user',], context: list[dict],
                 model: Literal['gpt-3.5-turbo', 'gpt-4'] = 'gpt-3.5-turbo'):
    context.append({"role": role, "content": message})

    completion = client.chat.completions.create(
        model=model,
        messages=context
    )

    return completion.choices[0].message


if __name__ == "__main__":
    messages = [
        {"role": "system", "content": "You are a hellpfull, sales assistant"}
    ]
    response = send_message("Hello", "system", messages)
    print(response.content)
