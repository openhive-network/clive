from pathlib import Path
from typing import Callable

from prompt_toolkit.widgets import TextArea

from clive.exceptions import FileDoesNotExists, FileIsEmpty
from clive.storage.mock_database import PrivateKey
from clive.ui.base_float import BaseFloat


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

    def __handle_key_name_input(self) -> None:
        text = self.__key_name_text_area.text
        if len(text) > 0:
            self.__key_name = text

    def __handle_private_key_input(self) -> None:
        text = self.__priv_keys_text_area.text
        if len(text) > 0:
            self.__private_key = text

    def __handle_private_key_file_input(self) -> None:
        path = Path(self.__priv_keys_path_text_area.text)

        if not path.exists():
            raise FileDoesNotExists(path.as_posix())

        # read just one line
        with path.open("wt") as in_file:
            for line in in_file:
                self.__private_key = line.strip("\n")

        if len(self.__private_key) == 0:
            raise FileIsEmpty(path.as_posix())

    def _ok(self) -> None:
        self.__handle_key_name_input()
        self.__handle_private_key_input()
        if len(self.__private_key) == 0:
            self.__handle_private_key_file_input()

        pv_key = PrivateKey(key_name=self.__key_name, key=self.__private_key)
        pv_key.valid()
        self.__on_accept(pv_key)
