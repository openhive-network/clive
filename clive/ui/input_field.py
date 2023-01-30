from __future__ import annotations

import typing
from typing import TYPE_CHECKING, Final

from loguru import logger
from prompt_toolkit.completion import FuzzyWordCompleter
from prompt_toolkit.widgets import SearchToolbar, TextArea

from clive.app_status import app_status
from clive.ui.containerable import Containerable

if TYPE_CHECKING:
    from prompt_toolkit.buffer import Buffer


class InputField(Containerable):
    DEACTIVATED_PROMPT: Final[str] = ">>>: "
    ACTIVATED_PROMPT: Final[str] = "###: "

    def __init__(self) -> None:
        self.__search_field = SearchToolbar()  # For reverse search.
        self.__completer = FuzzyWordCompleter(["activate", "deactivate"])
        super().__init__()

    @property
    def container(self) -> TextArea:
        return typing.cast(TextArea, self._container)

    def _create_container(self) -> TextArea:
        return TextArea(
            height=1,
            prompt=self.DEACTIVATED_PROMPT,
            multiline=False,
            wrap_lines=False,
            style="bg:#000000 #ffffff",
            accept_handler=self.__accept_handler,
            search_field=self.__search_field,
            completer=self.__completer,
        )

    def __accept_handler(self, buffer: Buffer) -> bool:
        logger.debug(f"Received input: {buffer.text}")

        # TODO: just for testing, should be done in a better way

        if buffer.text == "activate":
            app_status.activate()

        elif buffer.text == "deactivate":
            app_status.deactivate()

        return False


input_field = InputField()
