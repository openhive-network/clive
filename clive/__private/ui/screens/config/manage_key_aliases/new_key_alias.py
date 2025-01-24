from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Any, ClassVar

from textual import on
from textual.binding import Binding
from textual.widgets import Input

from clive.__private.core.constants.tui.placeholders import KEY_FILE_PATH_PLACEHOLDER
from clive.__private.core.keys import PrivateKey, PrivateKeyAliased
from clive.__private.core.profile import Profile
from clive.__private.settings import safe_settings
from clive.__private.ui.screens.config.manage_key_aliases.widgets.key_alias_form import (
    KeyAliasForm,
    KeyAliasFormContextT,
)
from clive.__private.ui.widgets.inputs.clive_input import CliveInput
from clive.__private.ui.widgets.inputs.clive_validated_input import (
    CliveValidatedInput,
    CliveValidatedInputError,
    FailedManyValidationError,
)
from clive.__private.ui.widgets.inputs.private_key_input import PrivateKeyInput
from clive.__private.ui.widgets.select_file import SaveFileResult, SelectFile

if TYPE_CHECKING:
    from pathlib import Path

    from textual.app import ComposeResult

    from clive.__private.ui.widgets.inputs.public_key_alias_input import PublicKeyAliasInput


class NewKeyAliasBase(KeyAliasForm[KeyAliasFormContextT], ABC):
    BINDINGS = [
        Binding("f2", "load_from_file", "Load from file"),
    ]

    SECTION_TITLE: ClassVar[str] = "Add key alias"
    IS_PRIVATE_KEY_REQUIRED: ClassVar[bool] = True

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
    def _private_key(self) -> PrivateKey:
        """
        Returns a PrivateKey instance with the given private key value.

        Raises
        ------
        FailedCliveInputValidationError: When given input is not a valid private key.
        """
        self._key_input.validate_with_error()
        return PrivateKey(value=self._key_input.value_or_error, file_path=self.__key_file_path)

    @property
    def _private_key_aliased(self) -> PrivateKeyAliased:
        """
        Returns a PrivateKeyAliased instance with the given alias and private key value.

        Raises
        ------
        FailedManyValidationError: when cannot create a private key from the given inputs.
        """
        CliveValidatedInput.validate_many_with_error(*self._get_inputs_to_validate())

        private_key = self._key_input.value_or_error
        return PrivateKeyAliased(value=private_key, file_path=self.__key_file_path, alias=self._get_key_alias())

    def action_load_from_file(self) -> None:
        self.app.push_screen(SelectFile(placeholder=KEY_FILE_PATH_PLACEHOLDER), self._load_private_key_from_file)

    def _load_private_key_from_file(self, result: SaveFileResult | None) -> None:
        if result is None:
            return

        file_path = result.file_path
        self._key_input.input.value = PrivateKey.read_key_from_file(file_path)
        self.__key_file_path = file_path
        self.notify(f"Private key loaded from `{file_path}`")

    @on(Input.Changed, "#key-input Input")
    def recalculate_public_key(self) -> None:
        try:
            private_key = self._private_key
        except CliveValidatedInputError:
            text = "Cannot calculate public key"
            calculated = False
        else:
            text = private_key.calculate_public_key().value
            calculated = True

        self._public_key_input.input.value = text
        self._public_key_input.input.set_style("valid" if calculated else "invalid")

    def _validate(self) -> None:
        """
        Validate the inputs.

        Raises
        ------
        FailedManyValidationError: when key alias or private key inputs are invalid.
        """
        CliveValidatedInput.validate_many_with_error(*self._get_inputs_to_validate())

    def _get_inputs_to_validate(self) -> list[PrivateKeyInput | PublicKeyAliasInput]:
        inputs_to_validate: list[PrivateKeyInput | PublicKeyAliasInput] = [self._key_input]

        if not self._key_alias_input.is_empty:
            inputs_to_validate.append(self._key_alias_input)

        return inputs_to_validate

    def _content_after_alias_input(self) -> ComposeResult:
        yield self._key_input

    def _default_private_key(self) -> str:
        return safe_settings.secrets.default_private_key or ""

    def _get_key_alias(self) -> str:
        if self._key_alias_input.is_empty:
            return self._private_key.calculate_public_key().value
        return self._key_alias_input.value_or_error


class NewKeyAlias(NewKeyAliasBase[Profile]):
    BIG_TITLE = "Configuration"
    SUBTITLE = "Manage key aliases"
    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("f6", "save", "Save"),
    ]

    @property
    def context(self) -> Profile:
        return self.profile

    @on(CliveInput.Submitted)
    async def action_save(self) -> None:
        try:
            self._validate()
        except FailedManyValidationError:
            return

        self.context.keys.set_to_import([self._private_key_aliased])
        await self._import_new_key()
        self.dismiss()

    async def _import_new_key(self) -> None:
        await self.commands.sync_data_with_beekeeper()
        self.notify("New key alias was created.")
        self.app.trigger_profile_watchers()
