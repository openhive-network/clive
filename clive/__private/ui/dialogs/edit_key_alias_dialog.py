from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.dialogs.clive_base_dialogs import CliveActionDialog
from clive.__private.ui.screens.config.manage_key_aliases.key_alias_base import KeyAliasBase
from clive.__private.ui.widgets.inputs.clive_validated_input import (
    FailedValidationError,
    InputValueError,
)
from clive.__private.ui.widgets.select_copy_paste_hint import SelectCopyPasteHint

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
        SelectCopyPasteHint {
            margin: 1 1 0 1;
        }
    }
    """

    def __init__(self, public_key: PublicKeyAliased) -> None:
        self._public_key = public_key
        super().__init__("Edit key alias")

    def create_dialog_content(self) -> ComposeResult:
        yield self._public_key_input
        yield self._key_alias_input
        yield SelectCopyPasteHint()

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

        Raises
        ------
        FailedValidationError: when key alias is not valid.
        """
        if not self._key_alias_input.is_empty:
            self._key_alias_input.validate_with_error()

    def _get_key_alias(self) -> str:
        if self._key_alias_input.is_empty:
            return self._public_key.value
        return self._key_alias_input.value_or_error

    def _default_key_alias_name(self) -> str:
        return self._public_key.alias

    def _default_public_key(self) -> str:
        return self._public_key.value
