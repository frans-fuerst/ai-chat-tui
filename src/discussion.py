#!/usr/bin/env python3

import asyncio
from contextlib import suppress

from src.chat import chat_response, load_config


async def discussion() -> None:
    styles = ["\033[1;34m", "\033[1;32;3m"]
    names = ["First one", "Second one"]
    reset = "\033[0m"
    history = [
        "Lass uns über das wichtigste reden, was es deiner Meinung nach im Leben gibt."
    ]

    print(f"{reset}\n=== {names[0]} (0) =====")
    print(styles[0])
    print(history[0], end="")

    while True:
        config = load_config()
        messages = [
            {
                "role": "system",
                "content": config["system-prompt"]
                + ["You are Richard Feynman.", "You are Albert Einstein."][
                    len(history) % 2
                ],
            },
            *(
                {
                    "role": "user" if (i + len(history)) % 2 else "assistant",
                    "content": m,
                }
                for i, m in enumerate(history)
            ),
        ]
        input()  # wait
        print(
            f"{reset}\n=== {names[len(history) % 2]} ({len(history)}) =====\n"
        )
        print(styles[len(history) % 2], end="")
        full_answer = ""
        async for words in chat_response(
            config,
            messages,
        ):
            full_answer += words
            print(words, end="", flush=True)

        history.append(full_answer)


def main() -> None:
    with suppress(KeyboardInterrupt):
        asyncio.run(discussion())


if __name__ == "__main__":
    main()
