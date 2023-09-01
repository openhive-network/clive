from __future__ import annotations

import asyncio
import contextlib
import json
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, Final

import aiohttp

from clive.__private.core._async import asyncio_run
from clive.__private.logger import logger
from clive.exceptions import CliveError, CommunicationError, CommunicationTimeoutError, UnknownResponseFormatError

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator

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
    DEFAULT_ATTEMPTS: Final[int] = 5
    TIMEOUT_TOTAL: Final[float] = 3
    _SESSION: aiohttp.ClientSession | None = None
    _overriden_attempts: int | None = None

    @classmethod
    def start(cls) -> None:
        if cls._SESSION is None:
            cls._SESSION = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=cls.TIMEOUT_TOTAL))

    @classmethod
    async def close(cls) -> None:
        if cls._SESSION is not None:
            await cls._SESSION.close()
            cls._SESSION = None

    @classmethod
    def __get_session(cls) -> aiohttp.ClientSession:
        assert cls._SESSION is not None, "Communication was not started."
        return cls._SESSION

    @classmethod
    @contextlib.contextmanager
    def overriden_attempts(cls, attempts: int = 1) -> Iterator[None]:
        cls._overriden_attempts = attempts
        yield
        cls._overriden_attempts = None

    @classmethod
    @contextlib.asynccontextmanager
    async def lifecycle(cls) -> AsyncIterator[None]:
        cls.start()
        try:
            yield
        finally:
            await cls.close()

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
        max_attempts = max_attempts if not cls._overriden_attempts else 1

        result: CommunicationResponseT | None = None

        data_serialized = data if isinstance(data, str) else json.dumps(data, cls=CustomJSONEncoder)

        attempt = 0
        timeouts_count = 0
        while attempt < max_attempts:
            try:
                response = await cls.__get_session().post(
                    url,
                    data=data_serialized,
                    headers={"Content-Type": "application/json"},
                )
            except aiohttp.ClientOSError:
                # https://github.com/aio-libs/aiohttp/issues/6138
                continue
            except aiohttp.ClientError as error:
                raise CommunicationError(url, data_serialized) from error
            except asyncio.TimeoutError as error:
                attempt += 1
                timeouts_count += 1
                logger.warning(f"Timeout error, request to {url=} took over {cls.TIMEOUT_TOTAL} seconds.")
                if timeouts_count >= max_attempts:  # there were only timeouts
                    raise CommunicationTimeoutError(url, data_serialized, cls.TIMEOUT_TOTAL, timeouts_count) from error
                continue

            if response.ok:
                try:
                    result = await response.json()
                except aiohttp.ContentTypeError:
                    result = await response.text()
                    break

                with contextlib.suppress(ErrorInResponseJsonError):
                    cls.__check_response(url=url, request=data_serialized, result=result)
                    return response
            else:
                logger.error(f"Received bad status code: {response.status} from {url=}, request={data_serialized}")
                result = await response.text()

            await __sleep()
            attempt += 1

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
