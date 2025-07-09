from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.dialogs.clive_base_dialogs import CliveActionDialog
from clive.__private.ui.key_alias_base import KeyAliasBase
from clive.__private.ui.widgets.inputs.clive_validated_input import (
    FailedValidationError,
    InputValueError,
)

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.core.keys import PublicKeyAliased


class EditKeyAliasDialog(CliveActionDialog, KeyAliasBase):
    DEFAULT_CSS = """
    EditKeyAliasDialog {
        CliveDialogContent {
            width: 85%;

        #public-key, PublicKeyAliasInput {
            margin-top: 1;
            }
        }
    }
    """

    def __init__(self, public_key: PublicKeyAliased) -> None:
        super().__init__("Edit key alias")
        self._public_key = public_key

    def create_dialog_content(self) -> ComposeResult:
        yield self._create_public_key_input()
        yield self._create_key_alias_input()

    async def _perform_confirmation(self) -> bool:
        return self._save()

    def _save(self) -> bool:
        try:
            self._validate()
        except FailedValidationError:
            return False  # Validation errors are already displayed.
        except InputValueError as error:
            self.notify(str(error), severity="error")
            return False

        old_alias = self._public_key.alias
        new_alias = self._get_key_alias()

        success_message = f"Key alias `{self._public_key.alias}` was edited."

        def rename_key_alias() -> None:
            self.profile.keys.rename(old_alias, new_alias)

        if not self._handle_key_alias_change(rename_key_alias, success_message):
            return False

        self.app.trigger_profile_watchers()
        return True

    def _validate(self) -> None:
        """
        Validate the inputs.

        Raises:
            FailedValidationError: when key alias is not valid.
        """
        key_alias_input = self.key_alias_input
        if not key_alias_input.is_empty:
            key_alias_input.validate_with_error()

    def _get_key_alias(self) -> str:
        key_alias_input = self.key_alias_input
        if key_alias_input.is_empty:
            return self._public_key.value
        return key_alias_input.value_or_error

    def _default_key_alias_name(self) -> str:
        return self._public_key.alias

    def _default_public_key(self) -> str:
        return self._public_key.value
