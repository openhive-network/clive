from __future__ import annotations

from typing import TYPE_CHECKING, Any

from httpx import codes
from pydantic import Field, validator

from clive.__private.config import settings
from clive.__private.core.beekeeper.api import BeekeeperApi
from clive.__private.core.beekeeper.config import BeekeeperConfig, webserver_default
from clive.__private.core.beekeeper.executable import BeekeeperExecutable, BeekeeperNotConfiguredError
from clive.__private.core.beekeeper.model import JSONRPCRequest, JSONRPCResponse, T
from clive.__private.core.beekeeper.notifications import BeekeeperNotificationsServer
from clive.__private.core.communication import Communication
from clive.__private.logger import logger
from clive.core.url import Url
from clive.exceptions import CliveError, CommunicationError
from clive.models.base import CliveBaseModel

if TYPE_CHECKING:
    from pathlib import Path

    from clive.__private.core.beekeeper.notification_http_server import JsonT


class BeekeeperError(CliveError):
    """Base class for all Beekeeper errors."""


class BeekeeperUrlNotSetError(BeekeeperError):
    pass


class BeekeeperNon200StatusCodeError(BeekeeperError):
    pass


class BeekeeperResponseError(BeekeeperError, CommunicationError):
    def __init__(self, url: str, request: JSONRPCRequest, response: JsonT) -> None:
        super().__init__(url, request.json(by_alias=True), response)


class BeekeeperNotMatchingIdJsonRPCError(BeekeeperError):
    def __init__(self, given: Any, got: Any) -> None:
        self.message = f"Given id `{given}` does not match the id of the response `{got}`"
        super().__init__(self.message)


class Beekeeper:
    class ConnectionFileData(CliveBaseModel):
        type_: str = Field(alias="type")
        address: str
        port: int

        @validator("type_")
        @classmethod
        def convert_type(cls, value: str) -> str:
            return value.lower()

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
            raise BeekeeperUrlNotSetError

        return self.config.webserver_http_endpoint

    @property
    def pid(self) -> int:
        return self.__executable.pid

    @staticmethod
    def get_pid_from_file() -> int:
        return BeekeeperExecutable.get_pid_from_file()

    @staticmethod
    def is_already_running_locally() -> bool:
        return BeekeeperExecutable.is_already_running()

    def _send(self, result_model: type[T], endpoint: str, **kwargs: Any) -> JSONRPCResponse[T]:  # noqa: ARG002, RUF100
        url = self.http_endpoint.as_string()
        request = JSONRPCRequest(method=endpoint, params=kwargs)
        response = Communication.request(url, data=request.json(by_alias=True))

        if response.status_code != codes.OK:
            raise BeekeeperNon200StatusCodeError

        result = response.json()
        if "error" in result:
            raise BeekeeperResponseError(url, request, result)

        return_value = JSONRPCResponse[T](**result)

        if return_value.id_ != request.id_:
            raise BeekeeperNotMatchingIdJsonRPCError(request.id_, return_value.id_)

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

    @classmethod
    def get_remote_address_from_connection_file(cls) -> Url | None:
        connection_file = BeekeeperConfig.get_wallet_dir() / "beekeeper.connection"
        if not connection_file.is_file():
            return None

        connection = cls.ConnectionFileData.parse_file(connection_file)

        return Url(connection.type_, connection.address, connection.port)
