from __future__ import annotations

import contextlib
from abc import ABC
from typing import TYPE_CHECKING, Any, ClassVar

from textual import on
from textual.binding import Binding
from textual.message import Message
from textual.widgets import Input

from clive.__private.core.keys import PrivateKey, PrivateKeyAliased
from clive.__private.core.profile import Profile
from clive.__private.logger import logger
from clive.__private.settings import safe_settings
from clive.__private.ui.manage_key_aliases.widgets.key_alias_form import KeyAliasForm
from clive.__private.ui.shared.form_screen import FormScreen
from clive.__private.ui.widgets.clive_screen import CliveScreen
from clive.__private.ui.widgets.inputs.clive_validated_input import (
    CliveValidatedInput,
    CliveValidatedInputError,
    FailedManyValidationError,
)
from clive.__private.ui.widgets.inputs.private_key_input import PrivateKeyInput
from clive.__private.ui.widgets.select_file import SelectFile
from clive.exceptions import (
    FormValidationError,
)

if TYPE_CHECKING:
    from pathlib import Path

    from textual.app import ComposeResult

    from clive.__private.ui.shared.form import Form


class NewKeyAliasBase(KeyAliasForm, ABC):
    BINDINGS = [
        Binding("f2", "load_from_file", "Load from file"),
    ]

    SECTION_TITLE: ClassVar[str] = "Add key alias"
    IS_PRIVATE_KEY_REQUIRED: ClassVar[bool] = True

    class Saved(Message, bubble=True):
        """Emitted when user Saves the form."""

        def __init__(self, private_key: PrivateKeyAliased) -> None:
            self.private_key = private_key
            super().__init__()

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # Multiple inheritance friendly, passes arguments to next object in MRO.
        super().__init__(*args, **kwargs)

        self._key_input = PrivateKeyInput(
            value=self._default_private_key(),
            password=True,
            required=self.IS_PRIVATE_KEY_REQUIRED,
            id="key-input",
        )
        self.__key_file_path: Path | None = None

    @property
    def _is_key_provided(self) -> bool:
        return bool(self._key_input.value_raw)

    @property
    def _private_key_aliased(self) -> PrivateKeyAliased:
        """
        Returns a PrivateKeyAliased instance with the given alias and private key value.

        Raises
        ------
        FailedManyValidationError: when cannot create a private key from the given inputs.
        """
        CliveValidatedInput.validate_many_with_error(self._key_input, self._key_alias_input)

        private_key = self._key_input.value_or_error
        key_alias = self._key_alias_input.value_or_error
        return PrivateKeyAliased(value=private_key, file_path=self.__key_file_path, alias=key_alias)

    def action_load_from_file(self) -> None:
        self.app.push_screen(SelectFile(placeholder="e.g. /home/me/my-active-key.wif"))

    @on(SelectFile.Saved)
    def load_private_key_from_file(self, event: SelectFile.Saved) -> None:
        self._key_input.input.value = PrivateKey.read_key_from_file(event.file_path)
        self.__key_file_path = event.file_path
        self.notify(f"Private key loaded from `{event.file_path}`")

    @on(Input.Changed, "#key-input Input")
    def recalculate_public_key(self) -> None:
        try:
            private_key = self._private_key_aliased
        except CliveValidatedInputError:
            text = "Cannot calculate public key"
            calculated = False
        else:
            text = private_key.calculate_public_key().value
            calculated = True

        self._public_key_input.input.value = text
        self._public_key_input.input.set_style("valid" if calculated else "invalid")

    def _save(self) -> None:
        """
        Proceeds with saving the form.

        Raises
        ------
        FailedManyValidationError: when key alias or private key inputs are invalid.
        """
        self._validate()
        self.app.post_message_to_everyone(self.Saved(private_key=self._private_key_aliased))

    def _validate(self) -> None:
        """
        Validate the inputs.

        Raises
        ------
        FailedManyValidationError: when key alias or private key inputs are invalid.
        """
        CliveValidatedInput.validate_many_with_error(self._key_input, self._key_alias_input)

    def _content_after_alias_input(self) -> ComposeResult:
        yield self._key_input

    def _default_private_key(self) -> str:
        return safe_settings.secrets.default_private_key or ""


class NewKeyAlias(NewKeyAliasBase):
    BIG_TITLE = "Configuration"
    SUBTITLE = "Manage key aliases"
    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("f6", "save", "Save"),
    ]

    class FailedValidationAlreadyHandledError(Exception):
        """
        A special error to indicate that the validation error was already shown to the user.

        Needed, because in the Form version of this screen, the validation error has to be converted to
        FormValidationError. It means, we always have to raise some error in the _validate method.
        This one exists because we don't want to show extra notification about the FailedManyValidationError.
        (which without this error, should be raised in _save, otherwise InputValueError would always be ignored).
        """

    @property
    def context(self) -> Profile:
        return self.profile

    @CliveScreen.try_again_after_unlock
    @on(NewKeyAliasBase.Saved)
    async def new_key_alias_base_saved(self, event: NewKeyAliasBase.Saved) -> None:
        self.context.keys.set_to_import([event.private_key])

        await self.commands.sync_data_with_beekeeper()
        self.app.trigger_profile_watchers()
        self.app.post_message_to_screen("ManageKeyAliases", self.Changed())
        self.app.pop_screen()
        self.notify("New key alias was created.")

    def action_save(self) -> None:
        self._save()

    def _save(self) -> None:
        # suppressing the validation error, because it was already shown, and no further logic relies on it in that case
        with contextlib.suppress(self.FailedValidationAlreadyHandledError):
            super()._save()

    def _validate(self) -> None:
        """
        Validate the inputs.

        Shows the validation error to the user. Either by notification when InputValueError occurs or by placing the
        validation failures under the inputs when FailedValidationError occurs.
        Then raises the FailedValidationAlreadyHandledError to exit from methods using this _validate. This error should
        be later suppressed.
        """
        if not CliveValidatedInput.validate_many(self._key_input, self._key_alias_input):
            raise self.FailedValidationAlreadyHandledError


class NewKeyAliasForm(NewKeyAliasBase, FormScreen[Profile]):
    BIG_TITLE = "Onboarding"
    SUBTITLE = "Optional step, could be done later"
    IS_KEY_ALIAS_REQUIRED: ClassVar[bool] = False
    IS_PRIVATE_KEY_REQUIRED: ClassVar[bool] = False

    def __init__(self, owner: Form[Profile]) -> None:
        super().__init__(owner=owner)

    @on(NewKeyAliasBase.Saved)
    def new_key_alias_base_saved(self, event: NewKeyAliasBase.Saved) -> None:
        self.context.keys.set_to_import([event.private_key])
        logger.debug("New private key is waiting to be imported...")

    async def apply_and_validate(self) -> None:
        if self._is_key_provided:  # NewKeyAliasForm step is optional, so we can skip it when no key is provided
            self._save()

    def _validate(self) -> None:
        """
        Validate the inputs.

        Converts the FailedManyValidationError to FormValidationError which can be handled by form later.

        Raises
        ------
        FormValidationError: when key alias or private key inputs are invalid.
        """
        try:
            super()._validate()
        except FailedManyValidationError as error:
            raise FormValidationError(str(error)) from error
