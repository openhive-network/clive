from __future__ import annotations

import socket
from http import HTTPStatus
from typing import Any, Protocol

from aiohttp import web

from clive.exceptions import CliveError

JsonT = dict[str, Any]


def pickup_free_port() -> int:
    sock = socket.socket()
    sock.bind(("", 0))
    return sock.getsockname()[1]  # type: ignore[no-any-return]


class AsyncHttpServerError(CliveError):
    pass


class ServerNotRunningError(AsyncHttpServerError):
    def __init__(self) -> None:
        super().__init__("Server is not running. Call run() first.")


class ServerAlreadyRunningError(AsyncHttpServerError):
    def __init__(self) -> None:
        super().__init__("Server is already running. Call close() first.")


class Notifiable(Protocol):
    def notify(self, message: JsonT) -> None:
        ...


class AsyncHttpServer:
    __ADDRESS = ("127.0.0.1", pickup_free_port())

    def __init__(self, observer: Notifiable) -> None:
        self.__observer = observer
        self.__app = web.Application()
        self.__app.router.add_route("PUT", "/", self.__do_put)
        self.__site: web.TCPSite | None = None

    @property
    def port(self) -> int:
        return self.__ADDRESS[1]

    async def run(self) -> web.AppRunner:
        if self.__site:
            raise ServerAlreadyRunningError

        runner = web.AppRunner(self.__app)
        await runner.setup()
        self.__site = web.TCPSite(runner, *self.__ADDRESS)
        await self.__site.start()
        return runner

    async def close(self) -> None:
        if not self.__site:
            raise ServerNotRunningError

        await self.__site.stop()
        self.__site = None

    async def __do_put(self, request: web.Request) -> web.Response:
        data = await request.json()
        self.__observer.notify(data)
        return web.Response(status=HTTPStatus.NO_CONTENT)
