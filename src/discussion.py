#!/usr/bin/env python3

import asyncio
import json
from contextlib import suppress

import httpx
import yaml
from rich import print as rich_print


async def get_answer(messages: list[dict[str, str]]) -> str:
    url = "http://127.0.0.1:9000/v1/chat/completions"
    data = {
        "stream": True,
        "messages": messages,
        "max_tokens": -1,
        "temperature": 0.8,
        "top_p": 1.0,  # 0.9,
    }
    answer = ""
    async with httpx.AsyncClient() as client:
        async with client.stream("POST", url, json=data) as response:
            if response.status_code != 200:
                print(f"Error: {response.status_code} / {response}")
                raise SystemExit(1)
            async for line in response.aiter_lines():
                if not line:
                    continue
                try:
                    data = json.loads(line[line.find("{") :])
                    words = data["choices"][0]["delta"].get("content") or ""
                    answer += words
                    print(words, end="", flush=True)
                except KeyError:
                    print(yaml.dump(data))
                    raise
                except json.JSONDecodeError:
                    if line != "data: [DONE]":
                        raise

    return answer


async def discussion() -> None:
    system = (
        "You are an intelligent constructively thinking, wise nerd."
        " You're interested in physics, metaphysics, meaning of life."
        " You think twice and your answer is short and concise."
    )
    history = [
        "Lass uns über das wichtigste reden, was es deiner Meinung nach im Leben gibt."
    ]
    print("\033[1;34m")
    print(history[0])
    while True:
        print("\033[0m")
        input()
        rich_print(
            f"\n\n=== {'Second' if len(history) % 2 else 'First'} ({len(history)}) =====\n"
        )
        rich_print("\033[1;32;3m" if len(history) % 2 else "\033[1;34m")
        history.append(
            await get_answer(
                [
                    {"role": "system", "content": system},
                    *(
                        {
                            "role": "user"
                            if (i + len(history)) % 2
                            else "assistant",
                            "content": m,
                        }
                        for i, m in enumerate(history)
                    ),
                ]
            )
        )
        await asyncio.sleep(10)


def main() -> None:
    with suppress(KeyboardInterrupt):
        asyncio.run(discussion())


if __name__ == "__main__":
    main()
