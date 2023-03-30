from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid
from textual.message import Message
from textual.widgets import Input, Static

from clive.__private.storage.mock_database import PrivateKey
from clive.__private.ui.shared.base_screen import BaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.notification import Notification
from clive.__private.ui.widgets.select_file import SelectFile
from clive.__private.ui.widgets.view_bag import ViewBag

if TYPE_CHECKING:
    from pathlib import Path

    from textual.app import ComposeResult


class Body(Grid):
    """Container for body"""


class SubTitle(Static):
    pass


class AuthorityForm(BaseScreen):
    class Saved(Message, bubble=True):
        """Emitted when user Saves the form"""

        def __init__(self, private_key: PrivateKey) -> None:
            self.private_key = private_key
            super().__init__()

    class AuthoritiesChanged(Message):
        """Emitted when authorities have been changed"""

    def __init__(self) -> None:
        super().__init__()

        self.__key_alias_input = Input(self.__generate_key_alias(), placeholder="e.g. My active key", disabled=True)
        self.__key_input = Input(self._default_key(), placeholder="You can paste your key here")
        self.__key_file_path: Path | None = None

    def create_main_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle(self._title())
            if self._subtitle():
                yield SubTitle(self._subtitle())
            with Body():
                yield Static("Key alias:", classes="label")
                yield self.__key_alias_input
                yield Static("Key:", classes="label")
                yield self.__key_input

    def action_load_from_file(self) -> None:
        self.app.push_screen(SelectFile(self._default_file_path()))

    def on_select_file_saved(self, event: SelectFile.Saved) -> None:
        self.__key_input.value = PrivateKey.read_key_from_file(event.file_path)
        self.__key_file_path = event.file_path
        Notification(f"Authority loaded from `{event.file_path}`", category="success").show()

    def _save(self) -> None:
        if not self.__is_valid():
            Notification("Failed the validation process! Could not continue", category="error").show()
            return

        private_key = PrivateKey(self.__get_authority_name(), self._get_key(), self.__key_file_path)
        self.app.post_message_to_everyone(self.Saved(private_key))

    def _title(self) -> str:
        return ""

    def _subtitle(self) -> str:
        return ""

    def _default_authority_name(self) -> str:
        return ""

    def _default_key(self) -> str:
        return ""

    def _default_file_path(self) -> str:
        return ""

    def __get_authority_name(self) -> str:
        return self.__key_alias_input.value

    def _get_key(self) -> str:
        return PrivateKey.validate_key(self.__key_input.value)

    def __is_valid(self) -> bool:
        return bool(self._get_key()) and bool(self.__get_authority_name())

    def __generate_key_alias(self) -> str:
        return f"{self.app.profile_data.working_account.name}@active"
