# AI-Chat-TUI

Experimental AI chat TUI to be used with `llama-server` (for now)


## Install and use

```
git clone https://github.com/frans-fuerst/ai-chat-tui.git
cd ai-chat-tui
uv sync
uv run chat
```


## License

See [License.md](License.md).


## Contribution

```bash
git clone https://github.com/frans-fuerst/ai-chat-tui.git
cd ai-chat-tui
uv run pre-commit install
```
.. make your changes and check if they pass the configured gate keepers.

```bash
# run all checks which would be executed on commit, but on unstaged stuff, too
uv run pre-commit run --hook-stage pre-commit --all-files
```


## Wishlist

- [x] Enter 'prompt'
- [x] Continuation
- [ ] CTRL-D (clear)
- [ ] CTRL-C (abort)
- [ ] Multiline input
- [ ] Spoiler for parameters (URL, chat parameters, etc.)
- [ ] Set initial prompt / chat template


## External Sources

* TBD
