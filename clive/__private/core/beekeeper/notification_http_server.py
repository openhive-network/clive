from __future__ import annotations

import json
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import TYPE_CHECKING, Any, Protocol, cast

from clive.__private.core.beekeeper.raise_exception_helper import RaiseExceptionHelper

if TYPE_CHECKING:
    from collections.abc import Callable

JsonT = dict[str, Any]


class Notifiable(Protocol):
    def notify(self, message: JsonT) -> None:
        ...


class HttpServer:
    __ADDRESS = ("127.0.0.1", 0)

    class HttpServerImpl(HTTPServer):
        def __init__(
            self,
            server_address: tuple[str, int],
            request_handler_class: Callable[..., BaseHTTPRequestHandler],
            parent: Notifiable,
        ) -> None:
            super().__init__(server_address, request_handler_class)
            self.parent = parent

        def notify(self, message: JsonT) -> None:
            self.parent.notify(message)

    def __init__(self, observer: Notifiable, *, name: str) -> None:
        self.__observer = observer

        self.__name = name
        self.__server: HTTPServer | None = None
        self.__thread: threading.Thread | None = None

    def __assure_server_exists(self) -> None:
        if self.__server is None:
            self.__server = self.HttpServerImpl(self.__ADDRESS, HttpRequestHandler, self)

    @property
    def port(self) -> int:
        self.__assure_server_exists()
        assert self.__server is not None
        return self.__server.server_port

    def run(self) -> None:
        if self.__thread is not None:
            raise RuntimeError("Server is already running")

        self.__assure_server_exists()
        self.__thread = threading.Thread(target=self.__thread_function, name=self.__name, daemon=True)
        self.__thread.start()

    def __thread_function(self) -> None:
        try:
            assert self.__server is not None
            self.__server.serve_forever()
        except Exception as exception:  # pylint: disable=broad-except  # noqa: BLE001
            RaiseExceptionHelper.raise_exception_in_main_thread(exception)

    def close(self) -> None:
        if self.__thread is None:
            return

        assert self.__server is not None
        self.__server.shutdown()
        self.__server.server_close()
        self.__server = None

        self.__thread.join(timeout=2.0)
        if self.__thread.is_alive():
            raise RuntimeError("Unable to join server thread")
        self.__thread = None

    def notify(self, message: JsonT) -> None:
        """Should be called only by request handler when request is received"""
        self.__observer.notify(message)


class HttpRequestHandler(BaseHTTPRequestHandler):
    def do_PUT(self) -> None:  # pylint: disable=invalid-name  # noqa: N802
        server = cast(HttpServer, self.server)
        content_length = int(self.headers["Content-Length"])
        message = self.rfile.read(content_length)
        server.notify(json.loads(message))
        self.__set_response()

    def log_message(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=redefined-builtin
        # This method is defined to silent logs printed after each received message.
        # Solution based on: https://stackoverflow.com/a/3389505
        pass

    def __set_response(self) -> None:
        self.send_response(HTTPStatus.NO_CONTENT)
