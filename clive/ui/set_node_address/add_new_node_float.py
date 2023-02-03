from typing import Callable, Optional

from prompt_toolkit.widgets import TextArea

from clive.exceptions import InvalidHost, NotInValidRange
from clive.storage.mock_database import NodeAddress
from clive.ui.base_float import BaseFloat


class CreateNodeFloat(BaseFloat):
    def __init__(self, on_accept: Callable[[NodeAddress], None]) -> None:
        self.__proto: str = ""
        self.__host: str = ""
        self.__port: Optional[int] = None
        self.__on_accept = on_accept

        self.__proto_text_area: TextArea = self._create_text_area(text="http")
        self.__host_text_area: TextArea = self._create_text_area()
        self.__port_text_area: TextArea = self._create_text_area()

        super().__init__(
            "Creating Node Address",
            {"Proto": self.__proto_text_area, "Host": self.__host_text_area, "Port": self.__port_text_area},
        )

    def __handle_str_input(self, area: TextArea) -> str:
        text = area.text
        if len(text) > 0:
            return text
        return ""

    def __handle_proto_input(self) -> None:
        self.__proto = self.__handle_str_input(self.__proto_text_area)

    def __handle_host_input(self) -> None:
        self.__host = self.__handle_str_input(self.__host_text_area)
        if len(self.__host) == 0:
            raise InvalidHost()

    def __handle_port_input(self) -> None:
        MAX_PORT_RANGE = (2**15) - 1
        text = self.__port_text_area.text
        port = int(text)
        if port <= 0 or port >= MAX_PORT_RANGE:
            raise NotInValidRange(port, 1, MAX_PORT_RANGE - 1)
        self.__port = port

    def _ok(self) -> None:
        self.__handle_proto_input()
        self.__handle_host_input()
        self.__handle_port_input()
        self.__on_accept(NodeAddress(proto=self.__proto, host=self.__host, port=self.__port))
