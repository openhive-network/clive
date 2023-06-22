from __future__ import annotations

import typing
from abc import ABC
from typing import TYPE_CHECKING, Any

from textual.containers import Grid
from textual.message import Message
from textual.widgets import Input, Static

from clive.__private.config import settings
from clive.__private.core.keys.keys import PrivateKey, PrivateKeyInvalidFormatError
from clive.__private.core.profile_data import ProfileData
from clive.__private.storage.contextual import Contextual
from clive.__private.ui.shared.base_screen import BaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.notification import Notification
from clive.__private.ui.widgets.select_file import SelectFile
from clive.__private.ui.widgets.view_bag import ViewBag
from clive.exceptions import (
    AliasAlreadyInUseError,
    FormValidationError,
    PrivateKeyAlreadyInUseError,
    PrivateKeyInvalidFormatFormError,
)

if TYPE_CHECKING:
    from pathlib import Path

    from textual.app import ComposeResult


class Body(Grid):
    """Container for body"""


class SubTitle(Static):
    pass


class AuthorityForm(BaseScreen, Contextual[ProfileData], ABC):
    class Saved(Message, bubble=True):
        """Emitted when user Saves the form"""

        def __init__(self, key_alias: str, private_key: PrivateKey) -> None:
            self.key_alias = key_alias
            self.private_key = private_key
            super().__init__()

    class AuthoritiesChanged(Message):
        """Emitted when authorities have been changed"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # Multiple inheritance friendly, passes arguments to next object in MRO.
        super().__init__(*args, **kwargs)

        self.__key_alias_input = Input(self.__generate_key_alias(), placeholder="e.g. My active key")
        self.__key_input = Input(self._default_key(), placeholder="You can paste your key here")
        self.__public_key_input = Input(
            self._default_public_key(), placeholder="Public key will be calculated here", disabled=True
        )
        self.__key_file_path: Path | None = None

    @property
    def _is_key_provided(self) -> bool:
        return bool(self._private_key_raw)

    @property
    def _key_alias_raw(self) -> str:
        return self.__key_alias_input.value

    @property
    def _private_key_raw(self) -> str:
        return self.__key_input.value

    @property
    def _private_key(self) -> PrivateKey:
        """
        :raises PrivateKeyInvalidFormatError: if private key is not in valid format
        """
        return PrivateKey(value=self._private_key_raw, file_path=self.__key_file_path)

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
                yield Static("Public key:", classes="label")
                yield self.__public_key_input

    def action_load_from_file(self) -> None:
        self.app.push_screen(SelectFile())

    def on_select_file_saved(self, event: SelectFile.Saved) -> None:
        self.__key_input.value = PrivateKey.read_key_from_file(event.file_path)
        self.__key_file_path = event.file_path
        Notification(f"Authority loaded from `{event.file_path}`", category="success").show()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input == self.__key_input:
            try:
                self.__public_key_input.value = self._private_key.calculate_public_key().value
            except PrivateKeyInvalidFormatError:
                self.__public_key_input.value = "Invalid form of private key"

    def _save(self, reraise_exception: bool = False) -> None:
        if not self._is_key_provided:
            Notification("Not saving any private key, because none has been provided", category="warning").show()
            return

        try:
            self._validate()
        except FormValidationError as error:
            Notification(
                f"Failed the validation process! Could not continue. Reason: {error.reason}", category="error"
            ).show()
            if reraise_exception:
                raise
            return

        self.app.post_message_to_everyone(self.Saved(key_alias=self._key_alias_raw, private_key=self._private_key))

    def _title(self) -> str:
        return ""

    def _subtitle(self) -> str:
        return ""

    def _default_authority_name(self) -> str:
        return ""

    def _default_public_key(self) -> str:
        return ""

    def _default_key(self) -> str:
        return typing.cast(str, settings.get("secrets.default_key", ""))

    def _validate(self) -> None:
        """
        Raises:
            PrivateKeyInvalidFormatFormError: if key is invalid
            AliasAlreadyInUseError: if alias is already in use
            PrivateKeyAlreadyInUseError: if private key is already in use
        """
        try:
            self.__check_if_authority_already_exists(self._key_alias_raw, self._private_key)
        except PrivateKeyInvalidFormatError:
            raise PrivateKeyInvalidFormatFormError("Invalid form of private key") from None

    def __generate_key_alias(self) -> str:
        return f"{self.context.working_account.name}@active"

    def __check_if_authority_already_exists(self, key_alias: str, private_key: PrivateKey) -> None:
        """
        Raises:
            AliasAlreadyInUseError: if alias is already in use
            PrivateKeyAlreadyInUseError: if private key is already in use
        """

        def __alias_already_exists() -> bool:
            return key_alias in (key.alias for key in self.context.working_account.keys)

        def __private_key_already_exists() -> bool:
            return private_key in self.app.world.profile_data.working_account.keys

        if __alias_already_exists():
            raise AliasAlreadyInUseError(key_alias)

        if __private_key_already_exists():
            raise PrivateKeyAlreadyInUseError()
