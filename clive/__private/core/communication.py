from __future__ import annotations

import asyncio
import contextlib
import json
from contextlib import contextmanager
from datetime import datetime
from json import JSONDecodeError
from typing import TYPE_CHECKING, Any, Final

import aiohttp
from typing_extensions import Self

from clive.__private.core._async import asyncio_run
from clive.__private.core.constants.date import TIME_FORMAT_WITH_MILLIS
from clive.__private.logger import logger
from clive.exceptions import CliveError, CommunicationError, CommunicationTimeoutError, UnknownResponseFormatError

if TYPE_CHECKING:
    from collections.abc import Iterator
    from types import TracebackType

    from clive.__private.core.beekeeper.notification_http_server import JsonT
    from clive.exceptions import CommunicationResponseT


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:  # noqa: ANN401
        if isinstance(obj, datetime):
            return obj.strftime(TIME_FORMAT_WITH_MILLIS)

        return super().default(obj)


class ErrorInResponseJsonError(CliveError):
    """Raised if "error" field found in response json."""


class NullResultInResponseJsonError(CliveError):
    """Raised if "result" field is None in response json."""


class Communication:
    DEFAULT_ATTEMPTS: Final[int] = 5
    DEFAULT_TIMEOUT_TOTAL_SECONDS: Final[float] = 3
    DEFAULT_POOL_TIME_SECONDS: Final[float] = 0.2

    def __init__(
        self,
        *,
        max_attempts: int = DEFAULT_ATTEMPTS,
        timeout_secs: float = DEFAULT_TIMEOUT_TOTAL_SECONDS,
        pool_time_secs: float = DEFAULT_POOL_TIME_SECONDS,
    ) -> None:
        self.__max_attempts = max_attempts
        self.__timeout_secs = timeout_secs
        self.__pool_time_secs = pool_time_secs
        self.__session: aiohttp.ClientSession | None = None

        assert self.__max_attempts > 0, "Max attempts must be greater than 0."
        assert self.__timeout_secs > 0, "Timeout must be greater than 0."
        assert self.__pool_time_secs >= 0, "Pool time must be greater or equal to 0."

    async def __aenter__(self) -> Self:
        await self.setup()
        return self

    async def __aexit__(
        self, _: type[BaseException] | None, __: BaseException | None, ___: TracebackType | None
    ) -> None:
        await self.teardown()

    async def setup(self) -> None:
        if self.__session is None:
            self.__session = aiohttp.ClientSession()

    async def teardown(self) -> None:
        if self.__session is not None:
            await self.__session.close()
            self.__session = None

    @property
    def _session(self) -> aiohttp.ClientSession:
        assert self.__session is not None, "Session is not started."
        return self.__session

    @contextmanager
    def modified_connection_details(
        self,
        max_attempts: int = DEFAULT_ATTEMPTS,
        timeout_secs: float = DEFAULT_TIMEOUT_TOTAL_SECONDS,
        pool_time_secs: float = DEFAULT_POOL_TIME_SECONDS,
    ) -> Iterator[None]:
        """Temporarily change connection details."""
        before = {
            "max_attempts": self.__max_attempts,
            "timeout_secs": self.__timeout_secs,
            "pool_time_secs": self.__pool_time_secs,
        }
        self.__max_attempts = max_attempts
        self.__timeout_secs = timeout_secs
        self.__pool_time_secs = pool_time_secs
        try:
            yield
        finally:
            self.__max_attempts = before["max_attempts"]  # type: ignore[assignment]
            self.__timeout_secs = before["timeout_secs"]
            self.__pool_time_secs = before["pool_time_secs"]

    def request(  # noqa: PLR0913
        self,
        url: str,
        *,
        data: Any,  # noqa: ANN401
        max_attempts: int | None = None,
        timeout_secs: float | None = None,
        pool_time_secs: float | None = None,
    ) -> aiohttp.ClientResponse:
        """
        Make a single sync request to the given url.

        Args:
        ----
        =====
        url: url to send request to.
        data: data to send.
        max_attempts: max attempts to send request (will override the value given during Communication creation)
        timeout_secs: timeout in seconds (will override the value given during Communication creation)
        pool_time_secs: time to wait between attempts (will override the value given during Communication creation)
        """
        return asyncio_run(
            self.__request(
                url, data=data, max_attempts=max_attempts, timeout_secs=timeout_secs, pool_time_secs=pool_time_secs
            )
        )

    async def arequest(  # noqa: PLR0913
        self,
        url: str,
        *,
        data: Any,  # noqa: ANN401
        max_attempts: int | None = None,
        timeout_secs: float | None = None,
        pool_time_secs: float | None = None,
    ) -> aiohttp.ClientResponse:
        """
        Make a single async request to the given url.

        Args:
        ----
        =====
        url: url to send request to.
        data: data to send.
        max_attempts: max attempts to send request (will override the value given during Communication creation)
        timeout_secs: timeout in seconds (will override the value given during Communication creation)
        pool_time_secs: time to wait between attempts (will override the value given during Communication creation)
        """
        return await self.__request(
            url, data=data, max_attempts=max_attempts, timeout_secs=timeout_secs, pool_time_secs=pool_time_secs
        )

    async def __request(  # noqa: PLR0913, C901, PLR0915
        self,
        url: str,
        *,
        data: Any,  # noqa: ANN401
        max_attempts: int | None = None,
        timeout_secs: float | None = None,
        pool_time_secs: float | None = None,
    ) -> aiohttp.ClientResponse:
        _max_attempts = max_attempts or self.__max_attempts
        _timeout_secs = timeout_secs or self.__timeout_secs
        _pool_time_secs = pool_time_secs or self.__pool_time_secs

        assert _max_attempts > 0, "Max attempts must be greater than 0."
        assert _timeout_secs > 0, "Timeout must be greater than 0."
        assert _pool_time_secs >= 0, "Pool time must be greater or equal to 0."

        result: CommunicationResponseT | None = None
        exception: Exception | None = None

        data_serialized = data if isinstance(data, str) else json.dumps(data, cls=CustomJSONEncoder)

        attempt = 0

        async def next_try(error_: Exception | None = None) -> None:
            nonlocal attempt, exception
            exception = error_
            attempt += 1
            await asyncio.sleep(_pool_time_secs)

        def raise_timeout_error(context: str, error_: asyncio.TimeoutError) -> None:
            raise CommunicationTimeoutError(url, data_serialized, _timeout_secs, context) from error_

        while attempt < _max_attempts:
            try:
                response = await self._session.post(
                    url,
                    data=data_serialized,
                    headers={"Content-Type": "application/json"},
                    timeout=aiohttp.ClientTimeout(total=_timeout_secs),
                )
            except aiohttp.ClientError as error:
                logger.error(f"ClientError occurred: {error} from {url=}, request={data_serialized}")
                await next_try(error)
                continue
            except asyncio.TimeoutError as error:
                raise_timeout_error("performing request", error)
            except Exception as error:  # noqa: BLE001
                logger.error(f"Unexpected error occurred: {error} from {url=}, request={data_serialized}")
                await next_try(error)
                continue

            if response.ok:
                try:
                    result = await response.json()
                except (aiohttp.ContentTypeError, JSONDecodeError) as error:
                    try:
                        result = await response.text()
                    except asyncio.TimeoutError as timeout_error:
                        raise_timeout_error("reading text response", timeout_error)
                    else:
                        await next_try(error)
                        continue
                except asyncio.TimeoutError as error:
                    raise_timeout_error("reading json response", error)

                with contextlib.suppress(ErrorInResponseJsonError, NullResultInResponseJsonError):
                    self.__check_response(url=url, request=data_serialized, result=result)
                    await response.read()  # Ensure response is available outside of the context manager.
                    return response
            else:
                logger.error(f"Received bad status code: {response.status} from {url=}, request={data_serialized}")
                result = await response.text()

            await next_try()

        raise CommunicationError(url, data_serialized, result) from exception

    @classmethod
    def __check_response(cls, url: str, request: str, result: Any) -> None:  # noqa: ANN401
        if isinstance(result, dict):
            cls.__check_response_item(url=url, request=request, response=result, item=result)
        elif isinstance(result, list):
            for item in result:
                cls.__check_response_item(url=url, request=request, response=result, item=item)
        else:
            raise UnknownResponseFormatError(url, request, result)

    @classmethod
    def __check_response_item(cls, url: str, request: str, response: Any, item: JsonT) -> None:  # noqa: ANN401
        if "error" in item:
            logger.debug(f"Error in response from {url=}, request={request}, response={response}")
            raise ErrorInResponseJsonError
        if "result" in item:
            if item["result"] is not None:
                return  # everything's good
            # null result is some kind of random error, it could be already observed in
            # account_history_api.get_account_history call
            # where the result was null:
            # {'id': 3, 'jsonrpc': '2.0', 'result': None}  # noqa: ERA001
            # even though account for sure had some history (blocktrades.com)
            # when account history plugin is not enabled on a node, still there is no null result but an error response
            logger.debug(f"Null result from {url=}, request={request}, response={response}")
            raise NullResultInResponseJsonError
        raise UnknownResponseFormatError(url, request, response)
