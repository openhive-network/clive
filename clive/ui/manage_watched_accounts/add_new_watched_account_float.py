from typing import Callable

from prompt_toolkit.layout import AnyContainer, Dimension, HorizontalAlign, HSplit, VSplit
from prompt_toolkit.widgets import Button, Frame, Label, TextArea

from clive.storage.mock_database import Account
from clive.ui.base_float import BaseFloat


class CreateWatchedAccountFloat(BaseFloat):
    def __init__(self, on_accept: Callable[[Account], None]) -> None:
        self.__account_name: str = ""
        self.__on_accept = on_accept

        self.__account_name_text_area: TextArea = self.__create_text_area()

        super().__init__()

    def __create_text_area(self) -> TextArea:
        return TextArea(multiline=False, width=Dimension(min=15))

    def _create_container(self) -> AnyContainer:
        return Frame(
            HSplit(
                [
                    VSplit(
                        [
                            HSplit([Frame(Label("Account Name"))]),
                            HSplit([Frame(self.__account_name_text_area)]),
                        ]
                    ),
                    VSplit(
                        [Button("Ok", handler=self.__ok_button), Button("Cancel", handler=self.__cancel_button)],
                        align=HorizontalAlign.CENTER,
                        padding=Dimension(min=1),
                    ),
                ]
            ),
            title="Creating Watched Account",
        )

    def __handle_account_name_input(self) -> bool:
        text = self.__account_name_text_area.text
        if len(text) > 0:
            self.__account_name = text
            return True
        return False

    def __ok_button(self) -> None:
        if self.__handle_account_name_input():
            self.__on_accept(Account(name=self.__account_name))
            self._close()

    def __cancel_button(self) -> None:
        self._close()
