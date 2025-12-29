#!/usr/bin/env python3

import asyncio
import json
from pathlib import Path

import httpx
import yaml
from textual import getters, on, work
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Input, Markdown


class ChatApp(App[None]):
    """Chat TUI"""

    CSS_PATH = Path(__file__).parent / "chat.tcss"
    conversation = getters.query_one("#conversation", Markdown)
    prompt_input = getters.query_one("#prompt-input", Input)
    messages = []  # type: ignore[var-annotated]
    conversation_md = ""

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Say something", id="prompt-input")
        with VerticalScroll(id="conversation-container"):
            yield Markdown(id="conversation")

    @on(Input.Submitted, "#prompt-input")
    @work(exclusive=True)
    async def send_prompt_input(self) -> None:
        """Invoke functionality after pressing Return in input field"""
        url = "http://127.0.0.1:9000/v1/chat/completions"
        user_input = self.prompt_input.value.rstrip()
        self.prompt_input.clear()
        self.conversation_md += f"*{user_input}*\n\n---\n\n"
        self.conversation.update(self.conversation_md)
        self.messages.append({"role": "user", "content": user_input})
        data = {
            "stream": True,
            # "prompt": f"User: {self.prompt_input.value.rstrip()}",
            "messages": self.messages,
            "max_tokens": -1,
            # "temperature": 0.0,  # 0.7,
            # "top_p": 1.0,  # 0.9,
        }
        answer = ""
        async with httpx.AsyncClient() as client:
            async with client.stream("POST", url, json=data) as response:
                if response.status_code != 200:
                    self.conversation.update(
                        f"Error: {response.status_code} / {response}"
                    )
                    return
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    try:
                        data = json.loads(line[line.find("{") :])
                        answer += (
                            data["choices"][0]["delta"].get("content") or ""
                        )
                        self.conversation.update(self.conversation_md + answer)
                        await asyncio.sleep(0.1)
                    except KeyError:
                        self.conversation.update(
                            f"\n\n```yaml\n{yaml.dump(data)}\n```\n\n"
                        )
                        return
                    except json.JSONDecodeError:
                        if line != "data: [DONE]":
                            raise

        self.messages.append({"role": "assistant", "content": answer})
        self.conversation_md += f"{answer}\n\n---\n\n"
        self.conversation.update(self.conversation_md)


def main() -> None:
    ChatApp().run()


if __name__ == "__main__":
    main()
