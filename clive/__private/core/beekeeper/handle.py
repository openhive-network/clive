from __future__ import annotations

import asyncio
from contextlib import contextmanager
from http import HTTPStatus
from time import perf_counter
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
from clive.__private.core.beekeeper.notifications import BeekeeperNotificationsServer, WalletClosingListener
from clive.__private.core.communication import Communication
from clive.__private.logger import logger
from clive.core.url import Url
from clive.models.base import CliveBaseModel
from schemas.jsonrpc import ExpectResultT, JSONRPCRequest, JSONRPCResult, get_response_model

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
        self.api = BeekeeperApi(self)
        self.__executable = BeekeeperExecutable(self.config, run_in_background=run_in_background)
        self.__token: str | None = None
        self.__next_time_unlock = perf_counter()

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
                notifications_endpoint=self.__notification_server.http_endpoint.as_string(with_protocol=False),
                salt=str(id(self)),
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
        self, result_model: type[ExpectResultT], endpoint: str, **kwargs: Any
    ) -> JSONRPCResult[ExpectResultT]:  # noqa: ARG002, RUF100
        await self.__assert_is_running()

        url = self.http_endpoint.as_string()
        request = JSONRPCRequest(method=endpoint, params=kwargs)

        await self.__delay_on_unlock(endpoint)
        response = await self.__communication.arequest(
            url,
            data=request.json(by_alias=True),
            max_attempts=1,  # Beekeeper is not idempotent, so we don't retry e.g. unlock can't be retried to fast.
        )

        if response.status != HTTPStatus.OK:
            raise BeekeeperNon200StatusCodeError

        result = await response.json()
        response_model = get_response_model(result_model, **result)

        logger.info(f"Got beekeeper response: {response_model}")

        if response_model.id_ != request.id_:
            raise BeekeeperNotMatchingIdJsonRPCError(request.id_, response_model.id_)

        if not isinstance(response_model, JSONRPCResult):
            raise BeekeeperResponseError(url, request, result)
        return response_model

    async def __delay_on_unlock(self, endpoint: str) -> None:
        seconds_to_wait = 0.6
        endpoints_to_wait = ("beekeeper_api.unlock", "beekeeper_api.create_session")

        if endpoint not in endpoints_to_wait:
            return

        while perf_counter() < self.__next_time_unlock:
            logger.debug(f"Waiting for {endpoint} to be available...")
            await asyncio.sleep(0.1)

        self.__next_time_unlock = perf_counter() + seconds_to_wait

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
        await self.__start_notifications_server()
        if not (remote := self.get_remote_address_from_settings()):
            await self.__run_beekeeper(timeout=timeout)
        else:
            self.config.webserver_http_endpoint = remote

        assert self.config.webserver_http_endpoint is not None
        self.is_running = True
        self.is_starting = False
        logger.info(f"Beekeeper started on {self.config.webserver_http_endpoint}.")

    async def __start_notifications_server(self) -> None:
        address = await self.__notification_server.listen()
        self.config.notifications_endpoint = address

    async def restart(self) -> None:
        await self.close()
        await self.launch()

    async def __run_beekeeper(self, *, timeout: float = 5.0) -> None:
        self.__executable.run()

        start_task = asyncio.create_task(self.__wait_for_beekeeper_to_start(timeout))
        already_running_task = asyncio.create_task(self.__wait_for_beekeeper_report_already_running(timeout))

        try:
            done, _ = await asyncio.wait(
                [start_task, already_running_task],
                timeout=timeout,
                return_when=asyncio.FIRST_COMPLETED,
            )
        except asyncio.TimeoutError:
            await self.__close_beekeeper()
        else:
            if already_running_task in done:
                await self.__close_beekeeper(wait_for_deleted_pid=False, close_notifications_server=False)
            self.config.webserver_http_endpoint = self.__notification_server.beekeeper_webserver_http_endpoint

    async def __wait_for_beekeeper_to_start(self, timeout: float) -> bool:
        ready_event, http_listening_event = await asyncio.gather(
            event_wait(self.__notification_server.ready, timeout),
            event_wait(self.__notification_server.http_listening_event, timeout),
        )
        return ready_event and http_listening_event

    async def __wait_for_beekeeper_report_already_running(self, timeout: float) -> bool:
        return await event_wait(self.__notification_server.opening_beekeeper_failed, timeout)

    async def __close_beekeeper(
        self, *, wait_for_deleted_pid: bool = False, close_notifications_server: bool = True
    ) -> None:
        try:
            self.__executable.close(wait_for_deleted_pid=wait_for_deleted_pid)
        finally:
            if close_notifications_server:
                await self.__notification_server.close()
                self.config.webserver_http_endpoint = webserver_default()

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
