from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from textual.containers import Horizontal
from textual.widgets import Checkbox

from clive.__private.ui.widgets.select_file import SelectFile

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Switches(Horizontal):
    """Container for the switches."""

    DEFAULT_CSS = """
    Switches {
        margin: 1 0;
        height: auto;
    }
    """


class SelectFileToSaveTransaction(SelectFile):
    BIG_TITLE = "Save transaction to file"

    @dataclass
    class Saved(SelectFile.Saved):
        """Emitted when user saves the form."""

        save_as_binary: bool = False
        should_be_signed: bool = False

    def __init__(self) -> None:
        super().__init__(validator_mode="is_file_or_can_be_file")
        self.__binary_checkbox = Checkbox("Binary?")
        self.__signed_checkbox = Checkbox("Signed?")

    @property
    def is_binary_checked(self) -> bool:
        return self.__binary_checkbox.value

    @property
    def is_signed_checked(self) -> bool:
        return self.__signed_checkbox.value

    def additional_content_after_input(self) -> ComposeResult:
        with Switches():
            yield self.__binary_checkbox
            yield self.__signed_checkbox

    def _post_saved_message(self) -> None:
        from clive.__private.ui.transaction_summary.common import TransactionSummaryCommon

        self.app.post_message_to_screen(TransactionSummaryCommon, self._create_saved_message())

    def _create_saved_message(self) -> Saved:
        return self.Saved(
            file_path=self._file_path_input.value_or_error,
            save_as_binary=self.is_binary_checked,
            should_be_signed=self.is_signed_checked,
        )  # already validated in action_save
