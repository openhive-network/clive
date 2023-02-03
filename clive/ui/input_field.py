from __future__ import annotations

from typing import TYPE_CHECKING, Final

from loguru import logger
from prompt_toolkit.completion import FuzzyWordCompleter
from prompt_toolkit.layout import CompletionsMenu, Dimension, Float, FloatContainer, VSplit
from prompt_toolkit.layout.processors import BeforeInput
from prompt_toolkit.widgets import SearchToolbar, TextArea

from clive.app_status import app_status
from clive.ui.containerable import Containerable

if TYPE_CHECKING:
    from prompt_toolkit.buffer import Buffer


class InputField(Containerable[VSplit]):
    DEACTIVATED_PROMPT: Final[str] = ">>>: "
    ACTIVATED_PROMPT: Final[str] = "###: "

    def __init__(self) -> None:
        self.__search_field = SearchToolbar()  # For reverse search.
        self.__completer = FuzzyWordCompleter(["activate", "deactivate"])

        self.__text_area = TextArea(
            prompt=self.DEACTIVATED_PROMPT,
            multiline=False,
            wrap_lines=True,
            style="bg:#000000 #ffffff",
            accept_handler=self.__accept_handler,
            search_field=self.__search_field,
            completer=self.__completer,
        )

        self.__completion_float = Float(
            xcursor=True,
            ycursor=True,
            content=CompletionsMenu(max_height=16, scroll_offset=1),
        )
        super().__init__()

    def _create_container(self) -> VSplit:
        return VSplit(
            [
                FloatContainer(
                    self.__text_area,
                    floats=[self.__completion_float],
                ),
            ],
            height=Dimension(min=10),
            width=80,
        )

    def __accept_handler(self, buffer: Buffer) -> bool:
        logger.debug(f"Received input: {buffer.text}")

        # TODO: just for testing, should be done in a better way

        if buffer.text == "activate":
            app_status.activate()

        elif buffer.text == "deactivate":
            app_status.deactivate()

        return False

    def set_prompt_text(self, text: str) -> None:
        processors = self.__text_area.control.input_processors or []
        for processor in processors:
            if isinstance(processor, BeforeInput):
                processor.text = text
                break


input_field = InputField()
