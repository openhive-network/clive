from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

from textual.containers import Horizontal
from textual.widgets import Button

if TYPE_CHECKING:
    from textual.app import ComposeResult


class AuthoritySubmitButtons(Horizontal):
    def __init__(self, on_save: Callable[[], None], on_close: Callable[[], None], **kwargs: Any) -> None:
        self.on_save = on_save
        self.on_close = on_close
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        yield Button("💾 Save", id="authority_edit_save")
        yield Button("🚫 Cancel", id="authority_edit_cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "authority_edit_save":
            self.on_save()
        elif event.button.id == "authority_edit_cancel":
            self.on_close()
