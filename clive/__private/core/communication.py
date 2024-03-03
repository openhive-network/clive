from __future__ import annotations

import asyncio
import contextlib
import json
from contextlib import contextmanager
from datetime import datetime, timedelta
from json import JSONDecodeError
from typing import TYPE_CHECKING, Any, Final

import aiohttp
from helpy._communication.abc.communicator import AbstractCommunicator

from clive.__private.core._async import asyncio_run
from clive.__private.logger import logger
from clive.exceptions import (
    CliveError,
    CommunicationError,
    CommunicationTimeoutError,
)

if TYPE_CHECKING:
    from collections.abc import Iterator

    from helpy import HttpUrl

    from clive.exceptions import CommunicationResponseT


class CustomJSONEncoder(json.JSONEncoder):
    TIME_FORMAT_WITH_MILLIS: Final[str] = "%Y-%m-%dT%H:%M:%S.%f"

    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.strftime(self.TIME_FORMAT_WITH_MILLIS)

        return super().default(obj)


class ErrorInResponseJsonError(CliveError):
    """Raised if "error" field found in response json."""


class Communication(AbstractCommunicator):
    DEFAULT_ATTEMPTS: Final[int] = 5
    DEFAULT_TIMEOUT_TOTAL_SECONDS: Final[float] = 3
    DEFAULT_POOL_TIME_SECONDS: Final[float] = 0.2

    @contextmanager
    def modified_connection_details(
        self,
        max_attempts: int = DEFAULT_ATTEMPTS,
        timeout_secs: float = DEFAULT_TIMEOUT_TOTAL_SECONDS,
        pool_time_secs: float = DEFAULT_POOL_TIME_SECONDS,
    ) -> Iterator[None]:
        """Allows to temporarily change connection details."""
        with self.restore_settings():
            self.settings.max_retries = max_attempts
            self.settings.timeout = timedelta(seconds=timeout_secs)
            self.settings.period_between_retries = timedelta(seconds=pool_time_secs)
            yield

    def send(self, url: HttpUrl, data: str) -> str:
        return asyncio_run(self.__request(url=url, data=data))  # type: ignore[return-value]

    async def async_send(self, url: HttpUrl, data: str) -> str:
        return await (await self.__request(url=url, data=data)).text()

    async def __request(  # noqa: C901, PLR0915
        self,
        *,
        url: HttpUrl,
        data: Any,
    ) -> aiohttp.ClientResponse:
        result: CommunicationResponseT | None = None
        exception: Exception | None = None

        data_serialized = data if isinstance(data, str) else json.dumps(data, cls=CustomJSONEncoder)

        attempt = 0
        timeouts_count = 0

        async def next_try(error_: Exception | None = None) -> None:
            nonlocal attempt, exception
            exception = error_
            attempt += 1
            await self._async_sleep_for_retry()

        def handle_timeout_error(context: str, error_: asyncio.TimeoutError) -> None:
            nonlocal timeouts_count
            timeouts_count += 1
            logger.warning(
                f"Timeout error when {context}, request to {url=} took over {self.settings.timeout.seconds} seconds."
            )
            if timeouts_count >= self.settings.max_retries:
                raise CommunicationTimeoutError(
                    url, data_serialized, self.settings.timeout.seconds, timeouts_count
                ) from error_

        while not self._is_amount_of_retries_exceeded(attempt):
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.settings.timeout.seconds)
            ) as session:
                try:
                    attempt += 1
                    response = await session.post(
                        url.as_string(with_protocol=True),
                        data=data_serialized,
                        headers=self._json_headers(),
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

                    with contextlib.suppress(ErrorInResponseJsonError):
                        await response.read()  # Ensure response is available outside of the context manager.
                        return response
                else:
                    logger.error(f"Received bad status code: {response.status} from {url=}, request={data_serialized}")
                    result = await response.text()

            await next_try()

        raise CommunicationError(url, data_serialized, result) from exception
