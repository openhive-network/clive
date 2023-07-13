from __future__ import annotations

from typing import TYPE_CHECKING, Any

from httpx import codes

from clive.__private.config import settings
from clive.__private.core.beekeeper.api import BeekeeperApi
from clive.__private.core.beekeeper.config import BeekeeperConfig, webserver_default
from clive.__private.core.beekeeper.executable import BeekeeperExecutable, BeekeeperNotConfiguredError
from clive.__private.core.beekeeper.model import JSONRPCRequest, JSONRPCResponse, T
from clive.__private.core.beekeeper.notifications import BeekeeperNotificationsServer
from clive.__private.core.communication import Communication
from clive.__private.logger import logger
from clive.core.url import Url
from clive.exceptions import CommunicationError

if TYPE_CHECKING:
    from pathlib import Path

    from clive.__private.core.beekeeper.notification_http_server import JsonT


class UrlNotSetError(CommunicationError):
    pass


class Non200StatusCodeError(CommunicationError):
    pass


class ErrorResponseError(CommunicationError):
    def __init__(self, request: JSONRPCRequest, response: JsonT) -> None:
        logger.error(f"""
For request: {request}

Got error response: {response}
""")
        super().__init__(request, response)


class NotMatchingIdJsonRPCError(CommunicationError):
    def __init__(self, given: Any, got: Any) -> None:
        logger.error(f"Id sent: `{given}`, got: `{got}`")
        super().__init__(given, got)


class Beekeeper:
    def __init__(self, *, remote_endpoint: Url | None = None, run_in_background: bool = False) -> None:
        if remote_endpoint:
            settings.set("beekeeper.remote_address", str(remote_endpoint))

        if not (Beekeeper.get_remote_address_from_settings() or Beekeeper.get_path_from_settings()):
            raise BeekeeperNotConfiguredError

        self.config = BeekeeperConfig()
        self.__notification_server = BeekeeperNotificationsServer()
        self.__notification_server_port: int | None = None
        self.api = BeekeeperApi(self)
        self.__executable = BeekeeperExecutable(self.config, run_in_background=run_in_background)
        self.__token: str | None = None

    @property
    def token(self) -> str:
        if self.__token is None:
            self.__token = self.api.create_session(
                notifications_endpoint=f"127.0.0.1:{self.__notification_server_port}", salt=str(id(self))
            ).token
        return self.__token

    @property
    def http_endpoint(self) -> Url:
        if not self.config.webserver_http_endpoint and (remote := self.get_remote_address_from_settings()):
            self.config.webserver_http_endpoint = remote

        if not self.config.webserver_http_endpoint:
            raise UrlNotSetError

        return self.config.webserver_http_endpoint

    @property
    def pid(self) -> int:
        return self.__executable.pid

    @staticmethod
    def get_pid_from_file() -> int:
        return BeekeeperExecutable.get_pid_from_file()

    def _send(self, response: type[T], endpoint: str, **kwargs: Any) -> JSONRPCResponse[T]:  # noqa: ARG002, RUF100
        request = JSONRPCRequest(method=endpoint, params=kwargs)
        result = Communication.request(self.http_endpoint.as_string(), data=request.json(by_alias=True))

        if result.status_code != codes.OK:
            raise Non200StatusCodeError

        json = result.json()
        if "error" in json:
            raise ErrorResponseError(request, json)

        return_value = JSONRPCResponse[T](**json)

        if return_value.id_ != request.id_:
            raise NotMatchingIdJsonRPCError(request.id_, return_value.id_)

        logger.info(f"Returning model: {return_value}")
        return return_value

    def close(self) -> None:
        self.api.close_session()
        self.__token = None
        self.__close_beekeeper()

    def start(self, *, timeout: float = 5.0) -> None:
        self.__notification_server_port = self.__notification_server.listen()
        if not (remote := self.get_remote_address_from_settings()):
            self.__run_beekeeper(timeout=timeout)
        else:
            self.config.webserver_http_endpoint = remote

        assert self.config.webserver_http_endpoint is not None
        assert self.token is not None

    def restart(self) -> None:
        self.close()
        self.start()

    def __run_beekeeper(self, *, timeout: float = 5.0) -> None:
        self.config.notifications_endpoint = Url("http", "127.0.0.1", self.__notification_server_port)
        self.__executable.run()

        if self.__notification_server.opening_beekeeper_failed.wait(timeout):
            self.__close_beekeeper()
            self.__notification_server_port = self.__notification_server.listen()
            self.config.notifications_endpoint = Url("http", "127.0.0.1", self.__notification_server_port)
        elif not (
            self.__notification_server.http_listening_event.wait(timeout)
            and self.__notification_server.ready.wait(timeout)
        ):
            self.__close_beekeeper()
            return

        logger.debug(f"Got webserver http endpoint: `{self.__notification_server.http_endpoint}`")
        self.config.webserver_http_endpoint = self.__notification_server.http_endpoint

    def __close_beekeeper(self) -> None:
        try:
            self.__executable.close()
        finally:
            self.__notification_server_port = None
            self.config.webserver_http_endpoint = webserver_default()
            self.__notification_server.close()

    @classmethod
    def get_path_from_settings(cls) -> Path | None:
        return BeekeeperExecutable.get_path_from_settings()

    @classmethod
    def get_remote_address_from_settings(cls) -> Url | None:
        raw_address = settings.get("beekeeper.remote_address")
        return Url.parse(raw_address) if raw_address else None
