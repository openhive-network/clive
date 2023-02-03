from prompt_toolkit.layout import Dimension, Float, HSplit, ScrollablePane, VSplit
from prompt_toolkit.widgets import Frame, TextArea

from clive.ui.containerable import Containerable
from clive.ui.internal_cli.input_field import InputField


class PromptFloat(Containerable[Float]):
    def __init__(self) -> None:
        self.__input_field = InputField()
        super().__init__()

    @property
    def input_field(self) -> InputField:
        return self.__input_field

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
                width=Dimension(preferred=80),
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
                        style="class:tertiary",
                    )
                ],
                height=Dimension(preferred=15),
            )
        )
