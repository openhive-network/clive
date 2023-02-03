from prompt_toolkit.layout import Float, HSplit, ScrollablePane, VSplit
from prompt_toolkit.widgets import Frame, TextArea

from clive.ui.containerable import Containerable
from clive.ui.input_field import input_field


class PromptFloat(Containerable[Float]):
    def __init__(self) -> None:
        self.__input_field = input_field
        super().__init__()

    def _create_container(self) -> Float:
        return Float(
            Frame(
                HSplit(
                    [
                        self.__crate_log_panel(),
                        self.__input_field.container,
                    ]
                ),
                title="Prompt",
                modal=True,
            ),
            z_index=2,
        )

    @staticmethod
    def __crate_log_panel() -> ScrollablePane:
        return ScrollablePane(
            VSplit(
                [
                    TextArea(
                        text="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec auctor, nisl eget",
                        read_only=True,
                        focusable=False,
                        style="bg:#0000ff #ffffff",
                    )
                ]
            )
        )
