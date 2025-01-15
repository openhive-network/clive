from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse

import aiohttp
from typing_extensions import Self

from clive.exceptions import CliveError


class UrlError(CliveError):
    """Base class for all Url exceptions."""


@dataclass(frozen=True)
class Url:
    proto: str
    host: str
    port: int | None = None

    @classmethod
    def parse(cls, url: str | Self, *, protocol: str = "") -> Url:
        if isinstance(url, Url):
            return url

        parsed_url = urlparse(url, scheme=protocol)

        if not parsed_url.netloc:
            parsed_url = urlparse(f"//{url}", scheme=protocol)

        if not parsed_url.hostname:
            raise UrlError("Hostname is not specified.")

        return Url(parsed_url.scheme, parsed_url.hostname, parsed_url.port)

    async def is_url_open(self) -> bool:
        try:
            async with aiohttp.ClientSession() as session, session.get(self.as_string()) as resp:
                return resp.ok
        except aiohttp.ClientConnectorError:
            return False

    def as_string(self, *, with_protocol: bool = True) -> str:
        protocol_prefix = f"{self.proto}://" if with_protocol and self.proto else ""
        port_suffix = f":{self.port}" if self.port is not None else ""

        return f"{protocol_prefix}{self.host}{port_suffix}"

    def __str__(self) -> str:
        return self.as_string()
