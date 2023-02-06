from __future__ import annotations

from typing import TYPE_CHECKING

from prompt_toolkit.document import Document
from prompt_toolkit.layout import Dimension, ScrollablePane, VSplit
from prompt_toolkit.widgets import TextArea

from clive.ui.containerable import Containerable
from clive.ui.parented import Parented

if TYPE_CHECKING:
    from clive.ui.internal_cli.prompt_float import PromptFloat


class LogPanel(Parented["PromptFloat"], Containerable[ScrollablePane]):
    def __init__(self, parent: PromptFloat) -> None:
        self.__text_area = TextArea(
            text="",
            read_only=True,
            focusable=False,
            style="class:tertiary",
        )
        super().__init__(parent)

    def save_input(self, text: str) -> None:
        prefix = self._parent.input_field.prompt_text
        self.__log(f"{prefix}{text}")

    def save_log(self, text: str) -> None:
        self.__log(text)

    def save_error(self, text: str) -> None:
        self.__log(f"! {text}")

    def __log(self, text: str) -> None:
        text = self.__text_area.text + f"{text}\n"
        self.__text_area.document = Document(text, len(text))  # scroll to the bottom of the log panel

    def _create_container(self) -> ScrollablePane:
        return ScrollablePane(
            VSplit(
                [
                    self.__text_area,
                ],
                height=Dimension(preferred=15),
            )
        )
