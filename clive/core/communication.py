from __future__ import annotations

import asyncio
from datetime import timedelta
from typing import Any

import httpx
from loguru import logger
from textual import log

from clive.exceptions import CommunicationError, UnknownResponseFormatError


class Communication:
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
    async def request(
        cls, url: str, *, data: dict[str, Any], max_attempts: int = 3, pool_time: timedelta = timedelta(seconds=0.2)
    ) -> httpx.Response:
        assert max_attempts > 0, "Max attempts must be greater than 0."

        client = cls.get_async_client()

        for attempts_left in reversed(range(max_attempts)):
            response = await client.post(url, json=data)

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
                logger.debug(message)
                log(message)

            if attempts_left > 0:
                await asyncio.sleep(pool_time.total_seconds())

        raise CommunicationError(f"Problem occurred during communication with {url=}, {data=}, {result=}")
