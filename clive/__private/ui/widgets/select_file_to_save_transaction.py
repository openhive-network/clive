from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from textual.widgets import Checkbox

from clive.__private.ui.widgets.select_file import SelectFile

if TYPE_CHECKING:
    from textual.app import ComposeResult


class SelectFileToSaveTransaction(SelectFile):
    @dataclass
    class Saved(SelectFile.Saved):
        """Emitted when user saves the form."""

        binary: bool = False

    def __init__(self) -> None:
        super().__init__(file_must_exist=False)
        self.__checkbox = Checkbox("Binary?")

    def additional_content_after_input(self) -> ComposeResult:
        yield self.__checkbox

    def _create_saved_message(self) -> Saved:
        return self.Saved(file_path=self.file_path, binary=self.__checkbox.value)
