from __future__ import annotations

import asyncio
import json
from contextlib import contextmanager
from datetime import datetime
from json import JSONDecodeError
from typing import TYPE_CHECKING, Any, Final

import aiohttp

from clive.__private.core._async import asyncio_run
from clive.__private.logger import logger
from clive.exceptions import CliveError, CommunicationError, CommunicationTimeoutError, UnknownResponseFormatError

if TYPE_CHECKING:
    from collections.abc import Iterator

    from clive.__private.core.beekeeper.notification_http_server import JsonT
    from clive.exceptions import CommunicationResponseT

MISSING_API_ERROR_MESSAGE: Final[str] = "Could not find API"


class CustomJSONEncoder(json.JSONEncoder):
    TIME_FORMAT_WITH_MILLIS: Final[str] = "%Y-%m-%dT%H:%M:%S.%f"

    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.strftime(self.TIME_FORMAT_WITH_MILLIS)

        return super().default(obj)


class ErrorInResponseJsonError(CliveError):
    """Raised if "error" field found in response json."""

    def __init__(self, url: str, request: str, response: Any, *, details: str = "") -> None:
        self.url = url
        self.request = request
        self.response = response
        self.details = details
        additional_info = f"Details: {details} " if details else ""
        self.message = f"Error in response from {url=} {additional_info} {request=}, {response=}"
        super().__init__(self.message)


class MissingAPIError(ErrorInResponseJsonError):
    """Raised if error in response json is due to missing API."""

    def __init__(self, url: str, request: str, response: Any) -> None:
        details = f"{MISSING_API_ERROR_MESSAGE} found."
        super().__init__(url, request, response, details=details)


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
    ):
        self.__max_attempts = max_attempts
        self.__timeout_secs = timeout_secs
        self.__pool_time_secs = pool_time_secs

        assert self.__max_attempts > 0, "Max attempts must be greater than 0."
        assert self.__timeout_secs > 0, "Timeout must be greater than 0."
        assert self.__pool_time_secs >= 0, "Pool time must be greater or equal to 0."

    @contextmanager
    def modified_connection_details(
        self,
        max_attempts: int = DEFAULT_ATTEMPTS,
        timeout_secs: float = DEFAULT_TIMEOUT_TOTAL_SECONDS,
        pool_time_secs: float = DEFAULT_POOL_TIME_SECONDS,
    ) -> Iterator[None]:
        """Allows to temporarily change connection details."""
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
        data: Any,
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
        data: Any,
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
        data: Any,
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
        timeouts_count = 0

        async def next_try(error_: Exception | None = None) -> None:
            nonlocal attempt, exception
            exception = error_
            attempt += 1
            await asyncio.sleep(_pool_time_secs)

        def handle_timeout_error(context: str, error_: asyncio.TimeoutError) -> None:
            nonlocal timeouts_count, _max_attempts
            timeouts_count += 1
            logger.warning(f"Timeout error when {context}, request to {url=} took over {_timeout_secs} seconds.")
            if timeouts_count >= _max_attempts:
                raise CommunicationTimeoutError(url, data_serialized, _timeout_secs, timeouts_count) from error_

        async def return_response(response: aiohttp.ClientResponse) -> aiohttp.ClientResponse:
            await response.read()  # Ensure response is available outside of the context manager.
            return response

        while attempt < _max_attempts:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=_timeout_secs)) as session:
                try:
                    response = await session.post(
                        url,
                        data=data_serialized,
                        headers={"Content-Type": "application/json"},
                    )
                except aiohttp.ClientError as error:
                    logger.error(f"ClientError occurred: {error} from {url=}, request={data_serialized}")
                    await next_try(error)
                    continue
                except asyncio.TimeoutError as error:
                    handle_timeout_error("performing request", error)
                    continue
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
                            handle_timeout_error("reading text response", timeout_error)
                            continue
                        else:
                            await next_try(error)
                            continue
                    except asyncio.TimeoutError as error:
                        handle_timeout_error("reading json response", error)
                        continue

                    try:
                        self.__check_response(url=url, request=data_serialized, result=result)
                    except MissingAPIError:
                        # in case of missing API, we should not retry, because it can increase time of waiting
                        # when Clive is operation in non-full API mode
                        logger.debug(f"Ignoring {MISSING_API_ERROR_MESSAGE} found in the response.")
                        return await return_response(response)
                    except ErrorInResponseJsonError as error:
                        logger.error(f"Trying again because of: {error}")
                        await next_try()
                        continue
                    else:
                        return await return_response(response)
                else:
                    logger.error(f"Received bad status code: {response.status} from {url=}, request={data_serialized}")
                    result = await response.text()

            await next_try()

        raise CommunicationError(url, data_serialized, result) from exception

    @classmethod
    def __check_response(cls, url: str, request: str, result: Any) -> None:
        if isinstance(result, dict):
            cls.__check_response_item(url=url, request=request, response=result, item=result)
        elif isinstance(result, list):
            for item in result:
                cls.__check_response_item(url=url, request=request, response=result, item=item)
        else:
            raise UnknownResponseFormatError(url, request, result)

    @classmethod
    def __check_response_item(cls, url: str, request: str, response: Any, item: JsonT) -> None:
        if "error" in item:
            cls.__check_for_missing_api_error(url, request, item)
            raise ErrorInResponseJsonError(url, request, item, details=item["error"])
        if "result" not in item:
            raise UnknownResponseFormatError(url, request, response)

    @staticmethod
    def __check_for_missing_api_error(url: str, request: str, item: dict[str, Any]) -> None:
        message = item.get("error", {}).get("message", None)
        if message is not None and MISSING_API_ERROR_MESSAGE in message:
            raise MissingAPIError(url, request, item)
