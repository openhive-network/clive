from typing import Callable

from prompt_toolkit.widgets import TextArea

from clive.storage.mock_database import Account
from clive.ui.base_float import BaseFloat


class CreateWatchedAccountFloat(BaseFloat):
    def __init__(self, on_accept: Callable[[Account], None]) -> None:
        self.__account_name: str = ""
        self.__on_accept = on_accept

        self.__account_name_text_area: TextArea = self._create_text_area()

        super().__init__("Creating Watched Account", {"Account Name": self.__account_name_text_area})

    def __handle_account_name_input(self) -> None:
        text = self.__account_name_text_area.text
        if len(text) > 0:
            self.__account_name = text

    def _ok(self) -> None:
        self.__handle_account_name_input()
        acc = Account(name=self.__account_name)
        acc.valid()
        self.__on_accept(acc)
