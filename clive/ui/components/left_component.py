from __future__ import annotations

from typing import TYPE_CHECKING

from prompt_toolkit.layout import FormattedTextControl, VSplit, Window
from prompt_toolkit.widgets import TextArea

from clive.ui.component import Component

if TYPE_CHECKING:
    from clive.ui.views.dashboard import Dashboard  # noqa: F401


class LeftComponentFirst(Component["Dashboard"]):
    def _create_container(self) -> TextArea:
        return TextArea(
            text="LEFT COMPONENT",
            style="class:secondary",
            focus_on_click=True,
        )


class LeftComponentSecond(Component["Dashboard"]):
    def _create_container(self) -> VSplit:
        return VSplit(
            [
                TextArea(
                    text="LEFT COMPONENT SECOND VARIATION",
                    style="class:secondary",
                ),
                Window(
                    FormattedTextControl(text="LEFT COMPONENT SECOND VARIATION"),
                ),
            ]
        )
