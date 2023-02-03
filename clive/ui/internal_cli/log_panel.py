from prompt_toolkit.layout import Dimension, ScrollablePane, VSplit
from prompt_toolkit.widgets import TextArea

from clive.ui.containerable import Containerable


class LogPanel(Containerable[ScrollablePane]):
    def _create_container(self) -> ScrollablePane:
        return ScrollablePane(
            VSplit(
                [
                    TextArea(
                        text="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec auctor, nisl eget",
                        read_only=True,
                        focusable=False,
                        style="class:tertiary",
                    )
                ],
                height=Dimension(preferred=15),
            )
        )
