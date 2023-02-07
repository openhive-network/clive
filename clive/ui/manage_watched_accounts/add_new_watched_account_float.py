from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from clive.storage.mock_database import Account
from clive.ui.base_float import BaseFloat

if TYPE_CHECKING:
    from prompt_toolkit.widgets import TextArea


class CreateWatchedAccountFloat(BaseFloat):
    def __init__(self, on_accept: Callable[[Account], None]) -> None:
        self.__account_name: str = ""
        self.__on_accept = on_accept

        self.__account_name_text_area: TextArea = self._create_text_area()

        super().__init__("Creating Watched Account", {"Account Name": self.__account_name_text_area})

    def __handle_account_name_input(self) -> bool:
        text = self.__account_name_text_area.text
        if len(text) > 0:
            self.__account_name = text
            return True
        return False

    def _ok(self) -> bool:
        if self.__handle_account_name_input():
            self.__on_accept(Account(name=self.__account_name))
            return True
        return False
