from __future__ import annotations

import asyncio
import contextlib
import json
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, Final

import aiohttp

from clive.__private.core._async import asyncio_run
from clive.__private.logger import logger
from clive.exceptions import CliveError, CommunicationError, UnknownResponseFormatError

if TYPE_CHECKING:
    from types import TracebackType

    from typing_extensions import Self

    from clive.__private.core.beekeeper.notification_http_server import JsonT


class CustomJSONEncoder(json.JSONEncoder):
    TIME_FORMAT_WITH_MILLIS: Final[str] = "%Y-%m-%dT%H:%M:%S.%f"

    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.strftime(self.TIME_FORMAT_WITH_MILLIS)

        return super().default(obj)


class ErrorInResponseJsonError(CliveError):
    """Raised if "error" field found in response json."""


class Communication:
    DEFAULT_POOL_TIME_SECONDS: Final[float] = 0.2
    DEFAULT_ATTEMPTS: Final[int] = 1

    def __init__(self) -> None:
        self.__async_client: aiohttp.ClientSession | None = None
        self.start()

    def start(self) -> None:
        if self.__async_client is None:
            self.__async_client = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=2))

    async def close(self) -> None:
        if self.__async_client is not None:
            await self.__async_client.close()
            self.__async_client = None

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, _: type[Exception] | None, ex: Exception | None, ___: TracebackType | None) -> None:
        await self.close()

    def __get_async_client(self) -> aiohttp.ClientSession:
        assert self.__async_client is not None, "Session is closed."
        return self.__async_client

    def request(
        self,
        url: str,
        *,
        data: Any,
        max_attempts: int = DEFAULT_ATTEMPTS,
        pool_time: timedelta = timedelta(seconds=DEFAULT_POOL_TIME_SECONDS),
    ) -> aiohttp.ClientResponse:
        return asyncio_run(
            self.__request(url, data=data, max_attempts=max_attempts, pool_time=pool_time),
        )

    async def arequest(
        self,
        url: str,
        *,
        data: Any,
        max_attempts: int = DEFAULT_ATTEMPTS,
        pool_time: timedelta = timedelta(seconds=DEFAULT_POOL_TIME_SECONDS),
    ) -> aiohttp.ClientResponse:
        return await self.__request(url, data=data, max_attempts=max_attempts, pool_time=pool_time)

    async def __request(
        self,
        url: str,
        *,
        data: Any,
        max_attempts: int,
        pool_time: timedelta,
    ) -> aiohttp.ClientResponse:
        async def __sleep() -> None:
            seconds_to_sleep = pool_time.total_seconds()
            await asyncio.sleep(seconds_to_sleep)

        assert max_attempts > 0, "Max attempts must be greater than 0."

        response: aiohttp.ClientResponse | None = None

        data_serialized = data if isinstance(data, str) else json.dumps(data, cls=CustomJSONEncoder)

        for attempts_left in reversed(range(max_attempts)):
            try:
                response = await self.__get_async_client().post(
                    url,
                    data=data_serialized,
                    headers={"Content-Type": "application/json"},
                )

            except aiohttp.ClientError as error:
                raise CommunicationError(url, data_serialized) from error

            assert response is not None
            if response.ok:
                result = await response.json()
                with contextlib.suppress(ErrorInResponseJsonError):
                    if isinstance(result, list):
                        for item in result:
                            self.__check_response_item(item=item, url=url, request=data_serialized)
                    if isinstance(result, dict):
                        self.__check_response_item(item=result, url=url, request=data_serialized)
                    return response
            else:
                logger.error(f"Received bad status code: {response.status} from {url=}, request={data_serialized}")

            if attempts_left > 0:
                await __sleep()

        assert response is not None

        try:
            result = await response.json()
        except aiohttp.ContentTypeError as error:
            raise CommunicationError(url, data_serialized, await response.text()) from error
        raise CommunicationError(url, data_serialized, result)

    @classmethod
    def __check_response_item(cls, item: JsonT, url: str, request: str) -> JsonT:
        if "error" in item:
            logger.debug(f"Error in response from {url=}, request={request}, response={item}")
            raise ErrorInResponseJsonError
        if "result" not in item:
            raise UnknownResponseFormatError(url, request, item)
        return item
