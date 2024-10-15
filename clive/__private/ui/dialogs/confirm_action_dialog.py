from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.widgets import Static

from clive.__private.ui.dialogs.clive_base_dialogs import CliveActionDialog, CliveDialogVariant
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.widgets.buttons import CancelButton, ConfirmButton
from clive.__private.ui.widgets.section import Section

if TYPE_CHECKING:
    from textual.app import ComposeResult


class ConfirmActionDialog(CliveActionDialog[bool]):
    CSS_PATH = [get_relative_css_path(__file__)]

    def __init__(
        self,
        border_title: str = "Confirm action",
        confirm_question: str = "Are you sure?",
        confirm_button_label: str = "Yes, proceed",
        variant: CliveDialogVariant = "default",
        id_: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(
            border_title=border_title,
            confirm_button_label=confirm_button_label,
            variant=variant,
            id_=id_,
            classes=classes,
        )
        self._confirm_question = confirm_question

    def create_dialog_content(self) -> ComposeResult:
        with Section():
            yield Static(self._confirm_question, id="confirm-question")

    @on(ConfirmButton.Pressed)
    async def confirm_dialog(self) -> None:
        self.dismiss(result=True)

    @on(CancelButton.Pressed)
    def action_cancel(self, event: CancelButton.Pressed) -> None:  # type: ignore[override]
        event.prevent_default()
        self.dismiss(result=False)
