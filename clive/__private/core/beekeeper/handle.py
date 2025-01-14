from __future__ import annotations

import asyncio
import json
import shutil
import tempfile
from contextlib import contextmanager
from http import HTTPStatus
from pathlib import Path
from time import perf_counter
from typing import TYPE_CHECKING, Any, Final

from pydantic import Field, validator

from clive.__private.core._async import event_wait
from clive.__private.core.beekeeper.api import BeekeeperApi
from clive.__private.core.beekeeper.command_line_args import (
    BeekeeperCLIArguments,
    ExportKeysWalletParams,
)
from clive.__private.core.beekeeper.config import BeekeeperConfig, webserver_default
from clive.__private.core.beekeeper.defaults import BeekeeperDefaults
from clive.__private.core.beekeeper.exceptions import (
    BeekeeperNon200StatusCodeError,
    BeekeeperNotConfiguredError,
    BeekeeperNotificationServerNotSetError,
    BeekeeperNotMatchingIdJsonRPCError,
    BeekeeperNotRunningError,
    BeekeeperResponseError,
    BeekeeperTokenNotAvailableError,
    BeekeeperUrlNotSetError,
)
from clive.__private.core.beekeeper.executable import BeekeeperExecutable
from clive.__private.core.beekeeper.notifications import (
    BeekeeperNotificationsServer,
    WalletClosingListener,
)
from clive.__private.core.communication import Communication
from clive.__private.core.url import Url
from clive.__private.logger import logger
from clive.__private.models.base import CliveBaseModel
from clive.__private.models.schemas import (
    JSONRPCExpectResultT,
    JSONRPCRequest,
    JSONRPCResult,
    get_response_model,
)
from clive.__private.settings import safe_settings
from clive.dev import is_in_dev_mode

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator
    from types import TracebackType

    from typing_extensions import Self


ExportedKeys = list[dict[str, str]]


