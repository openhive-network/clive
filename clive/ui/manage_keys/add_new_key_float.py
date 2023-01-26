from pathlib import Path
from typing import Callable

from prompt_toolkit.layout import AnyContainer, Dimension, HorizontalAlign, HSplit, VSplit
from prompt_toolkit.widgets import Button, Frame, Label, TextArea

from clive.storage.mock_database import PrivateKey
from clive.ui.base_float import BaseFloat


class CreatePrivateKeyFloat(BaseFloat):
    def __init__(self, on_accept: Callable[[PrivateKey], None]) -> None:
        self.__key_name: str = ""
        self.__private_key: str = ""
        self.__on_accept = on_accept

        self.__key_name_text_area: TextArea = self.__create_text_area()
        self.__priv_keys_text_area: TextArea = self.__create_text_area()
        self.__priv_keys_path_text_area: TextArea = self.__create_text_area()

        super().__init__()

    def __create_text_area(self) -> TextArea:
        return TextArea(multiline=False, width=Dimension(min=15))

    def _create_container(self) -> AnyContainer:
        return Frame(
            HSplit(
                [
                    VSplit(
                        [
                            HSplit(
                                [
                                    Frame(Label("Key Name")),
                                    Frame(Label("Private Key")),
                                    Frame(Label("or Path to File with Private Key")),
                                ]
                            ),
                            HSplit(
                                [
                                    Frame(self.__key_name_text_area),
                                    Frame(self.__priv_keys_text_area),
                                    Frame(self.__priv_keys_path_text_area),
                                ]
                            ),
                        ]
                    ),
                    VSplit(
                        [Button("Ok", handler=self.__ok_button), Button("Cancel", handler=self.__cancel_button)],
                        align=HorizontalAlign.CENTER,
                        padding=Dimension(min=1),
                    ),
                ]
            ),
            title="Creating Private Key",
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

    def __ok_button(self) -> None:
        if self.__handle_key_name_input() and (
            self.__handle_private_key_input() or self.__handle_private_key_file_input()
        ):
            self.__on_accept(PrivateKey(key_name=self.__key_name, key=self.__private_key))
            self._close()

    def __cancel_button(self) -> None:
        self._close()
