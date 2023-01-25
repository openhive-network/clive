from pathlib import Path
from typing import Callable, List

from prompt_toolkit.layout import AnyContainer, Dimension, HorizontalAlign, HSplit, VSplit
from prompt_toolkit.widgets import Button, Frame, Label, TextArea

from clive.storage.mock_database import Account, AccountType
from clive.ui.floats.base_float import BaseFloat


class CreateAccountFloat(BaseFloat):
    def __init__(self, on_accept: Callable[[Account], None]) -> None:
        self.__account_name: str = ""
        self.__private_keys: List[str] = []
        self.__on_accept = on_accept

        self.__account_name_text_area: TextArea = self.__create_text_area()
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
                                    Frame(Label("Account Name")),
                                    Frame(Label("Private Key")),
                                    Frame(Label("or Path to File with Private Key")),
                                ]
                            ),
                            HSplit(
                                [
                                    Frame(self.__account_name_text_area),
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
            title="Creating Account",
        )

    def __handle_account_name_input(self) -> bool:
        text = self.__account_name_text_area.text
        if len(text) > 0:
            self.__account_name = text
            return True
        return False

    def __handle_private_key_input(self) -> bool:
        text = self.__priv_keys_text_area.text
        if len(text) > 0:
            self.__private_keys = [text]
            return True
        return False

    def __handle_private_key_file_input(self) -> bool:
        path = Path(self.__priv_keys_text_area.text)

        if not path.exists():
            return False

        with path.open("wt") as ifile:
            for line in ifile:
                self.__private_keys.append(line.strip("\n"))

        return True

    def __ok_button(self) -> None:
        if self.__handle_account_name_input() and (self.__handle_private_key_input() or self.__handle_private_key_file_input()):
            self._close()
            self.__on_accept(
                Account(name=self.__account_name, account_type=AccountType.ACTIVE, key_names=self.__private_keys)
            )

    def __cancel_button(self) -> None:
        self._close()
