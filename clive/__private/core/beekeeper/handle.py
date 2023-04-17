from __future__ import annotations

from typing import TYPE_CHECKING, Any

from httpx import codes, post

from clive.__private.core.beekeeper.api import BeekeeperApi
from clive.__private.core.beekeeper.config import BeekeeperConfig, webserver_default
from clive.__private.core.beekeeper.executable import BeekeeperExecutable
from clive.__private.core.beekeeper.model import HiveResponse, T
from clive.__private.core.beekeeper.notifications import BeekeeperNotificationsServer
from clive.__private.core.beekeeper.url import Url
from clive.__private.logger import logger
from clive.exceptions import CommunicationError

if TYPE_CHECKING:
    from pathlib import Path

    from clive.__private.core.beekeeper.notification_http_server import JsonT


class Beekeeper:
    class UrlNotSetError(CommunicationError):
        pass

    class Non200StatusCodeError(CommunicationError):
        pass

    class ErrorResponseError(CommunicationError):
        def __init__(self, request: JsonT, response: JsonT) -> None:
            logger.error(
                f"""
For request: {request}

Got error response: {response}
            """
            )
            super().__init__(request, response)

    class NotMatchingIdJsonRPCError(CommunicationError):
        def __init__(self, given: Any, got: Any) -> None:
            logger.error(f"Id sent: `{given}`, got: `{got}`")
            super().__init__(given, got)

    def __init__(self, *, executable: Path | None = None) -> None:
        self.__executable = BeekeeperExecutable(executable=executable)
        self.__notification_server = BeekeeperNotificationsServer()
        self.config = BeekeeperConfig()
        self.api = BeekeeperApi(self)

    def _send(self, response: type[T], endpoint: str, **kwargs: Any) -> HiveResponse[T]:  # noqa: ARG002, RUF100
        url = self.config.webserver_http_endpoint

        if url is None:
            raise Beekeeper.UrlNotSetError()

        request = {"id": 0, "jsonrpc": "2.0", "method": endpoint, "params": kwargs}
        result = post(url.as_string(), json=request)

        if result.status_code != codes.OK:
            raise Beekeeper.Non200StatusCodeError()

        return_value = HiveResponse[T](**result.json())

        if return_value.error is not None:
            raise Beekeeper.ErrorResponseError(request, result.json())

        if return_value.id != request["id"]:
            raise Beekeeper.NotMatchingIdJsonRPCError(request["id"], return_value.id)

        logger.info(f"Returning model: {return_value}")
        return return_value

    def run(self, *, timeout: float = 5.0) -> None:
        self.config.notifications_endpoint = Url(f"127.0.0.1:{self.__notification_server.listen()}")
        self.__executable.run(self.config)
        try:
            if not self.__notification_server.http_listening_event.wait(timeout):
                raise TimeoutError()  # noqa: TRY301
            logger.debug(f"Got webserver http endpoint: `{self.__notification_server.http_endpoint}`")
            self.config.webserver_http_endpoint = self.__notification_server.http_endpoint
        except TimeoutError:
            self.__executable.close()
            self.__notification_server.close()
            logger.error("Beekeeper didn't start on time")  # noqa: TRY400
            raise

    def close(self) -> None:
        try:
            self.__executable.close()
        finally:
            self.config.notifications_endpoint = None
            self.config.webserver_http_endpoint = webserver_default()
