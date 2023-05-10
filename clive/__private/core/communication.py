from __future__ import annotations

import asyncio
import json
import time
import typing
from datetime import datetime, timedelta
from functools import partial
from typing import Any, Final

import httpx

from clive.__private.core._async import asyncio_run
from clive.__private.core.callback import invoke
from clive.__private.logger import logger
from clive.exceptions import CommunicationError, UnknownResponseFormatError

if typing.TYPE_CHECKING:
    from collections.abc import Callable


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()

        return super().default(obj)


class Communication:
    DEFAULT_POOL_TIME_SECONDS: Final[float] = 0.2
    DEFAULT_ATTEMPTS: Final[int] = 3

    __async_client: httpx.AsyncClient | None = None

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
        data: dict[str, Any],
        max_attempts: int = DEFAULT_ATTEMPTS,
        pool_time: timedelta = timedelta(seconds=DEFAULT_POOL_TIME_SECONDS),
    ) -> httpx.Response:
        return typing.cast(
            httpx.Response,
            asyncio_run(cls.__request(url, sync=True, data=data, max_attempts=max_attempts, pool_time=pool_time)),
        )

    @classmethod
    async def arequest(
        cls,
        url: str,
        *,
        data: dict[str, Any],
        max_attempts: int = DEFAULT_ATTEMPTS,
        pool_time: timedelta = timedelta(seconds=DEFAULT_POOL_TIME_SECONDS),
    ) -> httpx.Response:
        return await cls.__request(url, sync=False, data=data, max_attempts=max_attempts, pool_time=pool_time)

    @classmethod
    async def __request(
        cls,
        url: str,
        *,
        sync: bool,
        data: dict[str, Any],
        max_attempts: int,
        pool_time: timedelta,
    ) -> httpx.Response:
        async def __sleep() -> None:
            seconds_to_sleep = pool_time.total_seconds()
            time.sleep(seconds_to_sleep) if sync else await asyncio.sleep(seconds_to_sleep)

        assert max_attempts > 0, "Max attempts must be greater than 0."

        result: dict[str, Any] = {}
        post_method: Callable[..., httpx.Response] = httpx.post if sync else cls.get_async_client().post  # type: ignore

        for attempts_left in reversed(range(max_attempts)):
            serialized = json.dumps(data, cls=CustomJSONEncoder)
            response: httpx.Response = await invoke(callback=partial(post_method, url, json=serialized))
            result = response.json()

            if response.is_success:
                if "result" in result:
                    return response

                if "error" in result:
                    logger.debug(f"Error in response from {url=}, {data=}, {result=}")
                else:
                    raise UnknownResponseFormatError(response)
            else:
                message = f"Received bad status code: {response.status_code} from {url=}, {data=}, {result=}"
                logger.error(message)

            if attempts_left > 0:
                await __sleep()

        raise CommunicationError(f"Problem occurred during communication with {url=}, {data=}, {result=}")