class Beekeeper:
    # We have 500ms time period protection on ulocking wallet, so we use 600ms to make sure that wallet is unlocked.
    UNLOCK_INTERVAL: Final[float] = 0.6
    DEFAULT_TIMEOUT_TOTAL_SECONDS: Final[float] = safe_settings.beekeeper.communication_total_timeout_secs
    DEFAULT_INITIALIZATION_TIMEOUT_SECONDS: Final[float] = safe_settings.beekeeper.initialization_timeout_secs

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
        remote_endpoint: Url | None = None,
        token: str | None = None,
        run_in_background: bool = False,
        notify_closing_wallet_name_cb: Callable[[], str] | None = None,
    ) -> None:
        if not (remote_endpoint or Beekeeper.get_remote_address_from_settings() or Beekeeper.get_path_from_settings()):
            raise BeekeeperNotConfiguredError

        self._remote_endpoint = remote_endpoint
        self.__communication = Communication(timeout_total_secs=self.DEFAULT_TIMEOUT_TOTAL_SECONDS)
        self.__run_in_background = run_in_background
        self.is_running = False
        self.is_starting = False
        self.config = BeekeeperConfig()
        self.__notification_server = BeekeeperNotificationsServer(lambda: self.token, notify_closing_wallet_name_cb)
        self.api = BeekeeperApi(self)
        self.__executable = BeekeeperExecutable(self.config, run_in_background=run_in_background)
        self.__token: str | None = token
        self._was_initial_token_set = token is not None
        self.__next_time_unlock = perf_counter()

    async def __aenter__(self) -> Self:
        # So that we can run async with await Beekeeper().launch(args=)
        if self.is_running:
            return self
        return await self.launch()

    async def __aexit__(
        self, _: type[BaseException] | None, ex: BaseException | None, ___: TracebackType | None
    ) -> None:
        if not self.__run_in_background:
            await self.close()

    async def launch(  # noqa: PLR0913
        self,
        *,
        backtrace: str = BeekeeperDefaults.DEFAULT_BACKTRACE,
        data_dir: Path = BeekeeperDefaults.DEFAULT_DATA_DIR,
        log_json_rpc: Path | None = BeekeeperDefaults.DEFAULT_LOG_JSON_RPC,
        notifications_endpoint: Url | None = BeekeeperDefaults.DEFAULT_NOTIFICATIONS_ENDPOINT,
        unlock_timeout: int = BeekeeperDefaults.DEFAULT_UNLOCK_TIMEOUT,
        wallet_dir: Path = BeekeeperDefaults.DEFAULT_WALLET_DIR,
        webserver_thread_pool_size: int = BeekeeperDefaults.DEFAULT_WEBSERVER_THREAD_POOL_SIZE,
        webserver_http_endpoint: Url | None = BeekeeperDefaults.DEFAULT_WEBSERVER_HTTP_ENDPOINT,
    ) -> Self:
        await self.__communication.setup()
        arguments: BeekeeperCLIArguments = BeekeeperCLIArguments(
            help=BeekeeperDefaults.DEFAULT_HELP,
            version=BeekeeperDefaults.DEFAULT_VERSION,
            dump_config=BeekeeperDefaults.DEFAULT_DUMP_CONFIG,
            backtrace=backtrace,
            data_dir=data_dir,
            log_json_rpc=log_json_rpc,
            notifications_endpoint=notifications_endpoint,
            unlock_timeout=unlock_timeout,
            wallet_dir=wallet_dir,
            webserver_thread_pool_size=webserver_thread_pool_size,
            webserver_http_endpoint=webserver_http_endpoint,
        )
        await self.__start(arguments=arguments)
        if not self._is_session_token_env_var_set() and not self.__token:
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
        if self._is_session_token_env_var_set():
            return str(safe_settings.beekeeper.session_token)
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
        if not self.config.webserver_http_endpoint and (
            remote := self._remote_endpoint or self.get_remote_address_from_settings()
        ):
            self.config.webserver_http_endpoint = remote

        if not self.config.webserver_http_endpoint:
            raise BeekeeperUrlNotSetError

        return self.config.webserver_http_endpoint

    @property
    def pid(self) -> int:
        return self.__executable.pid

    @property
    def notification_server_http_endpoint(self) -> Url:
        if self.config.notifications_endpoint is None:
            raise BeekeeperNotificationServerNotSetError
        return self.config.notifications_endpoint

    @property
    def is_opening_beekeeper_failed(self) -> bool:
        return self.__notification_server.opening_beekeeper_failed.is_set()

    @contextmanager
    def modified_connection_details(
        self,
        max_attempts: int = Communication.DEFAULT_ATTEMPTS,
        timeout_total_secs: float = DEFAULT_TIMEOUT_TOTAL_SECONDS,
        pool_time_secs: float = Communication.DEFAULT_POOL_TIME_SECONDS,
    ) -> Iterator[None]:
        """Allow to temporarily change connection details."""
        with self.__communication.modified_connection_details(max_attempts, timeout_total_secs, pool_time_secs):
            yield

    @staticmethod
    def get_pid_from_file() -> int:
        return BeekeeperExecutable.get_pid_from_file()

    @staticmethod
    def is_already_running_locally() -> bool:
        return BeekeeperExecutable.is_already_running()

    def _is_session_token_env_var_set(self) -> bool:
        return safe_settings.beekeeper.is_session_token_set

    async def _send(
        self, result_model: type[JSONRPCExpectResultT], endpoint: str, **kwargs: Any
    ) -> JSONRPCResult[JSONRPCExpectResultT]:  # noqa: ARG002, RUF100
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

        if is_in_dev_mode():
            logger.debug(f"Got beekeeper response: {response_model}")

        if response_model.id_ != request.id_:
            raise BeekeeperNotMatchingIdJsonRPCError(request.id_, response_model.id_)

        if not isinstance(response_model, JSONRPCResult):
            raise BeekeeperResponseError(url, request, result)
        return response_model

    async def __delay_on_unlock(self, endpoint: str) -> None:
        seconds_to_wait = self.UNLOCK_INTERVAL
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

    def get_wallet_dir(self) -> Path:
        return self.__executable.get_wallet_dir()

    async def close(self) -> None:
        if self._is_session_token_env_var_set() or self._was_initial_token_set:
            logger.info("Skipping beekeeper closure due to session token being explicitly set.")
            return
        logger.info("Closing Beekeeper...")
        if self.__token:
            await self.api.close_session()
            self.__token = None
        await self.__close_beekeeper()
        self.is_running = False
        await self.__communication.teardown()
        logger.info("Beekeeper closed.")

    def attach_wallet_closing_listener(self, listener: WalletClosingListener) -> None:
        self.__notification_server.attach_wallet_closing_listener(listener)

    def detach_wallet_closing_listener(self, listener: WalletClosingListener) -> None:
        self.__notification_server.detach_wallet_closing_listener(listener)

    async def __start(
        self, *, timeout: float = DEFAULT_INITIALIZATION_TIMEOUT_SECONDS, arguments: BeekeeperCLIArguments | None = None
    ) -> None:
        logger.info("Starting Beekeeper...")
        self.is_starting = True
        await self.__start_notifications_server()
        if not (remote := self._remote_endpoint or self.get_remote_address_from_settings()):
            await self.__run_beekeeper(timeout=timeout, arguments=arguments)
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

    async def __run_beekeeper(
        self, *, timeout: float = DEFAULT_INITIALIZATION_TIMEOUT_SECONDS, arguments: BeekeeperCLIArguments | None = None
    ) -> None:
        self.__executable.run(arguments=arguments)

        start_task = asyncio.create_task(self.__wait_for_beekeeper_to_start(timeout))
        already_running_task = asyncio.create_task(self.__wait_for_beekeeper_report_already_running(timeout))

        done, _ = await asyncio.wait(
            [start_task, already_running_task],
            timeout=timeout,
            return_when=asyncio.FIRST_COMPLETED,
        )

        if already_running_task in done and already_running_task.result():
            await self.__close_beekeeper(wait_for_deleted_pid=False, close_notifications_server=False)
            self.config.webserver_http_endpoint = self.__notification_server.beekeeper_webserver_http_endpoint
        elif start_task in done and start_task.result():
            self.config.webserver_http_endpoint = self.__notification_server.beekeeper_webserver_http_endpoint
        else:
            raise BeekeeperNotRunningError(
                f"Couldn't start or connect to locally running beekeeper instance in {timeout:.2f} seconds."
            )

    async def __wait_for_beekeeper_to_start(self, timeout: float) -> bool:
        ready_event, http_listening_event = await asyncio.gather(
            event_wait(self.__notification_server.ready, timeout),
            event_wait(self.__notification_server.http_listening_event, timeout),
        )
        return ready_event and http_listening_event

    async def __wait_for_beekeeper_report_already_running(self, timeout: float) -> bool:
        return await event_wait(self.__notification_server.opening_beekeeper_failed, timeout)

    async def __close_beekeeper(
        self, *, wait_for_deleted_pid: bool = True, close_notifications_server: bool = True
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
        return safe_settings.beekeeper.remote_address

    @classmethod
    def get_remote_address_from_connection_file(cls) -> Url | None:
        connection_file = BeekeeperConfig.get_wallet_dir() / "beekeeper.connection"
        if not connection_file.is_file():
            return None

        connection = cls.ConnectionFileData.parse_file(connection_file)

        return Url(connection.type_, connection.address, connection.port)

    def help(self) -> str:
        arguments = BeekeeperCLIArguments(help=True)
        return self.__executable.run_and_get_output(allow_empty_notification_server=True, arguments=arguments)

    def version(self) -> str:
        arguments = BeekeeperCLIArguments(version=True)
        return self.__executable.run_and_get_output(allow_empty_notification_server=True, arguments=arguments)

    def generate_beekeepers_default_config(self, destination: Path) -> None:
        with tempfile.TemporaryDirectory() as tmpdirname:
            arguments = BeekeeperCLIArguments(
                backtrace=None,
                data_dir=Path(tmpdirname),
                log_json_rpc=None,
                notifications_endpoint=None,
                unlock_timeout=None,
                wallet_dir=None,
                webserver_thread_pool_size=None,
                webserver_http_endpoint=None,
                dump_config=True,
            )
            self.__executable.run_and_get_output(allow_empty_notification_server=True, arguments=arguments)
            shutil.copyfile(Path(tmpdirname) / "config.ini", destination)

    async def export_keys_wallet(
        self, *, wallet_name: str, wallet_password: str, extract_to: Path | None = None
    ) -> ExportedKeys:
        with tempfile.TemporaryDirectory() as tmpdirname:
            shutil.copy(self.get_wallet_dir() / f"{wallet_name}.wallet", tmpdirname)
            bk = Beekeeper()
            arguments = BeekeeperCLIArguments(
                export_keys_wallet=ExportKeysWalletParams(wallet_name, wallet_password),
                # TODO : Workaround: Previously, there was no need to pass notifications_endpoint in order to dump keys.
                notifications_endpoint=Url(proto="http", host="127.0.0.1", port=-1),
                data_dir=Path(tmpdirname),
            )
            bk.__executable.run_and_get_output(allow_empty_notification_server=True, arguments=arguments)
            """Check if keys has been saved in dumped {wallet_name}.keys file."""
            wallet_path = Path.cwd() / f"{wallet_name}.keys"
            with wallet_path.open() as keys_file:
                if extract_to:
                    shutil.move(wallet_path, extract_to)
                keys: ExportedKeys = json.load(keys_file)
                return keys
