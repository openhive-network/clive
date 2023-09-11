from __future__ import annotations

from contextlib import contextmanager
from http import HTTPStatus
from typing import TYPE_CHECKING, Any

from pydantic import Field, validator

from clive.__private.config import settings
from clive.__private.core._async import event_wait
from clive.__private.core.beekeeper.api import BeekeeperApi
from clive.__private.core.beekeeper.config import BeekeeperConfig, webserver_default
from clive.__private.core.beekeeper.exceptions import (
    BeekeeperNon200StatusCodeError,
    BeekeeperNotConfiguredError,
    BeekeeperNotMatchingIdJsonRPCError,
    BeekeeperNotRunningError,
    BeekeeperResponseError,
    BeekeeperTokenNotAvailableError,
    BeekeeperUrlNotSetError,
)
from clive.__private.core.beekeeper.executable import BeekeeperExecutable
from clive.__private.core.beekeeper.model import JSONRPCRequest, JSONRPCResponse, T
from clive.__private.core.beekeeper.notifications import BeekeeperNotificationsServer, WalletClosingListener
from clive.__private.core.communication import Communication
from clive.__private.logger import logger
from clive.core.url import Url
from clive.models.base import CliveBaseModel

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator
    from pathlib import Path
    from types import TracebackType

    from typing_extensions import Self


class Beekeeper:
    class ConnectionFileData(CliveBaseModel):
        type_: str = Field(alias="type")
        address: str
        port: int

        @validator("type_")
        @classmethod
        def convert_type(cls, value: str) -> str:
            return value.lower()

    def __init__(
        self,
        *,
        communication: Communication | None = None,
        remote_endpoint: Url | None = None,
        run_in_background: bool = False,
        notify_closing_wallet_name_cb: Callable[[], str] | None = None,
    ) -> None:
        if remote_endpoint:
            settings.set("beekeeper.remote_address", str(remote_endpoint))

        if not (Beekeeper.get_remote_address_from_settings() or Beekeeper.get_path_from_settings()):
            raise BeekeeperNotConfiguredError

        self.__communication = communication or Communication()
        self.__run_in_background = run_in_background
        self.is_running = False
        self.is_starting = False
        self.config = BeekeeperConfig()
        self.__notification_server = BeekeeperNotificationsServer(lambda: self.token, notify_closing_wallet_name_cb)
        self.__notification_server_port: int | None = None
        self.api = BeekeeperApi(self)
        self.__executable = BeekeeperExecutable(self.config, run_in_background=run_in_background)
        self.__token: str | None = None

    async def __aenter__(self) -> Self:
        return await self.launch()

    async def __aexit__(self, _: type[Exception] | None, ex: Exception | None, ___: TracebackType | None) -> None:
        if not self.__run_in_background:
            await self.close()

    async def launch(self) -> Self:
        await self.__start()
        await self.__set_token()
        assert self.token
        return self

    @property
    def token(self) -> str:
        """
        Get token for current session.

        Raises
        ------
        BeekeeperTokenNotAvailableError: If token was not set yet.
        """
        if self.__token is None:
            raise BeekeeperTokenNotAvailableError
        return self.__token

    async def __set_token(self) -> None:
        self.__token = (
            await self.api.create_session(
                notifications_endpoint=f"127.0.0.1:{self.__notification_server_port}", salt=str(id(self))
            )
        ).token

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

    @contextmanager
    def modified_connection_details(
        self,
        max_attempts: int = Communication.DEFAULT_ATTEMPTS,
        timeout_secs: float = Communication.DEFAULT_TIMEOUT_TOTAL_SECONDS,
        pool_time_secs: float = Communication.DEFAULT_POOL_TIME_SECONDS,
    ) -> Iterator[None]:
        """Allows to temporarily change connection details."""
        with self.__communication.modified_connection_details(max_attempts, timeout_secs, pool_time_secs):
            yield

    @staticmethod
    def get_pid_from_file() -> int:
        return BeekeeperExecutable.get_pid_from_file()

    @staticmethod
    def is_already_running_locally() -> bool:
        return BeekeeperExecutable.is_already_running()

    async def _send(
        self, result_model: type[T], endpoint: str, **kwargs: Any  # noqa: ARG002
    ) -> JSONRPCResponse[T]:  # noqa: ARG002, RUF100
        await self.__assert_is_running()

        url = self.http_endpoint.as_string()
        request = JSONRPCRequest(method=endpoint, params=kwargs)
        response = await self.__communication.arequest(url, data=request.json(by_alias=True))

        if response.status != HTTPStatus.OK:
            raise BeekeeperNon200StatusCodeError

        result = await response.json()
        if "error" in result:
            raise BeekeeperResponseError(url, request, result)

        return_value = JSONRPCResponse[T](**result)

        if return_value.id_ != request.id_:
            raise BeekeeperNotMatchingIdJsonRPCError(request.id_, return_value.id_)

        logger.info(f"Returning model: {return_value}")
        return return_value

    async def __assert_is_running(self) -> None:
        if self.is_starting:
            return

        if not self.is_running:
            if self.__token is not None:
                await self.close()
            raise BeekeeperNotRunningError

    async def close(self) -> None:
        logger.info("Closing Beekeeper...")
        if self.__token:
            await self.api.close_session()
            self.__token = None
        await self.__close_beekeeper()
        self.is_running = False
        logger.info("Beekeeper closed.")

    def attach_wallet_closing_listener(self, listener: WalletClosingListener) -> None:
        self.__notification_server.attach_wallet_closing_listener(listener)

    def detach_wallet_closing_listener(self, listener: WalletClosingListener) -> None:
        self.__notification_server.detach_wallet_closing_listener(listener)

    async def __start(self, *, timeout: float = 5.0) -> None:
        logger.info("Starting Beekeeper...")
        self.is_starting = True
        self.__notification_server_port = await self.__notification_server.listen()
        if not (remote := self.get_remote_address_from_settings()):
            await self.__run_beekeeper(timeout=timeout)
        else:
            self.config.webserver_http_endpoint = remote

        assert self.config.webserver_http_endpoint is not None
        self.is_running = True
        self.is_starting = False
        logger.info(f"Beekeeper started on {self.config.webserver_http_endpoint}.")

    async def restart(self) -> None:
        await self.close()
        await self.launch()

    async def __run_beekeeper(self, *, timeout: float = 5.0) -> None:
        self.config.notifications_endpoint = Url("http", "127.0.0.1", self.__notification_server_port)
        self.__executable.run()

        if await event_wait(self.__notification_server.opening_beekeeper_failed, timeout):
            await self.__close_beekeeper()
            self.__notification_server_port = await self.__notification_server.listen()
            self.config.notifications_endpoint = Url("http", "127.0.0.1", self.__notification_server_port)
        elif not (
            await event_wait(self.__notification_server.http_listening_event, timeout)
            and await event_wait(self.__notification_server.ready, timeout)
        ):
            await self.__close_beekeeper()
            return

        logger.debug(f"Got webserver http endpoint: `{self.__notification_server.http_endpoint}`")
        self.config.webserver_http_endpoint = self.__notification_server.http_endpoint

    async def __close_beekeeper(self) -> None:
        try:
            self.__executable.close()
        finally:
            self.__notification_server_port = None
            self.config.webserver_http_endpoint = webserver_default()
            await self.__notification_server.close()

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
