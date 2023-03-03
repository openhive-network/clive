from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from textual.containers import Container
from textual.message import Message
from textual.widgets import Button, Input, Switch

from clive.storage.mock_database import PrivateKey
from clive.ui.manage_authorities.widgets.authority_inputs import (
    AuthorityDefinitionFromFile,
    AuthorityInputSwitch,
    RawAuthorityDefinition,
)
from clive.ui.shared.base_screen import BaseScreen
from clive.ui.widgets.big_title import BigTitle
from clive.ui.widgets.view_bag import ViewBag

if TYPE_CHECKING:
    from textual.app import ComposeResult


class AuthorityForm(BaseScreen):
    BINDINGS = [("f10", "save", "Save")]

    class Saved(Message, bubble=True):
        """Emitted when user press Save button"""

        def __init__(self, sender: AuthorityForm, authority: PrivateKey) -> None:
            self.authority = authority
            super().__init__(sender)

    class Canceled(Message, bubble=True):
        """Emitted when user press Cancel button"""

    def _title(self) -> str:
        return ""

    def _default_authority_name(self) -> str:
        return ""

    def _default_raw_authority(self) -> str:
        return ""

    def create_main_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle(self._title())
            yield Input(
                self._default_authority_name(),
                "authority name",
                id="authority_name_input",
            )
            yield AuthorityInputSwitch()
            with Container():
                yield AuthorityDefinitionFromFile(classes="hidden")
                yield RawAuthorityDefinition(self._default_raw_authority())
            yield from self._submit_buttons()

    def _submit_buttons(self) -> ComposeResult:
        with Container(id="user_action_buttons"):
            yield Button("💾 Save", id="authority_edit_save")
            yield Button("🚫 Cancel", id="authority_edit_cancel")

    def action_save(self) -> None:
        name = self.get_widget_by_id("authority_name_input", expect_type=Input).value
        if not self.get_widget_by_id("input_type", expect_type=Switch).value:
            pv_key = PrivateKey(name, self.query_one(RawAuthorityDefinition).value)
        else:
            with Path(self.query_one(AuthorityDefinitionFromFile).value).open("rt") as file:
                pv_key = PrivateKey(name, file.readline().strip("\n"))
        for screen in self.app.screen_stack:
            screen.post_message_no_wait(self.Saved(self, pv_key))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "authority_edit_save":
            self.action_save()
        elif event.button.id == "authority_edit_cancel":
            for screen in self.app.screen_stack:
                screen.post_message_no_wait(self.Canceled(self))
