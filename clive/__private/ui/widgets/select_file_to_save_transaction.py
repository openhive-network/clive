from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from textual.containers import Horizontal
from textual.widgets import Checkbox

from clive.__private.ui.widgets.select_file import SaveFileResult, SelectFile

if TYPE_CHECKING:
    from textual.app import ComposeResult


@dataclass
class SaveTransactionResult(SaveFileResult):
    save_as_binary: bool = False
    should_be_signed: bool = False


class Switches(Horizontal):
    """Container for the switches."""

    DEFAULT_CSS = """
    Switches {
        margin: 1 0;
        height: auto;
    }
    """


class SelectFileToSaveTransaction(SelectFile[SaveTransactionResult]):
    SECTION_TITLE = "Save transaction to file"

    def __init__(self) -> None:
        super().__init__(validator_mode="is_file_or_can_be_file")
        self.__binary_checkbox = Checkbox("Binary?")
        self.__signed_checkbox = Checkbox("Signed?", disabled=not self.profile.keys)

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

    def _create_success_save_result(self) -> SaveTransactionResult:
        return SaveTransactionResult(
            file_path=self._file_path_input.value_or_error,  # already validated in action_save
            save_as_binary=self.is_binary_checked,
            should_be_signed=self.is_signed_checked,
        )
