from __future__ import annotations

from typing import Callable

from prompt_toolkit.widgets import Button as PromptToolkitButton


class Button(PromptToolkitButton):
    def __init__(self, text: str = "", handler: Callable[[], None] | None = None):
        width = len(text) + 2  # make text centered
        super().__init__(text, handler, width, left_symbol="|", right_symbol="|")
