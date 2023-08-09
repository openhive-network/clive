from __future__ import annotations

import asyncio
import json
import time
import typing
from datetime import datetime, timedelta
from functools import partial
from typing import Any, ClassVar, Final

import httpx

from clive.__private.core._async import asyncio_run
from clive.__private.core.callback import invoke
from clive.__private.logger import logger
from clive.exceptions import CommunicationError, UnknownResponseFormatError

if typing.TYPE_CHECKING:
    from collections.abc import Callable


class CustomJSONEncoder(json.JSONEncoder):
    TIME_FORMAT_WITH_MILLIS: Final[str] = "%Y-%m-%dT%H:%M:%S.%f"

    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.strftime(self.TIME_FORMAT_WITH_MILLIS)

        return super().default(obj)


class Communication:
    DEFAULT_POOL_TIME_SECONDS: Final[float] = 0.2
    DEFAULT_ATTEMPTS: Final[int] = 1

    __async_client: ClassVar[httpx.AsyncClient | None] = None

    @classmethod
    def start(cls) -> None:
        if cls.__async_client is None:
            cls.__async_client = httpx.AsyncClient(timeout=2, http2=True)

    @classmethod
    async def close(cls) -> None:
        if cls.__async_client is not None:
            await cls.__async_client.aclose()
            cls.__async_client = None

    @classmethod
    def get_async_client(cls) -> httpx.AsyncClient:
        assert cls.__async_client is not None, "Session is closed."
        return cls.__async_client

    @classmethod
    def request(
        cls,
        url: str,
        *,
        data: Any,
        max_attempts: int = DEFAULT_ATTEMPTS,
        pool_time: timedelta = timedelta(seconds=DEFAULT_POOL_TIME_SECONDS),
    ) -> httpx.Response:
        return asyncio_run(
            cls.__request(url, sync=True, data=data, max_attempts=max_attempts, pool_time=pool_time),
        )

    @classmethod
    async def arequest(
        cls,
        url: str,
        *,
        data: Any,
        max_attempts: int = DEFAULT_ATTEMPTS,
        pool_time: timedelta = timedelta(seconds=DEFAULT_POOL_TIME_SECONDS),
    ) -> httpx.Response:
        return await cls.__request(url, sync=False, data=data, max_attempts=max_attempts, pool_time=pool_time)

    @classmethod
    async def __request(  # noqa: PLR0913
        cls,
        url: str,
        *,
        sync: bool,
        data: Any,
        max_attempts: int,
        pool_time: timedelta,
    ) -> httpx.Response:
        async def __sleep() -> None:
            seconds_to_sleep = pool_time.total_seconds()
            time.sleep(seconds_to_sleep) if sync else await asyncio.sleep(seconds_to_sleep)  # noqa: ASYNC101

        assert max_attempts > 0, "Max attempts must be greater than 0."

        result: dict[str, Any] = {}
        post_method: Callable[..., httpx.Response] = httpx.post if sync else cls.get_async_client().post  # type: ignore

        data_serialized = data if isinstance(data, str) else json.dumps(data, cls=CustomJSONEncoder)

        for attempts_left in reversed(range(max_attempts)):
            try:
                response: httpx.Response = await invoke(
                    callback=partial(
                        post_method, url, content=data_serialized, headers={"Content-Type": "application/json"}
                    )
                )
            except httpx.ConnectError as error:
                raise CommunicationError(url, data_serialized) from error

            result = response.json()

            if response.is_success:
                if "result" in result:
                    return response

                if "error" in result:
                    logger.debug(f"Error in response from {url=}, request={data_serialized}, response={result}")
                else:
                    raise UnknownResponseFormatError(url, data_serialized, result)
            else:
                logger.error(
                    f"Received bad status code: {response.status_code} from {url=}, request={data_serialized},"
                    f" response={result}"
                )

            if attempts_left > 0:
                await __sleep()

        raise CommunicationError(url, data_serialized, result)
