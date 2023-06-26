from __future__ import annotations

import typing
from abc import ABC
from typing import TYPE_CHECKING, Any

from textual.binding import Binding
from textual.message import Message
from textual.widgets import Input, Static

from clive.__private.config import settings
from clive.__private.core.keys import PrivateKey, PrivateKeyAliased, PrivateKeyInvalidFormatError
from clive.__private.core.profile_data import ProfileData
from clive.__private.logger import logger
from clive.__private.ui.app_messages import ProfileDataUpdated
from clive.__private.ui.manage_authorities.widgets.authority_form import AuthorityForm, SubTitle
from clive.__private.ui.shared.form_screen import FormScreen
from clive.__private.ui.widgets.clive_screen import CliveScreen
from clive.__private.ui.widgets.notification import Notification
from clive.__private.ui.widgets.select_file import SelectFile
from clive.exceptions import (
    AliasAlreadyInUseFormError,
    FormValidationError,
    PrivateKeyAlreadyInUseError,
    PrivateKeyInvalidFormatFormError,
)

if TYPE_CHECKING:
    from pathlib import Path

    from textual.app import ComposeResult

    from clive.__private.ui.shared.form import Form


class NewAuthorityBase(AuthorityForm, ABC):
    BINDINGS = [
        Binding("f2", "load_from_file", "Load from file"),
    ]

    class Saved(Message, bubble=True):
        """Emitted when user Saves the form"""

        def __init__(self, private_key: PrivateKeyAliased) -> None:
            self.private_key = private_key
            super().__init__()

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # Multiple inheritance friendly, passes arguments to next object in MRO.
        super().__init__(*args, **kwargs)

        self.__key_input = Input(self._default_key(), placeholder="You can paste your key here")
        self.__key_file_path: Path | None = None

    @property
    def _is_key_provided(self) -> bool:
        return bool(self._private_key_raw)

    @property
    def _private_key_raw(self) -> str:
        return self.__key_input.value

    @property
    def _private_key(self) -> PrivateKeyAliased:
        """
        :raises PrivateKeyInvalidFormatError: if private key is not in valid format
        """
        return PrivateKeyAliased(value=self._private_key_raw, file_path=self.__key_file_path, alias=self._key_alias_raw)

    def action_load_from_file(self) -> None:
        self.app.push_screen(SelectFile())

    def on_select_file_saved(self, event: SelectFile.Saved) -> None:
        self.__key_input.value = PrivateKey.read_key_from_file(event.file_path)
        self.__key_file_path = event.file_path
        Notification(f"Authority loaded from `{event.file_path}`", category="success").show()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input == self.__key_input:
            try:
                self._public_key_input.value = self._private_key.calculate_public_key().value
            except PrivateKeyInvalidFormatError:
                self._public_key_input.value = "Invalid form of private key"

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

        self.app.post_message_to_everyone(self.Saved(private_key=self._private_key))

    def _validate(self) -> None:
        """
        Raises:
            PrivateKeyInvalidFormatFormError: if key is invalid
            AliasAlreadyInUseError: if alias is already in use
            PrivateKeyAlreadyInUseError: if private key is already in use
        """
        try:
            self.__check_if_authority_already_exists(self._private_key)
        except PrivateKeyInvalidFormatError:
            raise PrivateKeyInvalidFormatFormError("Invalid form of private key") from None

    def __check_if_authority_already_exists(self, private_key: PrivateKeyAliased) -> None:
        """
        Raises:
            AliasAlreadyInUseFormError: if alias is already in use
            PrivateKeyAlreadyInUseError: if private key is already in use
        """

        def __private_key_already_exists() -> bool:
            return private_key.without_alias() in self.app.world.profile_data.working_account.keys

        if not self.context.working_account.keys.is_public_alias_available(private_key.alias):
            raise AliasAlreadyInUseFormError(private_key.alias)

        if __private_key_already_exists():
            raise PrivateKeyAlreadyInUseError()

    def _content_after_big_title(self) -> ComposeResult:
        if self._subtitle():
            yield SubTitle(self._subtitle())

    def _content_after_alias_input(self) -> ComposeResult:
        yield Static("Key:", classes="label")
        yield self.__key_input

    def _title(self) -> str:
        return "define keys"

    def _subtitle(self) -> str:
        return ""

    def _default_key(self) -> str:
        return typing.cast(str, settings.get("secrets.default_key", ""))

    def _default_authority_name(self) -> str:
        return f"{self.context.working_account.name}@active"


class NewAuthority(NewAuthorityBase):
    BINDINGS = [
        Binding("escape", "pop_screen", "Cancel"),
        Binding("f10", "save", "Save"),
    ]

    @property
    def context(self) -> ProfileData:
        return self.app.world.profile_data

    @CliveScreen.try_again_after_activation()
    def on_new_authority_base_saved(self, event: NewAuthorityBase.Saved) -> None:
        self.context.working_account.keys.set_to_import([event.private_key])

        self.app.world.commands.sync_data_with_beekeeper()
        self.app.post_message_to_everyone(ProfileDataUpdated())
        self.app.post_message_to_screen("ManageAuthorities", self.AuthoritiesChanged())
        self.app.pop_screen()
        Notification("New authority was created.", category="success").show()

    def action_save(self) -> None:
        self._save()


class NewAuthorityForm(NewAuthorityBase, FormScreen[ProfileData]):
    def __init__(self, owner: Form[ProfileData]) -> None:
        super().__init__(owner=owner)

    def on_new_authority_base_saved(self, event: NewAuthorityBase.Saved) -> None:
        self.context.working_account.keys.set_to_import([event.private_key])
        logger.debug("New authority is waiting to be imported...")

    def apply_and_validate(self) -> None:
        if self._is_key_provided:  # NewAuthorityForm step is optional, so we can skip it when no key is provided
            self._save(reraise_exception=True)

    def _subtitle(self) -> str:
        return "(Optional step, could be done later)"
