from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.binding import Binding
from textual.containers import Center
from textual.widgets import Pretty

from clive.__private.ui.dialogs.clive_base_dialogs import CliveActionDialog
from clive.__private.ui.widgets.buttons import ConfirmOneLineButton
from clive.__private.ui.widgets.section import Section

if TYPE_CHECKING:
    from textual import events
    from textual.app import ComposeResult


class ReadKeyDialog(CliveActionDialog):
    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "confirm", "Confirm"),
    ]

    def __init__(self, *, description: str) -> None:
        super().__init__("Read key")
        self._description = description
        self._key: str | None = None

    def create_dialog_content(self) -> ComposeResult:
        with Center(), Section():
            message = f"Press key for action `{self._description}`"
            if self._key is not None:
                message += f" (current key is `{self._key}`)"
            yield Pretty(message)

    async def handle_key(self, event: events.Key) -> bool:
        if event.key in ("enter", "escape"):
            return True
        self._key = event.key
        self.refresh(recompose=True)
        return True

    @on(ConfirmOneLineButton.Pressed)
    async def _confirm_with_button(self) -> None:
        """Pressing the confirm button will confirm the dialog."""
        await self._confirm()

    async def _action_confirm(self) -> None:
        """Pressing the enter key binding will confirm the dialog."""
        await self._confirm()

    async def _confirm(self) -> None:
        if self._key is not None:
            message = f"Key for action `{self._description}` will be set to `{self._key}`,"
        else:
            message = f"Binding for action `{self._description}` will be removed,"
        message += " you must validate and apply all changes."
        self.notify(message)
        await self.confirm_dialog()
