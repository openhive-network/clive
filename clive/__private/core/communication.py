from __future__ import annotations

import asyncio
import contextlib
import json
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, Final

import httpx

from clive.__private.core._async import asyncio_run
from clive.__private.logger import logger
from clive.exceptions import CliveError, CommunicationError, UnknownResponseFormatError

if TYPE_CHECKING:
    from types import TracebackType

    from typing_extensions import Self


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
        self.__async_client: httpx.AsyncClient | None = None
        self.start()

    def start(self) -> None:
        if self.__async_client is None:
            self.__async_client = httpx.AsyncClient(timeout=2, http2=True)

    async def close(self) -> None:
        if self.__async_client is not None:
            await self.__async_client.aclose()
            self.__async_client = None

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, _: type[Exception] | None, ex: Exception | None, ___: TracebackType | None) -> None:
        await self.close()

    def __get_async_client(self) -> httpx.AsyncClient:
        assert self.__async_client is not None, "Session is closed."
        return self.__async_client

    def request(
        self,
        url: str,
        *,
        data: Any,
        max_attempts: int = DEFAULT_ATTEMPTS,
        pool_time: timedelta = timedelta(seconds=DEFAULT_POOL_TIME_SECONDS),
    ) -> httpx.Response:
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
    ) -> httpx.Response:
        return await self.__request(url, data=data, max_attempts=max_attempts, pool_time=pool_time)

    async def __request(
        self,
        url: str,
        *,
        data: Any,
        max_attempts: int,
        pool_time: timedelta,
    ) -> httpx.Response:
        async def __sleep() -> None:
            seconds_to_sleep = pool_time.total_seconds()
            await asyncio.sleep(seconds_to_sleep)

        assert max_attempts > 0, "Max attempts must be greater than 0."

        response: httpx.Response | None = None

        data_serialized = data if isinstance(data, str) else json.dumps(data, cls=CustomJSONEncoder)

        for attempts_left in reversed(range(max_attempts)):
            try:
                response = await self.__get_async_client().post(
                    url,
                    content=data_serialized,
                    headers={"Content-Type": "application/json"},
                )
            except httpx.ConnectError as error:
                raise CommunicationError(url, data_serialized) from error

            assert response is not None
            if response.is_success:
                result = response.json()
                with contextlib.suppress(ErrorInResponseJsonError):
                    if isinstance(result, list):
                        for item in result:
                            self.__check_response_item(item=item, url=url, request=data_serialized)
                    if isinstance(result, dict):
                        self.__check_response_item(item=result, url=url, request=data_serialized)
                    return response
            else:
                logger.error(f"Received bad status code: {response.status_code} from {url=}, request={data_serialized}")

            if attempts_left > 0:
                await __sleep()

        raise CommunicationError(url, data_serialized, response)

    @classmethod
    def __check_response_item(cls, item: dict[str, Any], url: str, request: str) -> dict[str, Any]:
        if "error" in item:
            logger.debug(f"Error in response from {url=}, request={request}, response={item}")
            raise ErrorInResponseJsonError
        if "result" not in item:
            raise UnknownResponseFormatError(url, request, item)
        return item
