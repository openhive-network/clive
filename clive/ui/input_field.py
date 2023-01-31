from __future__ import annotations

import typing
from typing import TYPE_CHECKING, Final

from loguru import logger
from prompt_toolkit.clipboard import ClipboardData
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout import VSplit
from prompt_toolkit.layout.processors import BeforeInput
from prompt_toolkit.widgets import SearchToolbar, TextArea

from clive.ui.containerable import Containerable
from clive.ui.internal_cli.completer import CliveCompleter

if TYPE_CHECKING:
    from prompt_toolkit.buffer import Buffer


class InputField(Containerable):
    DEACTIVATED_PROMPT: Final[str] = ">>>: "
    ACTIVATED_PROMPT: Final[str] = "###: "

    def __init__(self) -> None:
        self.__search_field = SearchToolbar()  # For reverse search.
        self.__completer = CliveCompleter()
        self.__text_area = TextArea(
            # height=10,
            prompt=self.DEACTIVATED_PROMPT,
            multiline=False,
            wrap_lines=True,
            style="bg:#000000 #ffffff",
            accept_handler=self.__accept_handler,
            search_field=self.__search_field,
            completer=self.__completer,
        )
        super().__init__()

    @property
    def container(self) -> TextArea:
        return typing.cast(TextArea, self._container)

    def _create_container(self) -> VSplit:
        kb = KeyBindings()

        @kb.add(Keys.ControlBackslash)
        def _(_: KeyPressEvent) -> None:
            self.__text_area.document = self.__text_area.document.paste_clipboard_data(ClipboardData("\n"))

        return VSplit([self.__text_area], height=10, key_bindings=kb)

    def __accept_handler(self, buffer: Buffer) -> bool:
        logger.debug(f"Received input: {buffer.text}")

        return False

    def set_prompt_text(self, text: str) -> None:
        processors = self.container.control.input_processors or []
        for processor in processors:
            if isinstance(processor, BeforeInput):
                processor.text = text
                break


input_field = InputField()
