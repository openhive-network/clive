from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Horizontal
from textual.widgets import Checkbox

from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.dialogs.save_file_base_dialog import SaveFileBaseDialog
from clive.__private.ui.styling import colorize_path

if TYPE_CHECKING:
    from pathlib import Path

    from textual.app import ComposeResult

    from clive.__private.core.keys.keys import PublicKey


class Switches(Horizontal):
    """Container for the switches."""

    DEFAULT_CSS = """
    Switches {
        margin: 1 0;
        height: auto;
    }
    """


class BinaryCheckbox(Checkbox):
    def __init__(self) -> None:
        super().__init__("Binary?")


class SignedCheckbox(Checkbox, CliveWidget):
    def __init__(self) -> None:
        super().__init__("Signed?", value=self._initial_value, disabled=self._should_be_disabled)

    @property
    def _initial_value(self) -> bool:
        return self.profile.transaction.is_signed

    @property
    def _should_be_disabled(self) -> bool:
        """
        Determine if the checkbox should be disabled.

        The checkbox should be disabled when there are no profile keys because it's impossible
        to sign the transaction but should also allow for removing a signature if the transaction is already signed.
        """
        is_transaction_already_signed = self.profile.transaction.is_signed
        has_profile_keys = bool(self.profile.keys)
        return not has_profile_keys and not is_transaction_already_signed


class SaveTransactionToFileDialog(SaveFileBaseDialog):
    def __init__(self, sign_key: PublicKey | None) -> None:
        super().__init__("Save transaction to file", "Save file")
        self._sign_key = sign_key

    @property
    def _is_binary_checked(self) -> bool:
        return self.query_exactly_one(BinaryCheckbox).value

    @property
    def _is_signed_checked(self) -> bool:
        return self.query_exactly_one(SignedCheckbox).value

    def additional_content_after_input(self) -> ComposeResult:
        with Switches():
            yield BinaryCheckbox()
            yield SignedCheckbox()

    async def _save_to_file(self, file_path: Path) -> bool:
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
