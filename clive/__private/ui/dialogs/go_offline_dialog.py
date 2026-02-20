from __future__ import annotations

from typing import TYPE_CHECKING

from textual.widgets import Static

from clive.__private.ui.dialogs.clive_base_dialogs import CliveActionDialog

if TYPE_CHECKING:
    from textual.app import ComposeResult


class GoOfflineDialog(CliveActionDialog):
    def __init__(self) -> None:
        super().__init__(
            border_title="Connection Failed",
            confirm_button_label="Go Offline",
            variant="error",
        )

    def create_dialog_content(self) -> ComposeResult:
        yield Static(
            "Could not connect to the Hive node.\n"
            "Continue in offline mode using cached data?\n"
            "Some features will be unavailable."
        )
