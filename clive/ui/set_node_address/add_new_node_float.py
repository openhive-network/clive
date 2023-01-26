from typing import Any, Callable, Optional, Tuple

from prompt_toolkit.layout import AnyContainer, Dimension, HorizontalAlign, HSplit, VSplit
from prompt_toolkit.widgets import Button, Frame, Label, TextArea

from clive.storage.mock_database import NodeAddress
from clive.ui.base_float import BaseFloat


class CreateNodeFloat(BaseFloat):
    def __init__(self, on_accept: Callable[[NodeAddress], None]) -> None:
        self.__proto: str = ""
        self.__host: str = ""
        self.__port: Optional[int] = None
        self.__on_accept = on_accept

        self.__proto_text_area: TextArea = self.__create_text_area(text="http")
        self.__host_text_area: TextArea = self.__create_text_area()
        self.__port_text_area: TextArea = self.__create_text_area()

        super().__init__()

    def __create_text_area(self, **kwargs: Any) -> TextArea:
        return TextArea(**kwargs, multiline=False, width=Dimension(min=15))

    def _create_container(self) -> AnyContainer:
        return Frame(
            HSplit(
                [
                    VSplit(
                        [
                            HSplit([Frame(Label("Proto")), Frame(Label("Host")), Frame(Label("Port"))]),
                            HSplit(
                                [
                                    Frame(self.__proto_text_area),
                                    Frame(self.__host_text_area),
                                    Frame(self.__port_text_area),
                                ]
                            ),
                        ]
                    ),
                    VSplit(
                        [Button("Ok", handler=self.__ok_button), Button("Cancel", handler=self.__cancel_button)],
                        align=HorizontalAlign.CENTER,
                        padding=Dimension(min=1),
                    ),
                ]
            ),
            title="Creating Node Address",
        )

    def __handle_str_input(self, area: TextArea) -> Tuple[str, bool]:
        text = area.text
        if len(text) > 0:
            return (text, True)
        return ("", False)

    def __handle_proto_input(self) -> bool:
        self.__proto, result = self.__handle_str_input(self.__proto_text_area)
        return result

    def __handle_host_input(self) -> bool:
        self.__host, result = self.__handle_str_input(self.__host_text_area)
        return result

    def __handle_port_input(self) -> Optional[int]:
        text = self.__port_text_area.text
        try:
            self.__port = int(text)
            assert self.__port > 0 and self.__port < ((2**15) - 1)
        except Exception:
            self.__port = None
        return self.__port

    def __ok_button(self) -> None:
        if self.__handle_proto_input() and self.__handle_host_input():
            self.__on_accept(NodeAddress(proto=self.__proto, host=self.__host, port=self.__handle_port_input()))
            self._close()

    def __cancel_button(self) -> None:
        self._close()
