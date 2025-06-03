from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.keys.keys import PrivateKey
from clive.__private.ui.dialogs.select_file_base_dialog import SelectFileBaseDialog

if TYPE_CHECKING:
    ...


class LoadKeyFromFileDialog(SelectFileBaseDialog[str]):
    def __init__(self) -> None:
        super().__init__("Choose a file to load the key", "Load key")
        self._loaded_key: str | None = None

    async def _perform_confirmation(self) -> bool:
        return self._load_key_from_file()

    def _close_when_confirmed(self) -> None:
        self.dismiss(result=self._loaded_key)

    def _close_when_cancelled(self) -> None:
        self.dismiss(result=None)

    def _load_key_from_file(self) -> bool:
        path = self._file_path_input.value_or_none()
        if path is None:
            return False

        self._loaded_key = PrivateKey.read_key_from_file(path)
        self.notify(f"Private key loaded from `{path}`")
        return True
