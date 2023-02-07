from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Callable

from clive.storage.mock_database import PrivateKey
from clive.ui.base_float import BaseFloat

if TYPE_CHECKING:
    from prompt_toolkit.widgets import TextArea


class CreatePrivateKeyFloat(BaseFloat):
    def __init__(self, on_accept: Callable[[PrivateKey], None]) -> None:
        self.__key_name: str = ""
        self.__private_key: str = ""
        self.__on_accept = on_accept

        self.__key_name_text_area: TextArea = self._create_text_area()
        self.__priv_keys_text_area: TextArea = self._create_text_area()
        self.__priv_keys_path_text_area: TextArea = self._create_text_area()

        super().__init__(
            "Creating Private Key",
            {
                "Key Name": self.__key_name_text_area,
                "Private Key": self.__priv_keys_text_area,
                "or Path to File with Private Key": self.__priv_keys_path_text_area,
            },
        )

    def __handle_key_name_input(self) -> bool:
        text = self.__key_name_text_area.text
        if len(text) > 0:
            self.__key_name = text
            return True
        return False

    def __handle_private_key_input(self) -> bool:
        text = self.__priv_keys_text_area.text
        if len(text) > 0:
            self.__private_key = text
            return True
        return False

    def __handle_private_key_file_input(self) -> bool:
        path = Path(self.__priv_keys_text_area.text)

        if not path.exists():
            return False

        # read just one line
        with path.open("wt") as in_file:
            for line in in_file:
                self.__private_key = line.strip("\n")
                break
        return True

    def _ok(self) -> bool:
        if self.__handle_key_name_input() and (
            self.__handle_private_key_input() or self.__handle_private_key_file_input()
        ):
            self.__on_accept(PrivateKey(key_name=self.__key_name, key=self.__private_key))
            return True
        return False
