from __future__ import annotations

from prompt_toolkit.filters import Condition
from prompt_toolkit.layout import ConditionalContainer, Dimension, VSplit
from prompt_toolkit.widgets import Label
from prompt_toolkit.widgets import ProgressBar as PromptToolkitProgressBar

from clive.ui.get_view_manager import get_view_manager


class ProgressBar(PromptToolkitProgressBar):
    """
    A progress bar that also displays percentage text. The bar is not visible when any float elements are displayed
    because it would overlap with them. (This is a workaround for prompt_toolkit's ProgressBar not being able to be
    hidden under another floats, even when manipulating its z_index.)
    """

    def __init__(self) -> None:
        super().__init__()
        self.container = VSplit(
            [
                ConditionalContainer(
                    # VSplit with weight is needed to make the bar take more of the available space
                    VSplit([self.container], width=Dimension(weight=4)),
                    filter=~Condition(get_view_manager().floats.is_any_float_visible),
                ),
                Label(lambda: f"({self.percentage:.2f}%)"),
            ]
        )  # type: ignore
