from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

from textual import work

from clive.__private.ui.dialogs.confirm_save_file_dialog import ConfirmSaveFileDialog
from clive.__private.ui.dialogs.select_file_base_dialog import SelectFileBaseDialog
from clive.__private.ui.widgets.buttons.confirm_button import ConfirmOneLineButton


class SaveFileBaseDialog(SelectFileBaseDialog[bool]):
    def __init__(
        self,
        border_title: str,
        confirm_button_label: str = ConfirmOneLineButton.DEFAULT_LABEL,
        notice: str | None = None,
    ) -> None:
        super().__init__(border_title, confirm_button_label, notice)

    @abstractmethod
    async def _save_to_file(self, file_path: Path) -> bool:
        """Implement this method to save the file to the specified path."""

    async def get_save_file_path(self) -> Path | None:
        file_path = self._file_path_input.value_or_none()
        if file_path is None:
            return None
        if file_path.exists() and not await self._confirm_overwrite_a_file().wait():
            return None
        return file_path

    async def _perform_confirmation(self) -> bool:
        file_path = await self.get_save_file_path()
        if file_path is None:
            return False
        return await self._save_to_file(file_path)

    @work
    async def _confirm_overwrite_a_file(self) -> bool:
        """Confirm overwrite of the file if it already exists."""
        return await self.app.push_screen_wait(ConfirmSaveFileDialog())
