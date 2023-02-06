from __future__ import annotations

from typing import TYPE_CHECKING, Final

from loguru import logger
from prompt_toolkit.completion import FuzzyWordCompleter
from prompt_toolkit.layout import CompletionsMenu, Dimension, Float, FloatContainer, VSplit
from prompt_toolkit.layout.processors import BeforeInput
from prompt_toolkit.widgets import SearchToolbar, TextArea

from clive.app_status import app_status
from clive.ui.containerable import Containerable
from clive.ui.parented import Parented

if TYPE_CHECKING:
    from prompt_toolkit.buffer import Buffer

    from clive.ui.internal_cli.prompt_float import PromptFloat


class InputField(Parented["PromptFloat"], Containerable[VSplit]):
    DEACTIVATED_PROMPT: Final[str] = ">>>: "
    ACTIVATED_PROMPT: Final[str] = "###: "

    def __init__(self, parent: PromptFloat) -> None:
        self.__search_field = SearchToolbar()  # For reverse search.
        self.__completer = FuzzyWordCompleter(["activate", "deactivate"])

        self.__prompt_text = self.DEACTIVATED_PROMPT

        self.__text_area = TextArea(
            prompt=self.__prompt_text,
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
        super().__init__(parent)

    def _create_container(self) -> VSplit:
        return VSplit(
            [
                FloatContainer(
                    self.__text_area,
                    floats=[self.__completion_float],
                ),
            ],
            height=Dimension(min=10),
        )

    def __accept_handler(self, buffer: Buffer) -> bool:
        logger.debug(f"Received input: {buffer.text}")
        self._parent.log_panel.save_input(buffer.text)

        # TODO: just for testing, should be done in a better way

        if buffer.text == "activate":
            app_status.activate()
        elif buffer.text == "deactivate":
            app_status.deactivate()
        else:
            self._parent.log_panel.save_error("Invalid command")

        return False

    @property
    def prompt_text(self) -> str:
        return self.__prompt_text

    @prompt_text.setter
    def prompt_text(self, text: str) -> None:
        self.__prompt_text = text

        processors = self.__text_area.control.input_processors or []
        for processor in processors:
            if isinstance(processor, BeforeInput):
                processor.text = self.__prompt_text
                break
