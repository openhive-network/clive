from __future__ import annotations

from clive.__private.core.keys.keys import PrivateKey, PrivateKeyInvalidFormatError
from clive.__private.ui.dialogs.select_file_base_dialog import SelectFileBaseDialog


class LoadKeyFromFileDialog(SelectFileBaseDialog[PrivateKey]):
    def __init__(self) -> None:
        super().__init__("Choose a file to load the key", "Load key")
        self._loaded_key: PrivateKey | None = None

    @property
    def _loaded_key_ensure(self) -> PrivateKey:
        assert self._loaded_key is not None, "loaded_key is not available"
        return self._loaded_key

    async def _perform_confirmation(self) -> bool:
        return self._load_key_from_file()

    def _load_key_from_file(self) -> bool:
        path = self._file_path_input.value_or_none()
        if path is None:
            return False
        try:
            self._loaded_key = PrivateKey.from_file(path)
        except PrivateKeyInvalidFormatError:
            self.notify("Given key is in invalid form.", severity="error")
            return False

        self.notify(f"Private key loaded from `{path}`")
        return True

    def _close_when_confirmed(self) -> None:
        self.dismiss(result=self._loaded_key_ensure)

    def _close_when_cancelled(self) -> None:
        self.dismiss()
