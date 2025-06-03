from __future__ import annotations

from typing import TYPE_CHECKING, Any

from textual import on
from textual.widgets import Input

from clive.__private.core.keys import KeyAliasAlreadyInUseError, PrivateKey, PrivateKeyAliased
from clive.__private.settings import safe_settings
from clive.__private.ui.clive_dom_node import CliveDOMNode
from clive.__private.ui.widgets.inputs.clive_validated_input import (
    CliveValidatedInput,
    CliveValidatedInputError,
)
from clive.__private.ui.widgets.inputs.labelized_input import LabelizedInput
from clive.__private.ui.widgets.inputs.private_key_input import PrivateKeyInput
from clive.__private.ui.widgets.inputs.public_key_alias_input import PublicKeyAliasInput
from clive.__private.validators.private_key_validator import PrivateKeyValidator

if TYPE_CHECKING:
    from collections.abc import Callable

    from textual.app import ComposeResult

    from clive.__private.core.keys import PublicKey


class KeyAliasBase(CliveDOMNode):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._key_alias_input = PublicKeyAliasInput(
            value=self._default_key_alias_name(),
            setting_key_alias=True,
            key_manager=self.app.world.profile.keys,
            required=False,
        )
        self._key_alias_input.clear_validation(clear_value=False)
        self._public_key_input = LabelizedInput(
            "Public key", self._default_public_key() or "will be calculated here", id="public-key"
        )

    def _default_key_alias_name(self) -> str:
        return ""

    def _default_private_key(self) -> str:
        return safe_settings.secrets.default_private_key or ""

    def _default_public_key(self) -> str:
        return ""

    def _handle_key_alias_change(self, func: Callable[[], None], success_message: str | None = None) -> bool:
        try:
            func()
        except KeyAliasAlreadyInUseError:
            self.app.notify(
                "Can't proceed because such alias already exists. Use explicit name or remove the old alias.",
                severity="error",
            )
            return False

        if success_message is not None:
            self.app.notify(success_message)
        return True


class NewKeyAliasBase(KeyAliasBase):
    def __init__(self, public_key_to_match: str | PublicKey | None = None, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._key_input = PrivateKeyInput(
            value=self._default_private_key(),
            password=True,
            required=True,
            id="key-input",
            validators=PrivateKeyValidator(public_key_to_match=public_key_to_match),
        )

    @property
    def _private_key(self) -> PrivateKey:
        """
        Returns a PrivateKey instance with the given private key value.

        Raises
        ------
        FailedValidationError: When given input is not a valid private key.
        """
        self._key_input.validate_with_error()
        return PrivateKey(value=self._key_input.value_or_error, file_path=None)

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
        return PrivateKeyAliased(value=private_key, file_path=None, alias=self._get_key_alias())

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

    def _content_after_alias_input(self) -> ComposeResult:
        yield self._key_input

    def _get_key_alias(self) -> str:
        if self._key_alias_input.is_empty:
            return self._private_key.calculate_public_key().value
        return self._key_alias_input.value_or_error

    async def _import_new_key(self) -> None:
        await self.app.world.commands.sync_data_with_beekeeper()
        self.app.notify("New key alias was created.")
        self.app.trigger_profile_watchers()

    def _validate(self) -> None:
        """
        Validate the inputs.

        Raises
        ------
        FailedManyValidationError: when key alias / private key inputs are invalid or private key does
        not match given public key.
        """
        CliveValidatedInput.validate_many_with_error(*self._get_inputs_to_validate())

    def _get_inputs_to_validate(self) -> list[PrivateKeyInput | PublicKeyAliasInput]:
        inputs_to_validate: list[PrivateKeyInput | PublicKeyAliasInput] = [self._key_input]

        if not self._key_alias_input.is_empty:
            inputs_to_validate.append(self._key_alias_input)

        return inputs_to_validate
