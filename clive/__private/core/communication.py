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
    from clive.__private.core.beekeeper.notification_http_server import JsonT
    from clive.exceptions import CommunicationResponseT


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

    @classmethod
    def request(
        cls,
        url: str,
        *,
        data: Any,
        max_attempts: int = DEFAULT_ATTEMPTS,
        pool_time: timedelta = timedelta(seconds=DEFAULT_POOL_TIME_SECONDS),
    ) -> aiohttp.ClientResponse:
        return asyncio_run(
            cls.__request(url, data=data, max_attempts=max_attempts, pool_time=pool_time),
        )

    @classmethod
    async def arequest(
        cls,
        url: str,
        *,
        data: Any,
        max_attempts: int = DEFAULT_ATTEMPTS,
        pool_time: timedelta = timedelta(seconds=DEFAULT_POOL_TIME_SECONDS),
    ) -> aiohttp.ClientResponse:
        return await cls.__request(url, data=data, max_attempts=max_attempts, pool_time=pool_time)

    @classmethod
    async def __request(
        cls,
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

        result: CommunicationResponseT | None = None

        data_serialized = data if isinstance(data, str) else json.dumps(data, cls=CustomJSONEncoder)

        for attempts_left in reversed(range(max_attempts)):
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=2)) as session:
                try:
                    response = await session.post(
                        url,
                        data=data_serialized,
                        headers={"Content-Type": "application/json"},
                    )
                except aiohttp.ClientError as error:
                    raise CommunicationError(url, data_serialized) from error

                if response.ok:
                    try:
                        result = await response.json()
                    except aiohttp.ContentTypeError:
                        result = await response.text()
                        break

                    with contextlib.suppress(ErrorInResponseJsonError):
                        cls.__check_response(url=url, request=data_serialized, result=result)
                        await response.read()  # Ensure response is available outside of the context manager.
                        return response
                else:
                    logger.error(f"Received bad status code: {response.status} from {url=}, request={data_serialized}")
                    result = await response.text()

            if attempts_left > 0:
                await __sleep()

        assert result is not None, "Result should be set at this point."
        raise CommunicationError(url, data_serialized, result)

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
            logger.debug(f"Error in response from {url=}, request={request}, response={response}")
            raise ErrorInResponseJsonError
        if "result" not in item:
            raise UnknownResponseFormatError(url, request, response)
