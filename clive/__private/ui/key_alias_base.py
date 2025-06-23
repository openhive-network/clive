from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.widgets import Input

from clive.__private.abstract_class import AbstractClassMessagePump
from clive.__private.core.keys import KeyAliasAlreadyInUseError, PrivateKey, PrivateKeyAliased
from clive.__private.settings import safe_settings
from clive.__private.ui.bindings.clive_bindings import CLIVE_PREDEFINED_BINDINGS
from clive.__private.ui.clive_dom_node import CliveDOMNode
from clive.__private.ui.widgets.buttons import LoadFromFileButton, LoadFromFileOneLineButton
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

    from clive.__private.core.keys import PublicKey


class KeyAliasBase(CliveDOMNode, AbstractClassMessagePump):
    @property
    def key_alias_input(self) -> PublicKeyAliasInput:
        return self.query_exactly_one(PublicKeyAliasInput)

    @property
    def public_key_input(self) -> LabelizedInput:
        return self.query_exactly_one(LabelizedInput)

    def _create_key_alias_input(self) -> PublicKeyAliasInput:
        key_alias_input = PublicKeyAliasInput(
            value=self._default_key_alias_name(),
            setting_key_alias=True,
            key_manager=self.app.world.profile.keys,
            required=False,
        )
        key_alias_input.clear_validation(clear_value=False)
        return key_alias_input

    def _create_public_key_input(self) -> LabelizedInput:
        return LabelizedInput("Public key", self._default_public_key() or "will be calculated here", id="public-key")

    def _default_key_alias_name(self) -> str:
        return ""

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


class NewKeyAliasBase(KeyAliasBase, AbstractClassMessagePump):
    BINDINGS = [
        CLIVE_PREDEFINED_BINDINGS.manage_key_aliases.load_from_file.create(),
    ]

    @property
    def private_key_input(self) -> PrivateKeyInput:
        return self.query_exactly_one(PrivateKeyInput)

    @property
    def _private_key(self) -> PrivateKey:
        """
        Returns a PrivateKey instance with the given private key value.

        Raises:
            FailedValidationError: When given private key input is invalid.
        """
        private_key_input = self.private_key_input
        private_key_input.validate_with_error()
        return PrivateKey(value=private_key_input.value_or_error, file_path=None)

    @property
    def _private_key_aliased(self) -> PrivateKeyAliased:
        """
        Returns a PrivateKeyAliased instance with the given alias and private key value.

        Raises:
            FailedManyValidationError: When given private key and alias inputs are not valid.
        """
        CliveValidatedInput.validate_many_with_error(*self._get_inputs_to_validate())

        private_key = self.private_key_input.value_or_error
        return PrivateKeyAliased(value=private_key, file_path=None, alias=self._get_key_alias())

    @on(LoadFromFileButton.Pressed)
    @on(LoadFromFileOneLineButton.Pressed)
    def action_load_from_file(self) -> None:
        from clive.__private.ui.dialogs import LoadKeyFromFileDialog  # noqa: PLC0415

        def load_key_into_input(loaded_private_key: PrivateKey | None) -> None:
            if loaded_private_key is None:
                return

            self.private_key_input.input.value = loaded_private_key.value

        self.app.push_screen(LoadKeyFromFileDialog(), load_key_into_input)

    @on(Input.Changed, "#key-input Input")
    def _recalculate_public_key(self) -> None:
        try:
            private_key = self._private_key
        except CliveValidatedInputError:
            text = "Cannot calculate public key"
            calculated = False
        else:
            text = private_key.calculate_public_key().value
            calculated = True

        public_key_input = self.public_key_input
        public_key_input.input.value = text
        public_key_input.input.set_style("valid" if calculated else "invalid")

    def _create_private_key_input(self) -> PrivateKeyInput:
        return PrivateKeyInput(
            value=self._default_private_key(),
            password=True,
            required=self._default_private_key_input_required(),
            id="key-input",
            validators=PrivateKeyValidator(public_key_to_match=self._default_public_key_to_match()),
        )

    def _default_private_key(self) -> str:
        return safe_settings.secrets.default_private_key or ""

    def _default_private_key_input_required(self) -> bool:
        return True

    def _default_public_key_to_match(self) -> PublicKey | None:
        return None

    def _get_key_alias(self) -> str:
        key_alias_input = self.key_alias_input
        if key_alias_input.is_empty:
            return self._private_key.calculate_public_key().value
        return key_alias_input.value_or_error

    def _set_key_alias_to_import(self) -> None:
        self.app.world.profile.keys.set_to_import([self._private_key_aliased])

    def _validate(self) -> None:
        """
        Validate the inputs.

        Raises:
            FailedManyValidationError: When any of the given inputs is invalid.
        """
        CliveValidatedInput.validate_many_with_error(*self._get_inputs_to_validate())

    def _get_inputs_to_validate(self) -> list[PrivateKeyInput | PublicKeyAliasInput]:
        inputs_to_validate: list[PrivateKeyInput | PublicKeyAliasInput] = [self.private_key_input]

        key_alias_input = self.key_alias_input
        if not key_alias_input.is_empty:
            inputs_to_validate.append(key_alias_input)

        return inputs_to_validate
