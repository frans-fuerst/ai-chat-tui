#!/usr/bin/env python3

import asyncio
import json
from collections.abc import AsyncIterable
from pathlib import Path

import httpx
import yaml
from textual import getters, on, work
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Input, Markdown


def load_config() -> dict[str, float | str]:
    with Path("chatconfig.yaml").open() as config_f:
        return yaml.safe_load(config_f)


async def chat_response(
    config: dict[str, float | str], messages: list[dict[str, str]]
) -> AsyncIterable[str]:
    url = f"{config['server-url']}/v1/chat/completions"
    data = {"stream": True, "messages": messages, **config["request-data"]}
    async with httpx.AsyncClient() as client:
        async with client.stream(
            "POST", url, json=data, timeout=config.get("timeout", 3)
        ) as response:
            if response.status_code != 200:
                raise RuntimeError(
                    f"Error: {response.status_code} / {response}"
                )
            async for line in response.aiter_lines():
                if not line:
                    continue
                try:
                    data = json.loads(line[line.find("{") :])
                    words = data["choices"][0]["delta"].get("content") or ""
                    yield words
                except KeyError as exc:
                    raise RuntimeError(f"Error: {exc!r} data: {data}") from exc
                except json.JSONDecodeError:
                    if line != "data: [DONE]":
                        raise


class ChatApp(App[None]):
    """Chat TUI"""

    CSS_PATH = Path(__file__).parent / "chat.tcss"
    conversation = getters.query_one("#conversation", Markdown)
    prompt_input = getters.query_one("#prompt-input", Input)
    vertical_scroll = getters.query_one(
        "#conversation-container", VerticalScroll
    )
    history: list[str] = []
    conversation_md = ""

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Say something", id="prompt-input")
        with VerticalScroll(id="conversation-container"):
            yield Markdown(id="conversation")

    async def set_conversation_text(self, text: str) -> None:
        self.conversation.update(text)
        self.vertical_scroll.scroll_end(
            animate=False, immediate=True, x_axis=False
        )
        await asyncio.sleep(0.1)

    @on(Input.Submitted, "#prompt-input")
    @work(exclusive=True)
    async def send_prompt_input(self) -> None:
        """Invoke functionality after pressing Return in input field"""
        config = load_config()
        self.history.append(self.prompt_input.value.rstrip())
        self.prompt_input.clear()
        self.conversation_md += f"*{self.history[-1]}*\n\n---\n\n"
        messages = [
            {"role": "system", "content": config["system-prompt"]},
            *(
                {"role": "user" if i % 2 == 0 else "assistant", "content": m}
                for i, m in enumerate(self.history)
            ),
        ]
        await self.set_conversation_text(self.conversation_md)
        full_answer = ""
        async for words in chat_response(config, messages):
            full_answer += words
            await self.set_conversation_text(self.conversation_md + full_answer)

        self.history.append(full_answer)
        self.conversation_md += f"{full_answer}\n\n---\n\n"
        await self.set_conversation_text(self.conversation_md)


def main() -> None:
    ChatApp().run()


if __name__ == "__main__":
    main()
