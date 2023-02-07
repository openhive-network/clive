from __future__ import annotations

from typing import Callable, Optional, Tuple

from prompt_toolkit.widgets import TextArea

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
        except ValueError:
            self.__port = None
        return self.__port

    def _ok(self) -> bool:
        if self.__handle_proto_input() and self.__handle_host_input():
            self.__on_accept(NodeAddress(proto=self.__proto, host=self.__host, port=self.__handle_port_input()))
            return True
        return False
