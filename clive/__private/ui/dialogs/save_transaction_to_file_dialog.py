from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Horizontal
from textual.widgets import Checkbox

from clive.__private.ui.dialogs.select_file_base_dialog import SelectFileBaseDialog
from clive.__private.ui.styling import colorize_path

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.core.keys.keys import PublicKey
    from clive.__private.validators.path_validator import PathValidator


class Switches(Horizontal):
    """Container for the switches."""

    DEFAULT_CSS = """
    Switches {
        margin: 1 0;
        height: auto;
    }
    """


class SaveTransactionToFileDialog(SelectFileBaseDialog[bool]):
    def __init__(self, sign_key: PublicKey | None) -> None:
        super().__init__("Save transaction to file", "Save file")
        self._sign_key = sign_key

    @property
    def _is_binary_checked(self) -> bool:
        return self.query_exactly_one("#binary-checkbox", Checkbox).value

    @property
    def _is_signed_checked(self) -> bool:
        return self.query_exactly_one("#signed-checkbox", Checkbox).value

    def additional_content_after_input(self) -> ComposeResult:
        with Switches():
            yield Checkbox("Binary?", id="binary-checkbox")
            yield Checkbox("Signed?", disabled=not self.profile.keys, id="signed-checkbox")

    async def _perform_confirmation(self) -> bool:
        return await self._save_transaction_to_file()

    async def _save_transaction_to_file(self) -> bool:
        file_path = self._file_path_input.value_or_none()
        if file_path is None:
            return False

        save_as_binary = self._is_binary_checked
        should_be_signed = self._is_signed_checked
        transaction = self.profile.transaction.copy()

        if should_be_signed and not transaction.is_signed and self._sign_key is None:
            self.notify("Transaction can't be saved because no key was selected.", severity="error")
            return False

        wrapper = await self.commands.perform_actions_on_transaction(
            content=transaction,
            sign_key=self._sign_key,
            force_unsign=not should_be_signed,
            save_file_path=file_path,
            force_save_format="bin" if save_as_binary else "json",
        )

        if wrapper.error_occurred:
            self.notify("Transaction save failed. Please try again.", severity="error")
            return False

        self.profile.transaction.reset()
        self.profile.transaction_file_path = None
        self.app.trigger_profile_watchers()
        self.notify(
            f"Transaction ({'binary' if save_as_binary else 'json'}) saved to {colorize_path(file_path)}"
            f" {'(signed)' if transaction.is_signed else ''}"
        )
        return True

    def _default_validator_mode(self) -> PathValidator.Modes:
        return "is_file_or_can_be_file"
