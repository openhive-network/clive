from __future__ import annotations

from typing import TYPE_CHECKING, Any

from httpx import codes, post

from clive.__private.config import settings
from clive.__private.core.beekeeper.api import BeekeeperApi
from clive.__private.core.beekeeper.config import BeekeeperConfig, webserver_default
from clive.__private.core.beekeeper.executable import BeekeeperExecutable
from clive.__private.core.beekeeper.model import JSONRPCRequest, JSONRPCResponse, T
from clive.__private.core.beekeeper.notifications import BeekeeperNotificationsServer
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


class BeekeeperRemote:
    def __init__(self) -> None:
        self.__address = self.get_address_from_settings()
        self.api = BeekeeperApi(self)

    def _send(self, response: type[T], endpoint: str, **kwargs: Any) -> JSONRPCResponse[T]:  # noqa: ARG002, RUF100
        url = self._get_request_url()

        if url is None:
            raise UrlNotSetError()

        request = JSONRPCRequest(method=endpoint, params=kwargs)
        result = post(url.as_string(), json=request.dict(by_alias=True))

        if result.status_code != codes.OK:
            raise Non200StatusCodeError()

        json = result.json()
        if "error" in json:
            raise ErrorResponseError(request, json)

        return_value = JSONRPCResponse[T](**json)

        if return_value.id_ != request.id_:
            raise NotMatchingIdJsonRPCError(request.id_, return_value.id_)

        logger.info(f"Returning model: {return_value}")
        return return_value

    def _get_request_url(self) -> Url | None:
        return self.__address

    @classmethod
    def get_address_from_settings(cls) -> Url | None:
        raw_address = settings.get("beekeeper.remote_address")
        return Url.parse(raw_address) if raw_address else None


class Beekeeper(BeekeeperRemote):
    def __init__(self) -> None:
        self.__executable = BeekeeperExecutable()
        self.__notification_server = BeekeeperNotificationsServer()
        self.config = BeekeeperConfig()
        super().__init__()

    def _get_request_url(self) -> Url | None:
        return self.config.webserver_http_endpoint

    def run(self, *, timeout: float = 5.0) -> None:
        self.config.notifications_endpoint = Url("http", "127.0.0.1", self.__notification_server.listen())
        self.__executable.run(self.config)

        is_listening = self.__notification_server.http_listening_event.wait(timeout)
        if not is_listening:
            self.__executable.close()
            self.__notification_server.close()
            error_message = "Beekeeper didn't start on time"
            logger.error(error_message)
            raise TimeoutError(error_message)

        logger.debug(f"Got webserver http endpoint: `{self.__notification_server.http_endpoint}`")
        self.config.webserver_http_endpoint = self.__notification_server.http_endpoint

    def close(self) -> None:
        try:
            self.__executable.close()
        finally:
            self.config.notifications_endpoint = None
            self.config.webserver_http_endpoint = webserver_default()
            self.__notification_server.close()

    def restart(self) -> None:
        self.close()
        self.run()

    @classmethod
    def get_path_from_settings(cls) -> Path | None:
        return BeekeeperExecutable.get_path_from_settings()
