from prompt_toolkit.layout import Dimension, Float, HSplit
from prompt_toolkit.widgets import Frame

from clive.ui.containerable import Containerable
from clive.ui.enums import ZIndex
from clive.ui.internal_cli.input_field import InputField
from clive.ui.internal_cli.log_panel import LogPanel


class PromptFloat(Containerable[Float]):
    def __init__(self) -> None:
        self.__log_panel = LogPanel(self)
        self.__input_field = InputField(self)
        super().__init__()

    @property
    def log_panel(self) -> LogPanel:
        return self.__log_panel

    @property
    def input_field(self) -> InputField:
        return self.__input_field

    def _create_container(self) -> Float:
        return Float(
            Frame(
                HSplit(
                    [
                        self.__log_panel.container,
                        self.__input_field.container,
                    ]
                ),
                title="Prompt",
                width=Dimension(preferred=80),
                modal=True,
            ),
            z_index=ZIndex.PROMPT_FLOAT,
        )
